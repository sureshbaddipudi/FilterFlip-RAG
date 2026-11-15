# All eight copy comparisons

Every contrast is case-paired before aggregation. References and reproduction remain separate. B variants are controls, never P endpoints. Unknown primary per-answer fields remain missing. No missing or incomplete answer is imputed as a negative.

## Actual copy exposure

| Condition | Inserted budget | 0 retrieved | 1 retrieved | 2 retrieved | Retained copied documents (distribution) |
|---|---|---|---|---|---|
| BN1 | 1 | 2 | 57 | 0 | 0: 52; 1: 7 |
| BN2 | 2 | 1 | 3 | 55 | 0: 55; 1: 4 |
| PN1 | 1 | 18 | 41 | 0 | 0: 53; 1: 6 |
| PN2 | 2 | 18 | 2 | 39 | 0: 55; 1: 3; 2: 1 |
| BE1 | 1 | 0 | 59 | 0 | 0: 58; 1: 1 |
| BE2 | 2 | 0 | 0 | 59 | 0: 45; 1: 13; 2: 1 |
| PE1 | 1 | 20 | 39 | 0 | 0: 57; 1: 2 |
| PE2 | 2 | 20 | 2 | 37 | 0: 50; 1: 8; 2: 1 |

## Structural contrasts — all 59 cases

| Left→right | Same ordered input | Same survivors | Retrieved-document delta | Retained-document delta |
|---|---|---|---|---|
| BN1→BN2 | 1 | 8 | 0: 3; 1: 56 | -1: 5; 0: 52; 1: 2 |
| PN1→PN2 | 20 | 23 | 0: 20; 1: 39 | -1: 4; 0: 52; 1: 3 |
| BE1→BE2 | 0 | 5 | 1: 59 | -1: 1; 0: 44; 1: 13; 2: 1 |
| PE1→PE2 | 22 | 23 | 0: 22; 1: 37 | -1: 1; 0: 50; 1: 7; 2: 1 |
| BN1→BE1 | 0 | 49 | 0: 57; 1: 2 | -1: 7; 0: 51; 1: 1 |
| BN2→BE2 | 0 | 45 | 0: 55; 1: 3; 2: 1 | -1: 1; 0: 46; 1: 12 |
| PN1→PE1 | 18 | 48 | -1: 2; 0: 57 | -1: 4; 0: 55 |
| PN2→PE2 | 18 | 51 | -1: 2; -2: 1; 0: 56 | -1: 2; 0: 50; 1: 7 |

A delta is right minus left. Quote retention is a literal structural screen, not all-support-loss or answer correctness. Full structural and dataset tables are in expected/CONDITION_SUMMARIES.json and expected/COPY_PAIR_SUMMARIES.json.

## BN1 → BN2

### reference

| Field | Complete | Uncertain | Incomplete | Missing | N/A | Determinate transitions |
|---|---|---|---|---|---|---|
| background_qualified_endpoint | 0 | 0 | 0 | 0 | 59 | none |
| filtered_context_support | 0 | 0 | 0 | 59 | 0 | none |
| filtered_core_usable | 0 | 0 | 0 | 59 | 0 | none |
| filtered_full_complete | 0 | 0 | 0 | 59 | 0 | none |
| strict_endpoint | 0 | 0 | 0 | 0 | 59 | none |
| unfiltered_context_support | 0 | 0 | 0 | 59 | 0 | none |
| unfiltered_core_usable | 0 | 0 | 0 | 59 | 0 | none |
| unfiltered_full_complete | 0 | 0 | 0 | 59 | 0 | none |

### reproduction

