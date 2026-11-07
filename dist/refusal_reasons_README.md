# Why house→flats conversions get refused: refusal-reason categories

Files: `scripts/classify_refusals.py` writes `data/refusal_reasons.csv` (long format: `id,borough,year,category,evidence`) and `data/refusal_categories.json` (keys, labels and descriptions in display order). To regenerate, run `python3 scripts/classify_refusals.py` from the repo root.

## Method (rules only, no LLM)
1. Join refused applications (`decision == refused`) to `decision_text.csv` on `id`. Unescape the HTML (much of it is double-escaped), strip the tags and split on ` || `.
2. **Drop boilerplate segments and sentences**: conditions ("hereby permitted", "shall be…", "in accordance with plans…"), informatives, CIL/appeal notes, "positive and proactive"/NPPF para 38 statements, Hillingdon's "On this decision notice policies…" preamble, Croydon's pre-app tags ("PR - No Pre App"), validation letters ("please provide…") and pasted officer-report text.
3. **Cut policy citations.** Each sentence is truncated at "contrary to / in conflict with / fails to comply with / Policy X…", and bracketed policy titles are removed. Policy *names* like "D1 (Design)" or "…Conservation Area Design Guidelines" therefore never trigger a category. Tags shorter than 40 characters are kept whole, so that Sutton's "Policy 10" survives.
4. **Keyword and regex rules per category**, plus a few disambiguation rules:
   - Family-size words ("family-sized", "3-bed") only count with a loss/need/provision context nearby. "The proposed family-sized unit…" and "space standard for a 3-bed unit" do not count.
   - Privacy, outlook, light and noise go to `neighbour_impact` when a neighbour word is present ("neighbouring", "adjoining", "No. 42 X Road", "AOs"). They go to `living_standards` when the problem is the future occupiers'.
   - "Cycle parking" is not car parking. Ceiling height is not design. "Original dwelling under 120 m²" is the family-home rule, not space standards.
   - A generic "unacceptable in principle" is dropped when the same refusal already has `loss_family_home`.
   - Sutton's short "Principle" tags are mapped to `loss_family_home`, because Sutton's in-principle refusals are Local Plan Policy 10 (houses under 125 m²).
5. The evidence for each category is the first matching sentence, trimmed to 200 characters or fewer. An application with usable text but no match gets one `other` row.

Three keys were added beyond the brief because the data clearly needs them:
- `conversion_principle`: clustering or over-concentration of conversions (Enfield), the "10% of a street" rule (Hillingdon), Barnet's "Principle"/HOU03 tags for roads of houses.
- `fire_safety`: London Plan D12 fire statements. This is mostly Croydon from 2021.
- `environment`: flood/SuDS, energy/carbon, water, air quality, trees, ecology and BNG.

## Coverage
| | count |
|---|---|
| Refused conversions | 2,584 |
| …with any `decision_text` | 1,556 (60%) |
| …with **usable** reason text (after boilerplate removal) | **1,283 (50% of refusals)** |
| …with ≥1 real category (not `other`) | **1,277** (99.5% of usable) |
| Rows in `refusal_reasons.csv` | 4,175 (≈3.3 categories per refusal) |

Of the 1,556 with text, 273 are boilerplate only: Redbridge "in accordance with plans" lists (all 101 of its refusals), Hounslow "Condition : 1 - .", Ealing "xxxx" and Bexley "Policies". The following boroughs have **no** usable refusal text at all: Brent (353 refusals), Newham, Haringey, Greenwich, Lewisham, Tower Hamlets and Redbridge. Waltham Forest and Lambeth have almost none. Ealing has only 74 of its 264.

## Top categories (share of the 1,277 classified refusals)
| category | refusals | % |
|---|---|---|
| living_standards | 868 | 68.0% |
| design_character | 620 | 48.6% |
| parking_highways | 483 | 37.8% |
| loss_family_home | 413 | 32.3% |
| amenity_space | 366 | 28.7% |
| neighbour_impact | 291 | 22.8% |
| refuse_cycle | 284 | 22.2% |
| environment | 222 | 17.4% |
| overdevelopment | 158 | 12.4% |
| insufficient_info | 148 | 11.6% |
| legal_agreement | 137 | 10.7% |
| conversion_principle | 94 | 7.4% |
| fire_safety | 51 | 4.0% |
| heritage_conservation | 34 | 2.7% |

