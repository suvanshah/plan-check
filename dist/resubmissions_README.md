# Refused → resubmitted conversions ("back and forth")

`data/resubmissions.csv` is built by `python3 scripts/resubmissions.py` (run from the repo root, takes about 40 s).
It has one row per refused house→flats application that was followed by another
conversion application at the same site. The follow-up had to be validated after
the refusal's decision date and within 4 years of it. Only applications in
`data/conversions.csv` count, so a follow-up appeal, householder application or
HMO application is not seen.

## Headline numbers

| | |
|---|---|
| Refused conversion applications (after collapsing 12 duplicate records) | 2,581 |
| Sites with at least one refusal | **2,095** |
| …followed by another conversion application within 4 years | **844 sites (40%)**, 1,020 refused→next pairs |
| …with no later conversion application at all | 1,246 sites (some went to appeal or a non-conversion application, or were refused too recently) |
| Next application approved | **473 pairs (46%)**. Refused again: 450 (44%). Withdrawn: 45. Pending or other: 52 |
| Approval rate of the next application, counting decided ones only | 51% |
| Resubmitted sites where *some* later conversion application was approved | **477 of 844 (57%)** |
| Median days from refusal to the next application | **90** (IQR 40–210). It is the same whether the next one is approved (86) or refused (87) |
| Refused again, then approved at a later attempt | 89 pairs |
| Sites with 2+ refused→next rounds | 141 (up to 5 rounds) |

The resubmission rate is flat at 39–46% for refusals decided 2019–2024. It drops to 34% in 2025 and 22% in 2026 only because there has not yet been time to resubmit (right-censoring).

## What changed: approved next vs refused again

Share of pairs carrying each tag, by the next application's decision. The "approval rate" column is approved ÷ (approved + refused) among pairs with that tag. The baseline is 51%.

| change_tag | refused→approved (n=473) | refused→refused (n=450) | approval rate when tag present |
|---|---|---|---|
| same_units | 74.4% | 77.1% | 50% |
| identical_description | 22.2% | 22.9% | 50% |
| fewer_units | 18.2% | 15.8% | **55%** |
| extension_added | 15.4% | 15.8% | 51% |
| refuse_cycle_added | 12.5% | 12.2% | 52% |
| extension_reduced | 12.1% | 9.6% | **57%** |
| amenity_added | 11.2% | 11.3% | 51% |
| parking_added | 7.8% | 7.6% | 52% |
| retrospective | 6.6% | 11.8% | **37%** |
| larger_units | 5.9% | 4.0% | **61%** (small n=46) |
| smaller_units | 5.7% | 4.7% | 56% |
| extension_removed | 5.1% | 4.7% | 53% |
| family_unit_added | 5.1% | 6.4% | 45% |
| more_units | 4.4% | 5.3% | 47% |

**Main finding: the descriptions barely predict the outcome.** Most resubmissions keep the same number of flats (76%) and the same headline description. The changes that can be seen in the descriptions shift the odds only a little:
- Cutting units or cutting back the extension helps a bit (55–57% vs 51%).
- Retrospective resubmissions do clearly worse (37%). These are usually "retain the flats we already built" applications.
- Adding a family unit does not help on its own (45%). The re-refusals are spread thinly across boroughs: Croydon refused 5 of its 7. A family flat may be needed to get approval, but it is not enough on its own.

What really changed is mostly in the drawings: room sizes, layouts, stacking, amenity split. The Datahub description does not capture these. The borough matters more than the tags. Ealing approved 103 of 143 decided next applications, while Croydon approved 37 of 110 and Brent 69 of 153.

### Units change (next − refused, n=996 with both known)

| change | −5 | −4 | −3 | −2 | −1 | 0 | +1 | +2 | +3 or more |
|---|---|---|---|---|---|---|---|---|---|
| pairs | 1 | 3 | 8 | 30 | 128 | 773 | 34 | 13 | 6 |

Dropping one flat is by far the most common change to the scheme. It leads to approval 59% of the time (70 approved vs 49 refused), against 50% when the unit count stays the same.

### "Identical" resubmissions

228 pairs (22%) have essentially the same description: the same numbers, and the text is ≥92% similar or ≥90% the same words. Despite that, **105 were approved and 103 refused**, the same 50/50 as everyone else. The median gap is only 60 days, so these are quick "fix the drawings and resubmit" applications. The approvals suggest the refused issue was in the plans or supporting documents (layout, space standards, parking survey, cycle store details) rather than the scheme as described. A few could also be a different officer or committee making a different call.

## Examples

1. **Harrow — cut from 5 flats to 3 and added a family flat → approved** (`Harrow-PL_2379_25` → `Harrow-PL_1463_26`, 187 days).
   - Refused: *"Conversion of the existing dwellinghouse into 5 self-contained apartments, erection of a two storey rear extension, part raising of the roof…"*
   - Approved: *"Conversion of dwelling into three flats (1 X 1 bed, 1 X 2 bed and 1 X 3 bed); two storey rear extension; alterations and enlargement of roof; … bin and cycle stores"*
   - Refusal reason: *"lack of private outdoor amenity spaces for the proposed Flats B, C, D and E, the adverse vertical stacking issues … would overlook the neighbouring property…"*
2. **Hillingdon — a 3-bed unit replaced a 2-bed unit to answer a "loss of family home" refusal → approved in 81 days** (`64134/APP/2025/994` → `64134/APP/2025/2388`).
   - Refused: *"…conversion of two storey dwelling into 2 x 2-bed self-contained flats…"*
   - Approved: *"…conversion of dwelling into 1 x 3-bed and 1 x 2 bed self-contained flats with associated parking, cycle and bin stores and amenity space"*
   - Refusal reason: *"would result in the loss of a residential unit that is suitable and appropriately sized for a family…"*