| Field | Complete | Uncertain | Incomplete | Missing | N/A | Determinate transitions |
|---|---|---|---|---|---|---|
| background_qualified_endpoint | 0 | 0 | 0 | 0 | 59 | none |
| filtered_context_support | 35 | 0 | 0 | 24 | 0 | absent -> absent: 5; absent -> sufficient: 4; partial -> partial: 1; partial -> sufficient: 1; sufficient -> partial: 1; sufficient -> sufficient: 23 |
| filtered_core_usable | 30 | 5 | 0 | 24 | 0 | no -> no: 5; no -> yes: 3; yes -> yes: 22 |
| filtered_full_complete | 34 | 1 | 0 | 24 | 0 | no -> no: 15; no -> yes: 4; yes -> no: 1; yes -> yes: 14 |
| strict_endpoint | 0 | 0 | 0 | 0 | 59 | none |
| unfiltered_context_support | 35 | 0 | 0 | 24 | 0 | absent -> absent: 4; partial -> partial: 1; sufficient -> partial: 1; sufficient -> sufficient: 29 |
| unfiltered_core_usable | 31 | 4 | 0 | 24 | 0 | no -> no: 4; yes -> no: 1; yes -> yes: 26 |
| unfiltered_full_complete | 35 | 0 | 0 | 24 | 0 | no -> no: 14; yes -> no: 2; yes -> yes: 19 |

## PN1 → PN2

### reference

| Field | Complete | Uncertain | Incomplete | Missing | N/A | Determinate transitions |
|---|---|---|---|---|---|---|
| background_qualified_endpoint | 0 | 0 | 0 | 59 | 0 | none |
| filtered_context_support | 0 | 0 | 0 | 59 | 0 | none |
| filtered_core_usable | 0 | 0 | 0 | 59 | 0 | none |
| filtered_full_complete | 0 | 0 | 0 | 59 | 0 | none |
| strict_endpoint | 58 | 1 | 0 | 0 | 0 | met -> met: 3; met -> not_met: 5; not_met -> met: 1; not_met -> not_met: 49 |
| unfiltered_context_support | 0 | 0 | 0 | 59 | 0 | none |
| unfiltered_core_usable | 0 | 0 | 0 | 59 | 0 | none |
| unfiltered_full_complete | 0 | 0 | 0 | 59 | 0 | none |

### reproduction

| Field | Complete | Uncertain | Incomplete | Missing | N/A | Determinate transitions |
|---|---|---|---|---|---|---|
| background_qualified_endpoint | 33 | 1 | 1 | 24 | 0 | met -> met: 1; met -> not_met: 3; not_met -> not_met: 29 |
| filtered_context_support | 34 | 0 | 1 | 24 | 0 | absent -> absent: 14; absent -> partial: 2; absent -> sufficient: 5; partial -> partial: 3; sufficient -> partial: 2; sufficient -> sufficient: 8 |
| filtered_core_usable | 28 | 6 | 1 | 24 | 0 | no -> no: 13; no -> yes: 3; yes -> no: 1; yes -> yes: 11 |
| filtered_full_complete | 34 | 0 | 0 | 25 | 0 | no -> no: 24; no -> yes: 2; yes -> no: 1; yes -> yes: 7 |
| strict_endpoint | 33 | 1 | 1 | 24 | 0 | met -> met: 1; met -> not_met: 3; not_met -> not_met: 29 |
| unfiltered_context_support | 34 | 0 | 0 | 25 | 0 | absent -> absent: 4; sufficient -> sufficient: 30 |
| unfiltered_core_usable | 33 | 1 | 0 | 25 | 0 | no -> no: 5; yes -> no: 1; yes -> yes: 27 |
| unfiltered_full_complete | 34 | 0 | 0 | 25 | 0 | no -> no: 13; yes -> no: 2; yes -> yes: 19 |

## BE1 → BE2

### reference

