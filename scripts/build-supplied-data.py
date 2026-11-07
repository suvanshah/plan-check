"""Prepare the supplied release without merging it with Foundations.

Usage: python3 scripts/build-supplied-data.py /path/to/data
Original files remain unchanged. Parsed fields are never marked verified.
"""
from pathlib import Path
import csv, hashlib, json, math, re, sys

root = Path(sys.argv[1])
dest = Path(__file__).resolve().parents[1] / 'dist'
def read(name):
    with (root / name).open(newline='') as f:
        return list(csv.DictReader(f))
def number(value):
    try:
        n = float(value)
        return n if math.isfinite(n) else None
    except (ValueError, TypeError):
        return None
def boolean(value):
    return {'True': True, 'False': False}.get(value)
def borough(value):
    return {'Kensington and Chelsea': 'Kensington', 'Kingston upon Thames': 'Kingston',
            'Richmond upon Thames': 'Richmond', 'City of London': 'City',
            'OPDC': 'Old Oak Park Royal'}.get(value, value)

conversions = read('conversions.csv')
ids = {r['id'] for r in conversions}
assert len(ids) == len(conversions) == 6396
reasons = read('refusal_reasons.csv')
sizes = {r['id']: r for r in read('size_features.csv')}
texts = {r['id']: r['decision_text'] for r in read('decision_text.csv')}
pairs = read('resubmissions.csv')
reason_map = {}
for r in reasons:
    assert r['id'] in ids
    reason_map.setdefault(r['id'], []).append({'category': r['category'], 'evidence': r['evidence']})
files = ['conversions.csv', 'decision_text.csv', 'size_features.csv',
         'refusal_reasons.csv', 'refusal_categories.json', 'resubmissions.csv',
         'refusal_reasons_README.md', 'resubmissions_README.md']
manifest = [{'file': n, 'bytes': (root/n).stat().st_size,
             'sha256': hashlib.sha256((root/n).read_bytes()).hexdigest()} for n in files]
status = {'approved': 'Permitted', 'refused': 'Rejected', 'withdrawn': 'Withdrawn',
          'pending/unknown': 'Undecided', 'other': 'Other'}
rows = []
for c in conversions:
    z = sizes[c['id']]
    size = {k: number(z[k]) for k in ['flats_listed', 'flats_with_size', 'min_flat_m2',
        'median_flat_m2', 'total_flats_m2', 'flats_below_standard', 'worst_shortfall_m2',
        'house_area_m2', 'flats', 'area_per_flat_m2']}
    size.update(sizes_complete=boolean(z['sizes_complete']), any_below_standard=boolean(z['any_below_standard']))
    rows.append(dict(id=c['id'], ref=c['lpa_app_no'], borough=borough(c['borough']),
        description=c['description'], type=c['application_type'], status=status[c['decision']],
        decision=c['decision_raw'], sourceDecision=c['decision'], date=c['valid_date'],
        decided=c['decision_date'], days=number(c['days_to_decision']), lat=number(c['lat']),
        lng=number(c['lon']), url=c['url'], screen='House wording' if re.search(r'house|dwelling', c['description'], re.I) else 'Conversion screen',
        flags=['Text-screened; not plan-verified'], verified=False, storeys=None, heritage=None,
        existingHomes=None, proposedHomes=None, reviewedReason=None,
        reportedStoreys=number(c['storeys']), reportedDwellings=number(c['proposed_units_text']),
        existingUnitsField=number(c['existing_units_field']), proposedUnitsField=number(c['proposed_units_field']),
        reasons=reason_map.get(c['id'], []), size=size))
row_map = {r['id']:r for r in rows}
pair_rows = []
for p in pairs:
    assert p['refused_id'] in ids and p['next_id'] in ids
    assert row_map[p['refused_id']]['status'] == 'Rejected'
    # P0826 has a known count/description contradiction; retain it but flag it.
    warnings = ['Parsed next-unit count conflicts with a description listing two flats.'] if p['pair_id']=='P0826' else []
    pair_rows.append(dict(id=p['pair_id'], borough=borough(p['borough']),
        site=hashlib.sha256(p['site_key'].encode()).hexdigest()[:20], method=p['match_method'],
        refusedId=p['refused_id'], nextId=p['next_id'], days=number(p['days_between']),
        refusedUnits=number(p['refused_units']), nextUnits=number(p['next_units']),
        unitChange=number(p['units_change']), tags=p['change_tags'].split('|') if '|' in p['change_tags'] else p['change_tags'].split(';'),
        nextDecision=p['next_decision'], eventuallyApproved=boolean(p['eventually_approved']),
        reasonText=p['refused_reasons_text'], warnings=warnings))
meta = dict(release='supplied', title='Supplied conversion extract', prepared='2026-11-07',
    source='User-supplied Datahub-derived files', source_rows=66880, candidate_rows=6396,
    min_date=min(r['date'] for r in rows if r['date']), max_date=max(r['date'] for r in rows if r['date']),
    snapshot='Supplied 7 November 2026; query/extraction timestamp not provided',
    verified_records=0, manifest=manifest, decision_mapping=status,
    raw_not_deployed='66,880 raw candidates and 1,173 deconversions are audited but not loaded into the app.')
payload = dict(meta=meta, rows=rows, pairs=pair_rows,
               categories=json.loads((root/'refusal_categories.json').read_text()))
(dest/'conversions-data.json').write_text(json.dumps(payload, separators=(',', ':')))
for name in ['refusal_reasons_README.md', 'resubmissions_README.md']:
    (dest/name).write_bytes((root/name).read_bytes())
print(json.dumps({'rows':len(rows), 'pairs':len(pair_rows), 'reason_applications':len(reason_map),
                  'bytes':(dest/'conversions-data.json').stat().st_size}))