Percentages add to more than 100% because most refusals cite several reasons.

## Borough differences (boroughs with ≥20 classified refusals; % of that borough's classified refusals)
| borough | classified | loss_family_home | living_standards | parking | other notable |
|---|---|---|---|---|---|
| Sutton | 37 | **84%** | 51% | 59% | environment 59% |
| Barking & Dagenham | 59 | **76%** | 61% | 22% | |
| Wandsworth | 27 | **63%** | 67% | 0% | amenity 52% (15 m² garden for the family unit) |
| Hillingdon | 94 | 45% | 68% | 45% | |
| Enfield | 220 | 43% | 68% | 29% | conversion_principle 12% (clustering) |
| Havering | 61 | 36% | **90%** | 54% | amenity 66% |
| Merton | 84 | 30% | 77% | 64% | **legal_agreement 42%** (permit-free s106), environment 51% |
| Croydon | 192 | 28% | 66% | 56% | **fire_safety 19%** |
| Harrow | 154 | 14% | 76% | 27% | design 68% |
| Barnet | 123 | 13% | 50% | 32% | **conversion_principle 36%** ("roads of houses" principle) |
| Ealing | 74 | 3% | 77% | 4% | |

Takeaways:
- **Family-home protection is very borough-specific.** Sutton, Barking & Dagenham, Wandsworth, Hillingdon and Enfield make it a headline reason. Harrow, Barnet and Ealing almost never do: Barnet uses an in-principle "street of houses" objection instead, and Harrow and Ealing focus on accommodation quality and design.
- **Poor living standards is the near-universal reason** (two-thirds of refusals). It is usually space standards, bedroom sizes, headroom, outlook/light and stacking.
- Merton's refusals are long checklists: s106 permit-free, carbon/water, air quality, BNG, FRA and refuse. That inflates its legal_agreement and environment shares.
- Fire safety appears from 2021, after London Plan D12, and mostly through Croydon's tags.

## Validation and accuracy
I made six review passes of 30 randomly sampled refusals each (about 180 applications, from different random seeds). For each I printed the cleaned reason sentences next to the assigned categories, read them and fixed the rules.

In the last two passes about **90% of applications had exactly the right category set** (27/30 and 27/30). Nearly every remaining error was one extra or missing minor label, not a wrong headline reason. At the level of individual (application, category) labels, precision is about 95%.

## Known weaknesses
- **Coverage bias.** Only half of refusals have usable text, and whole boroughs are missing (Brent being the largest). Borough comparisons cover only the boroughs with text, and London-wide shares are really "shares among the ~20 boroughs that publish reasons".
- **Text formats differ by borough.** Croydon, Enfield, Barnet, Bexley and Sutton publish short tags ("QOA", "Character", "Principle"), while others publish full reasons. Tags are vaguer. For example, a bare "Amenity" is mapped to `neighbour_impact`, and Barnet's "Principle" and Sutton's "Principle"/"Policy 10" needed borough-specific interpretation.
- Some boundaries are fuzzy:
  - `design_character` versus `overdevelopment`: "cramped form of development" counts as overdevelopment.
  - `living_standards` versus `amenity_space`: lack of a garden often gives both.
  - `living_standards` versus `neighbour_impact`: noise from stacking within the same building counts as living standards.
- `parking_highways` and `legal_agreement` often co-occur by design. A "permit-free s106" refusal gets both.
- `insufficient_info` overlaps with environment and parking, e.g. "absence of a Flood Risk Assessment" or "absence of a parking survey".
- Officer-report or validation-letter text pasted into the conditions field (a few Kingston and Merton records) is only partly filtered out.
- Regexes cannot read negation well. A rare "would not result in overlooking" in a reason can still trigger a label.