| Field | Complete | Uncertain | Incomplete | Missing | N/A | Determinate transitions |
|---|---|---|---|---|---|---|
| background_qualified_endpoint | 0 | 0 | 0 | 0 | 59 | none |
| filtered_context_support | 59 | 0 | 0 | 0 | 0 | absent -> absent: 10; absent -> partial: 1; absent -> sufficient: 4; partial -> partial: 4; sufficient -> absent: 3; sufficient -> partial: 2; sufficient -> sufficient: 35 |
| filtered_core_usable | 53 | 6 | 0 | 0 | 0 | no -> no: 14; no -> yes: 4; yes -> no: 4; yes -> yes: 31 |
| filtered_full_complete | 58 | 1 | 0 | 0 | 0 | no -> no: 30; no -> yes: 3; yes -> no: 4; yes -> yes: 21 |
| strict_endpoint | 0 | 0 | 0 | 0 | 59 | none |
| unfiltered_context_support | 59 | 0 | 0 | 0 | 0 | absent -> absent: 9; partial -> partial: 5; sufficient -> partial: 2; sufficient -> sufficient: 43 |
| unfiltered_core_usable | 52 | 7 | 0 | 0 | 0 | no -> no: 12; no -> yes: 1; yes -> no: 1; yes -> yes: 38 |
| unfiltered_full_complete | 59 | 0 | 0 | 0 | 0 | no -> no: 29; no -> yes: 1; yes -> no: 2; yes -> yes: 27 |

### reproduction

| Field | Complete | Uncertain | Incomplete | Missing | N/A | Determinate transitions |
|---|---|---|---|---|---|---|
| background_qualified_endpoint | 0 | 0 | 0 | 0 | 59 | none |
| filtered_context_support | 59 | 0 | 0 | 0 | 0 | absent -> absent: 10; absent -> partial: 1; absent -> sufficient: 4; partial -> partial: 4; sufficient -> absent: 3; sufficient -> partial: 2; sufficient -> sufficient: 35 |
| filtered_core_usable | 51 | 8 | 0 | 0 | 0 | no -> no: 11; no -> yes: 6; yes -> no: 5; yes -> yes: 29 |
| filtered_full_complete | 58 | 1 | 0 | 0 | 0 | no -> no: 29; no -> yes: 4; yes -> no: 5; yes -> yes: 20 |
| strict_endpoint | 0 | 0 | 0 | 0 | 59 | none |
| unfiltered_context_support | 59 | 0 | 0 | 0 | 0 | absent -> absent: 9; partial -> partial: 5; sufficient -> partial: 2; sufficient -> sufficient: 43 |
| unfiltered_core_usable | 52 | 7 | 0 | 0 | 0 | no -> no: 11; no -> yes: 1; yes -> no: 5; yes -> yes: 35 |
| unfiltered_full_complete | 59 | 0 | 0 | 0 | 0 | no -> no: 29; no -> yes: 1; yes -> no: 4; yes -> yes: 25 |

## PE1 → PE2

### reference

| Field | Complete | Uncertain | Incomplete | Missing | N/A | Determinate transitions |
|---|---|---|---|---|---|---|
| background_qualified_endpoint | 56 | 3 | 0 | 0 | 0 | met -> met: 5; met -> not_met: 3; not_met -> not_met: 48 |
| filtered_context_support | 59 | 0 | 0 | 0 | 0 | absent -> absent: 27; absent -> partial: 2; absent -> sufficient: 5; partial -> absent: 1; partial -> partial: 8; partial -> sufficient: 2; sufficient -> absent: 3; sufficient -> partial: 2; sufficient -> sufficient: 9 |
| filtered_core_usable | 51 | 8 | 0 | 0 | 0 | no -> no: 28; no -> yes: 5; yes -> no: 4; yes -> yes: 14 |
| filtered_full_complete | 59 | 0 | 0 | 0 | 0 | no -> no: 43; no -> yes: 4; yes -> no: 4; yes -> yes: 8 |
| strict_endpoint | 57 | 2 | 0 | 0 | 0 | met -> met: 6; met -> not_met: 3; not_met -> met: 1; not_met -> not_met: 47 |
| unfiltered_context_support | 59 | 0 | 0 | 0 | 0 | absent -> absent: 9; partial -> partial: 4; sufficient -> sufficient: 46 |
| unfiltered_core_usable | 54 | 5 | 0 | 0 | 0 | no -> no: 12; no -> yes: 1; yes -> yes: 41 |
| unfiltered_full_complete | 59 | 0 | 0 | 0 | 0 | no -> no: 27; no -> yes: 1; yes -> no: 1; yes -> yes: 30 |