3. **Ealing — dropped the extra storey and a flat → approved** (`210185FUL` → `225356FUL`, 645 days).
   - Refused: *"Raising of ridge to create additional storey, part single, part three storey rear extension, flat roof dormer … conversion of existing house into 3 self-contained flats."*
   - Approved: *"Conversion of semi-detached dwellinghouse into two self-contained dwellings; installation of one rooflight to front elevation…"*
   - Refusal reason: *"by virtue of its siting, height, form … out of character and harmful to the established pattern of development…"*
4. **Islington — changed the bedroom mix (3-bed → 2-bed) and dropped the first-floor extension → approved in 39 days** (`P2019/3694/FUL` → `P2020/0621/FUL`).
   - Refused: *"…into 1x 4bedroom and 1x 3bedroom self-contained flats to include ground, first floor rear extensions, roof extension"*
   - Approved: *"…into 1x 4bedroom and 1x 2bedroom self-contained flats to include ground floor rear extension, roof extension"*
   - Refusal reason: *"undersized units and lack of private amenity space for family sized units … an inappropriate residential mix"*
5. **Enfield — word-for-word identical, appealed *and* resubmitted, then approved** (`25/02104/FUL` → `26/00522/FUL`, 172 days).
   - Both: *"Conversion of single family dwellinghouse into 2x flats and erection of rear terrace."*
   - Refusal reason: *"would result in the loss of a 3-bedroom family dwelling and fails to provide adequate compensatory family accommodation…"* Whatever changed (probably the floor plans or the evidence about the house) is not in the description.
6. **Hillingdon — identical description, approved 13 days later** (`32474/APP/2021/4374` → `32474/APP/2022/332`). The refusal was *"failed to demonstrate that adequate and functional parking space could be provided"*. This is a missing-information refusal, fixed with a parking plan.

## How sites are matched

Applications are joined into sites using union-find within a borough. The `match_method` of a pair is the strongest key the two applications share:

| method | rule | pairs |
|---|---|---|
| `uprn` | same UPRN (leading zeros stripped, junk such as `MAN000…` dropped) | 963 |
| `site_ref` | Hillingdon only: its LPA numbers start with a property reference (`64134/APP/…`), and it has no UPRNs | 26 |
| `latlon` | ≤15 m apart, only for applications with no UPRN, and not if both have different house numbers | 14 |
| `postcode_number` | same postcode and house number | 14 |
| `address` | same normalised site_number and street (rd→road, st→street, gdns→gardens…) | 3 |

Two guards stop wrong links:
- An address or postcode link is refused if it would merge two different UPRNs. The exception is when the postcode also matches, which usually means a re-issued UPRN.
- An address link is refused if the two postcodes differ. Havering stores the town ("Romford") in `street_name`.

Duplicates are collapsed before pairing, keeping the refused or approved record. A duplicate is the same site + description + valid date (FUL/LBC twins, Ealing double submissions), or the same LPA root (Tower Hamlets `_A1`/`_R`/`_NC`).

**Spot-check:** 30 pairs were read by hand (18 uprn, 12 others: latlon, site_ref, postcode_number). **All 30 are the same property**, judged by matching address, postcode and coordinates and recognisably the same scheme. An automated check of all pairs also passed:
- Of the 736 pairs where both have a street, the street differs in only 5. All 5 are Hillingdon records where one side stores the town.
- 1 of 624 has a different house number (2 vs 2A Dale Avenue, same UPRN).
- 1 uprn pair is 1.4 km apart (Ealing/OPDC). The UPRN and street match, so the geocode is wrong.

## Weaknesses

- **Change tags come from descriptions only**, using regex word and phrase diffs, so they miss changes that are only in the drawings. Unit counts come from `proposed_units_text`, which is parsed and is occasionally off. For example, one Bromley pair "3 one bedroom and 1 two bedroom" is read as fewer units than it is. The bedroom mix (`smaller_units`/`larger_units`) is only tagged when both descriptions spell out a mix. `extension_reduced` and `extension_added` compare sets of extension elements (two-storey, dormer, mansard, hip-to-gable, roof, basement…), not sizes. `family_unit_added` ignores "single family dwelling" (the house being converted), but can still fire on wording such as "family unit at ground floor" that was implicit in the refused scheme.
- **Only conversion→conversion pairs.** An appeal allowed after a refusal is not a "next application". 136 pairs have a refused application that was appealed, and 442 refused applications have some appeal record. Resubmissions to the same site as a householder or HMO application are invisible.
- **Window edges.** The 2019 refusals may themselves be resubmissions of pre-2019 refusals. Refusals from 2025–26 have had less time to be resubmitted.
- **Sites without keys.** 125 applications have no UPRN, no coordinates and no usable address, so they cannot be matched. The 15 m latlon fallback could join neighbouring houses: it is used for only 14 pairs and is guarded by house number, but one Hillingdon pair (P0805) links two property references 101 and 99 Belmont Road, where the refused scheme spanned both.
- **`refused_reasons_text`** is short or empty ("Refused", "xxxx") for 483 of the 1,020 pairs. Most of these are Brent (165) and Ealing (116), which don't publish reasons in the Datahub.
- `eventually_approved` means any later conversion application at the site was approved, with no time limit. It does not check that the approved scheme is the same one.