### reproduction

| Field | Complete | Uncertain | Incomplete | Missing | N/A | Determinate transitions |
|---|---|---|---|---|---|---|
| background_qualified_endpoint | 55 | 3 | 1 | 0 | 0 | met -> met: 4; met -> not_met: 3; not_met -> not_met: 48 |
| filtered_context_support | 58 | 0 | 1 | 0 | 0 | absent -> absent: 26; absent -> partial: 2; absent -> sufficient: 5; partial -> absent: 1; partial -> partial: 8; partial -> sufficient: 2; sufficient -> absent: 3; sufficient -> partial: 2; sufficient -> sufficient: 9 |
| filtered_core_usable | 49 | 9 | 1 | 0 | 0 | no -> no: 27; no -> yes: 5; yes -> no: 4; yes -> yes: 13 |
| filtered_full_complete | 58 | 0 | 1 | 0 | 0 | no -> no: 42; no -> yes: 5; yes -> no: 4; yes -> yes: 7 |
| strict_endpoint | 55 | 3 | 1 | 0 | 0 | met -> met: 5; met -> not_met: 3; not_met -> not_met: 47 |
| unfiltered_context_support | 59 | 0 | 0 | 0 | 0 | absent -> absent: 9; partial -> partial: 4; sufficient -> sufficient: 46 |
| unfiltered_core_usable | 53 | 6 | 0 | 0 | 0 | no -> no: 12; yes -> no: 1; yes -> yes: 40 |
| unfiltered_full_complete | 59 | 0 | 0 | 0 | 0 | no -> no: 27; no -> yes: 1; yes -> no: 1; yes -> yes: 30 |

## BN1 → BE1

### reference

| Field | Complete | Uncertain | Incomplete | Missing | N/A | Determinate transitions |
|---|---|---|---|---|---|---|
| background_qualified_endpoint | 0 | 0 | 0 | 0 | 59 | none |
| filtered_context_support | 0 | 0 | 0 | 59 | 0 | none |
| filtered_core_usable | 0 | 0 | 0 | 59 | 0 | none |
| filtered_full_complete | 0 | 0 | 0 | 59 | 0 | none |
| strict_endpoint | 0 | 0 | 0 | 0 | 59 | none |
| unfiltered_context_support | 0 | 0 | 0 | 59 | 0 | none |
| unfiltered_core_usable | 0 | 0 | 0 | 59 | 0 | none |
| unfiltered_full_complete | 0 | 0 | 0 | 59 | 0 | none |

### reproduction

| Field | Complete | Uncertain | Incomplete | Missing | N/A | Determinate transitions |
|---|---|---|---|---|---|---|
| background_qualified_endpoint | 0 | 0 | 0 | 0 | 59 | none |
| filtered_context_support | 35 | 0 | 0 | 24 | 0 | absent -> absent: 9; partial -> partial: 1; partial -> sufficient: 1; sufficient -> sufficient: 24 |
| filtered_core_usable | 31 | 4 | 0 | 24 | 0 | no -> no: 9; yes -> yes: 22 |
| filtered_full_complete | 35 | 0 | 0 | 24 | 0 | no -> no: 20; yes -> yes: 15 |
| strict_endpoint | 0 | 0 | 0 | 0 | 59 | none |
| unfiltered_context_support | 35 | 0 | 0 | 24 | 0 | absent -> absent: 4; partial -> partial: 1; sufficient -> sufficient: 30 |
| unfiltered_core_usable | 31 | 4 | 0 | 24 | 0 | no -> no: 4; yes -> no: 1; yes -> yes: 26 |
| unfiltered_full_complete | 35 | 0 | 0 | 24 | 0 | no -> no: 14; yes -> no: 3; yes -> yes: 18 |

## BN2 → BE2

### reference

| Field | Complete | Uncertain | Incomplete | Missing | N/A | Determinate transitions |
|---|---|---|---|---|---|---|
| background_qualified_endpoint | 0 | 0 | 0 | 0 | 59 | none |
| filtered_context_support | 59 | 0 | 0 | 0 | 0 | absent -> absent: 13; partial -> partial: 7; sufficient -> sufficient: 39 |
| filtered_core_usable | 53 | 6 | 0 | 0 | 0 | no -> no: 17; no -> yes: 1; yes -> no: 1; yes -> yes: 34 |
| filtered_full_complete | 58 | 1 | 0 | 0 | 0 | no -> no: 33; yes -> no: 1; yes -> yes: 24 |
| strict_endpoint | 0 | 0 | 0 | 0 | 59 | none |
| unfiltered_context_support | 59 | 0 | 0 | 0 | 0 | absent -> absent: 9; partial -> partial: 7; sufficient -> sufficient: 43 |
| unfiltered_core_usable | 53 | 6 | 0 | 0 | 0 | no -> no: 12; no -> yes: 2; yes -> no: 1; yes -> yes: 38 |
| unfiltered_full_complete | 59 | 0 | 0 | 0 | 0 | no -> no: 30; yes -> no: 1; yes -> yes: 28 |

### reproduction

| Field | Complete | Uncertain | Incomplete | Missing | N/A | Determinate transitions |
|---|---|---|---|---|---|---|
| background_qualified_endpoint | 0 | 0 | 0 | 0 | 59 | none |
| filtered_context_support | 59 | 0 | 0 | 0 | 0 | absent -> absent: 13; partial -> partial: 7; sufficient -> sufficient: 39 |
| filtered_core_usable | 51 | 8 | 0 | 0 | 0 | no -> no: 15; yes -> no: 1; yes -> yes: 35 |
| filtered_full_complete | 58 | 1 | 0 | 0 | 0 | no -> no: 33; yes -> no: 1; yes -> yes: 24 |
| strict_endpoint | 0 | 0 | 0 | 0 | 59 | none |
| unfiltered_context_support | 59 | 0 | 0 | 0 | 0 | absent -> absent: 9; partial -> partial: 7; sufficient -> sufficient: 43 |
| unfiltered_core_usable | 52 | 7 | 0 | 0 | 0 | no -> no: 13; yes -> no: 3; yes -> yes: 36 |
| unfiltered_full_complete | 59 | 0 | 0 | 0 | 0 | no -> no: 30; yes -> no: 3; yes -> yes: 26 |

## PN1 → PE1

### reference

| Field | Complete | Uncertain | Incomplete | Missing | N/A | Determinate transitions |
|---|---|---|---|---|---|---|
| background_qualified_endpoint | 0 | 0 | 0 | 59 | 0 | none |
| filtered_context_support | 0 | 0 | 0 | 59 | 0 | none |
| filtered_core_usable | 0 | 0 | 0 | 59 | 0 | none |
| filtered_full_complete | 0 | 0 | 0 | 59 | 0 | none |
| strict_endpoint | 58 | 1 | 0 | 0 | 0 | met -> met: 8; not_met -> met: 1; not_met -> not_met: 49 |
| unfiltered_context_support | 0 | 0 | 0 | 59 | 0 | none |
| unfiltered_core_usable | 0 | 0 | 0 | 59 | 0 | none |
| unfiltered_full_complete | 0 | 0 | 0 | 59 | 0 | none |

### reproduction

| Field | Complete | Uncertain | Incomplete | Missing | N/A | Determinate transitions |
|---|---|---|---|---|---|---|
| background_qualified_endpoint | 33 | 1 | 1 | 24 | 0 | met -> met: 4; not_met -> not_met: 29 |
| filtered_context_support | 34 | 0 | 1 | 24 | 0 | absent -> absent: 21; partial -> partial: 2; partial -> sufficient: 1; sufficient -> partial: 2; sufficient -> sufficient: 8 |
| filtered_core_usable | 30 | 4 | 1 | 24 | 0 | no -> no: 19; yes -> no: 1; yes -> yes: 10 |
| filtered_full_complete | 34 | 0 | 0 | 25 | 0 | no -> no: 26; yes -> no: 2; yes -> yes: 6 |
| strict_endpoint | 33 | 1 | 1 | 24 | 0 | met -> met: 4; not_met -> not_met: 29 |
| unfiltered_context_support | 34 | 0 | 0 | 25 | 0 | absent -> absent: 4; sufficient -> sufficient: 30 |
| unfiltered_core_usable | 33 | 1 | 0 | 25 | 0 | no -> no: 5; yes -> yes: 28 |
| unfiltered_full_complete | 34 | 0 | 0 | 25 | 0 | no -> no: 13; yes -> no: 1; yes -> yes: 20 |

## PN2 → PE2

### reference

| Field | Complete | Uncertain | Incomplete | Missing | N/A | Determinate transitions |
|---|---|---|---|---|---|---|
| background_qualified_endpoint | 57 | 2 | 0 | 0 | 0 | met -> met: 2; not_met -> met: 3; not_met -> not_met: 52 |
| filtered_context_support | 59 | 0 | 0 | 0 | 0 | absent -> absent: 29; partial -> partial: 12; partial -> sufficient: 1; sufficient -> absent: 2; sufficient -> sufficient: 15 |
| filtered_core_usable | 51 | 8 | 0 | 0 | 0 | no -> no: 30; yes -> no: 2; yes -> yes: 19 |
| filtered_full_complete | 59 | 0 | 0 | 0 | 0 | no -> no: 46; yes -> no: 1; yes -> yes: 12 |
| strict_endpoint | 58 | 1 | 0 | 0 | 0 | met -> met: 4; not_met -> met: 3; not_met -> not_met: 51 |
| unfiltered_context_support | 59 | 0 | 0 | 0 | 0 | absent -> absent: 8; partial -> partial: 4; sufficient -> absent: 1; sufficient -> sufficient: 46 |
| unfiltered_core_usable | 54 | 5 | 0 | 0 | 0 | no -> no: 12; no -> yes: 2; yes -> yes: 40 |
| unfiltered_full_complete | 59 | 0 | 0 | 0 | 0 | no -> no: 27; no -> yes: 3; yes -> no: 1; yes -> yes: 28 |

### reproduction

| Field | Complete | Uncertain | Incomplete | Missing | N/A | Determinate transitions |
|---|---|---|---|---|---|---|
| background_qualified_endpoint | 56 | 2 | 1 | 0 | 0 | met -> met: 2; not_met -> met: 2; not_met -> not_met: 52 |
| filtered_context_support | 58 | 0 | 1 | 0 | 0 | absent -> absent: 28; partial -> partial: 12; partial -> sufficient: 1; sufficient -> absent: 2; sufficient -> sufficient: 15 |
| filtered_core_usable | 50 | 8 | 1 | 0 | 0 | no -> no: 29; yes -> no: 2; yes -> yes: 19 |
| filtered_full_complete | 58 | 0 | 1 | 0 | 0 | no -> no: 45; yes -> no: 1; yes -> yes: 12 |
| strict_endpoint | 56 | 2 | 1 | 0 | 0 | met -> met: 3; not_met -> met: 2; not_met -> not_met: 51 |
| unfiltered_context_support | 59 | 0 | 0 | 0 | 0 | absent -> absent: 8; partial -> partial: 4; sufficient -> absent: 1; sufficient -> sufficient: 46 |
| unfiltered_core_usable | 54 | 5 | 0 | 0 | 0 | no -> no: 13; no -> yes: 1; yes -> yes: 40 |
| unfiltered_full_complete | 59 | 0 | 0 | 0 | 0 | no -> no: 27; no -> yes: 3; yes -> no: 1; yes -> yes: 28 |

The original PN1 endpoint uses accepted historical classification. No uniform primary reference per-answer labels are invented for BN1/PN1. New reproduction primary fields come only from exact linked Task 7 response reviews or its 35 endpoint records. Missing fields can therefore occur despite prior case-level acceptance. All transitions have record/file/field pointers in expected/COPY_PAIR_RECORDS.json. A conservative field-specific sensitivity is in expected/COPY_PAIR_SENSITIVITY.json.
