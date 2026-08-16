# v0.3 spec: reference-number and identifier realism

Scope: the formats, check-digit algorithms, generators and validators for every
identifier FreightBench renders or could render. Nothing here touches email
prose style or pathology content; those are owned elsewhere. This spec answers
three questions: what the real formats are (with sources), whether the schema
should grow from two reference fields to five, and whether a malformed-reference
pathology is worth a slot.

All citations point into `research/freight-document-research.md` (cited below as
"research §N" by section number, or "Gap §N" for the gap-analysis subsections).
Where the research does not pin a format down, this spec says so instead of
guessing. A wrong format in ground truth is worse than an admitted gap.

---

## 0. Decisions, up front

| Question | Recommendation |
|---|---|
| Five reference fields or two? | **Stay with two.** Render the extra references as typed distractor strings in document text, mapped to no schema field. Rationale in §3. |
| Malformed-reference pathology? | **Against.** It tests arithmetic, not extraction, and the truth value would be the verbatim malformed string, which every extractor copies anyway. Rationale in §4. |
| Replace `BK-#####` / `PO######`? | **Yes.** Heterogeneous house-format families (§2.4, §2.5). This is the actual v0.3 change. |
| AWB / container / B/L numbers | Specced with full algorithms (§2.1 to §2.3) for use as distractor texture in v0.3 and as groundwork for the HAWB document type later. They are not schema fields. |
| HS codes | No change. `hs_code` truth stays null (never rendered); upgrading the 4-digit headings would require verified subheadings the research does not contain (§2.6). |
| UN numbers | No format change. Registry-membership validation, not arithmetic (§2.7). |
| Scorer | One recommended amendment: the `code` comparison rule should ignore spaces and hyphens (§5.4). |

---

## 1. Source discipline

What the research pins down, and what it does not. Everything in §2 traces back
to this table.

| Claim | Status | Source |
|---|---|---|
| AWB = 3-digit prefix + 7-digit serial + check digit, check = serial mod 7, unweighted | **Pinned, cross-confirmed** | research §5: Australian Border Force / freight.domains / airwaybilltracker block; Freightos worked example 999-5372907-1 (§3); AltexSoft (§5); Cargo-IMP FWB sample `777-12345675` (§11) |
| Trailing AWB digit of 7, 8 or 9 is impossible | **Pinned** (follows from mod 7) | research §5, stated explicitly |
| 999 is a neutral AWB prefix; real prefixes name real airlines (020 = Lufthansa Cargo, 125/075 = IAG carriers) | **Pinned** | research §3 (Freightos, IAG), §5 (ABF block) |
| Container number shape: 4 letters ending in U + 6 digits + 1 check digit | **Pinned** (shape only) | Gap §2 and research §6 (exportnesthub: "MSCU 123456 7") |
| ISO 6346 check-digit *algorithm* (letter values, weights, mod 11) | **NOT in the research.** Reproduced in §2.2 from the published ISO 6346 standard as general knowledge, self-checked against the standard's canonical example. Flagged for independent verification before any ground truth depends on it. | none in file |
| B/L numbers: no universal format, carrier-specific patterns, house B/L must carry a SCAC, US manifest cap 16 chars (4-char SCAC + up to 12) | **Pinned** | research §6 (vizionapi) |
| Booking confirmation reference exemplar `BHK51332862` | **Pinned, with a wrinkle**: the quoted string is 3 letters + 8 digits; the research's own gloss says "2 letters + 8 digits". The verbatim string wins over the summary gloss. | research §3 (freightcourse) |
| Carrier-prefixed booking-number strings "MAEU123456789", "MSCU2024987654" | **Poisoned. Do not use.** The research explicitly flags these as likely fetch-tool fabrication. | research §3 (DocShipper entry) and access-limitations preamble |
| A real booking carries up to five reference numbers (Invoice Ref., BKG SH Ref., BKG FF Ref., S/I SH Ref., S/I FF No.) | **Pinned** | research §1 (ONE booking guide), summary table row 1 |
| Air-cargo message character set: capital A-Z, digits, `.` `-` and space only | **Pinned** | research §5 (DAKOSY FWB spec) |
| Shipper / forwarder internal house-reference formats | **Unpinned by nature.** Internal references have no standard to violate. | absence, plus vizionapi's "no universal numeric format exists" for the adjacent B/L case |
| PO / customer-reference formats | **Unpinned.** Existence confirmed (UK gov invoice checklist "proforma/PO/contract number", research §7); no format given anywhere. | research §7 |
| HS codes: real commercial documents use 6 to 10 digits; repo data is 4-digit headings | **Pinned as a gap** | Gap §8 (19 CFR 142.6 via Cornell LII, EU Access2Markets) |
| UN numbers UN3480 / UN3481 / UN3090 / UN3091 | **Pinned** | research §9 (49 CFR 173.185 via Cornell LII) |
| UN1263, UN1950 (already in `reference.py`) | **Not pinned by the research pass.** Consistent with general knowledge; flagged, not re-verified. | none in file |

Two internal tensions in the research, noted so nobody trips on them later:

1. vizionapi's "SCAC + 13 chars (Hapag-Lloyd-style)" conflicts with its own
   "16-character cap (4-char SCAC + up to 12 more)": 4 + 13 = 17. The 16-char
   cap is the one grounded in a named regulatory rule, so this spec treats
   **16 total** as binding and generates SCAC + 8 to 12 characters.
2. The Cargo-IMP sample is glossed as "3-digit prefix + 8-digit serial". The
   8-digit block is the 7-digit serial with the check digit concatenated
   (1234567 mod 7 = 5, hence `12345675`). Same number, different slicing. This
   spec always says 3 + 7 + 1.

---

## 2. Identifier catalogue

### 2.1 AWB numbers (air waybill)

**Format.** 11 digits: 3-digit IATA airline prefix, 7-digit serial, 1 check
digit. Check digit = the 7-digit serial modulo 7, unweighted (research §5,
cross-confirmed three ways; worked example 999-5372907-1 in research §3).
Because the modulus is 7, a trailing digit of 7, 8 or 9 is arithmetically
impossible (research §5).

**Algorithm, exactly:**

```
serial: integer 0..9999999 (render zero-padded to 7 digits)
check  = serial mod 7          # an integer 0..6
```

Worked examples, both from the research and re-verified by hand:

| serial | serial mod 7 | full number | source |
|---|---|---|---|
| 5372907 | 1 | 999-5372907-1 | Freightos worked example, research §3 |
| 1234567 | 5 | 777-12345675 | Cargo-IMP FWB sample, research §11 |
| 9999999 | 2 | (edge) | arithmetic |
| 0 | 0 | (edge) | arithmetic |

**Surface forms.** Two cited renderings: `###-########` (prefix, hyphen, then
serial+check concatenated; matches the SLI box-13 mask in research §4 and the
Cargo-IMP sample) and the fully hyphenated `XXX-XXXXXXX-X` (ABF block, research
§5). Default to the first; the validator accepts both plus the bare 11-digit
run (Freightos renders `99953729071` unhyphenated, research §3).

**Prefix policy.** Real prefixes identify real airlines (020 = Lufthansa Cargo,
research §5; 125/075 = IAG carriers, research §3), and the repo's data policy is
that no real company appears in the corpus. The one prefix the research
certifies as neutral is **999** (Freightos, research §3). v0.3 uses 999
exclusively. Cost: a uniform prefix is a corpus tell. Accepted, because AWBs in
v0.3 are distractor texture only, and inventing "unused" prefixes cannot be
verified against the IATA registry from the research at hand.

**Where AWBs may appear.** Not as ground truth for any schema field. Legitimate
placements (prose owners decide the wording): a prior shipment referenced in a
thread ("last consignment moved under 999-53729071"), or a forwarding agent's
pre-assigned AWB in an air `agent_not_shipper` variant. If a document ever makes
an AWB the sender's own booking reference (defensible for a forwarder-sender
holding AWB stock), the truth is the verbatim surface string, nothing else.

### 2.2 ISO 6346 container numbers

**Shape (pinned).** 4 letters, ending in U in every example the research
captured, + 6 serial digits + 1 check digit. Example shape `MSCU 123456 7`
rendered with or without spaces (research §6, Gap §2). The research describes
the 4 letters as a 3-letter owner code + 1-letter equipment category
(exportnesthub, research §6); whether the category letter is always U is not
pinned. The generator uses U.

**Check-digit algorithm (NOT in the research; provenance flagged).** The
following is the published ISO 6346 algorithm, reproduced from general
knowledge of the standard. It is self-consistent with the standard's own
canonical example (below), but before container-number ground truth ever enters
the corpus, verify this against an independent implementation or the BIC's
online calculator. Until then, container numbers are distractor texture only,
which is all v0.3 needs.

```
Step 1: map each of the 4 letters to a value from this table
        (values 10..38, skipping 11, 22 and 33):

        A=10 B=12 C=13 D=14 E=15 F=16 G=17 H=18 I=19 J=20
        K=21 L=23 M=24 N=25 O=26 P=27 Q=28 R=29 S=30 T=31
        U=32 V=34 W=35 X=36 Y=37 Z=38

Step 2: the 6 serial digits map to themselves.

Step 3: weight the 10 values left to right by 2^position:
        position 0 (first letter) has weight 1, position 1 weight 2,
        ... position 9 (last serial digit) weight 512.

Step 4: total = sum of value * weight over all 10 positions.

Step 5: check digit = (total mod 11) mod 10.
        The final "mod 10" folds the awkward remainder 10 into 0.
```

Worked examples (all hand-verified for this spec):

| stem (4 letters + 6 digits) | total | total mod 11 | check | note |
|---|---|---|---|---|
| CSQU305438 | 6185 | 3 | 3 | canonical example from the ISO 6346 standard itself; the anchor any independent verification must reproduce |
| MSCU123456 | 5528 | 6 | 6 | **the research's illustrative "MSCU 123456 7" is therefore invalid**; it is a placeholder, not a real number. Copied examples are not ground truth; the algorithm is |
| KGFU123456 | 5511 | 0 | 0 | fictional owner code, computed |
| HCYU998877 | 7792 | 4 | 4 | fictional owner code, computed |
| KSGU000000 | 405 | 9 | 9 | computed |
| KSGU900000 | 549 | 10 | 0 | the remainder-10 corner; the generator refuses these serials (below) so no emitted number depends on the mod-10 fold |

One worked total, fully expanded, so the algorithm is implementable from this
page alone. CSQU305438: letters C=13, S=30, Q=28, U=32; weights 1, 2, 4, 8
give 13 + 60 + 112 + 256 = 441. Digits 3,0,5,4,3,8 with weights
16,32,64,128,256,512 give 48 + 0 + 320 + 512 + 768 + 4096 = 5744. Total 6185.
6185 = 11 x 562 + 3. Check digit 3.

**Remainder-10 policy.** The generator re-draws any serial whose raw
remainder is 10 (about 1 draw in 11; the re-draw loop pulls from the same
seeded rng, so determinism holds). This means every emitted number validates
under both the strict-remainder reading and the mod-10 fold, sidestepping the
one corner of the algorithm the research cannot confirm.

**Owner codes.** Fictional, echoing the repo's fictional forwarders (KGFU,
HCYU, PFLU). Not checked against the BIC register; collision with a real code
is possible and is the same accepted risk as the fictional company names.

**Where container numbers may appear.** Not at booking-request time in the
normal flow (containers are assigned later), which the research supports
indirectly: they live in SI, VGM and confirmation documents (research §4, §10).
Legitimate v0.3 placements: shipper-owned-container mentions (S.O.C. is a real
booking-form field, ONE guide, research §1) and forwarded-thread texture
referencing an earlier shipment.

### 2.3 Ocean B/L numbers (SCAC-prefixed)

**Format.** There is no universal format and no check digit (research §6,
vizionapi: "no universal numeric format exists"). Pinned constraints: a house
B/L must carry the issuer's SCAC as part of the number; US customs manifest
rules cap the identifier at 16 characters, read as 4-char SCAC + up to 12 more
(research §6; see §1 note on the internal 13-vs-12 tension, resolved to the
16 cap). Pattern families cited by vizionapi: pure 9-12 digit numeric, 3
letters + 7-9 digits, and 4-letter SCAC + digits (`HLCU...` style).

**Generator rule.** Fictional SCAC (same fictional 4-letter pool as §2.2,
which mirrors the research's own examples where MSCU-shaped codes appear in
both roles; the research never asserts the two registries are the same thing) +
9 digits, giving 13 characters, under the 16 cap. Validation is shape-only:
`^[A-Z]{4}\d{8,12}$` and length <= 16. No checksum exists to enforce.

**Poisoned strings.** Never emit `MAEU...` or `MSCU2024...` style strings from
the DocShipper entry; the research flags them as probable fetch-tool
fabrication (research §3).

**Where B/L numbers may appear.** Not in a booking request in the normal flow
(the B/L does not exist yet). Thread texture only ("released under
HCYU123456789 last time").

### 2.4 Sender booking references (replaces `BK-#####`)

This is the schema-facing change. `booking_reference` is "Sender's own booking
or quote reference" (`schema.py`), i.e. a shipper's or forwarder's house
reference. **No source pins a format for these, and none can: they are
internal.** The design goal is therefore heterogeneity without false
precision, anchored to the one real-shaped exemplar the research captured:
`BHK51332862`, 3 letters + 8 digits, no hyphen (freightcourse booking
confirmation, research §3; the research's own "2 letters" gloss contradicts its
quoted string, and the string wins).

Why heterogeneity is the realism payload here: today `naive.py` extracts
`booking_reference` with the literal regex `\bBK-\d{5}\b`, which works only
because the fictional format is uniform. Real references force extractors to
anchor on labels and position rather than on a memorized shape. Killing the
uniform format is a genuine difficulty improvement that costs zero new fields.

**Format families** (drawn per document; optionally stable per sender company
by indexing the family with the company's position in `COMPANIES`, which is
deterministic and free):

| family | shape | example | anchor |
|---|---|---|---|
| 1 | 3 letters + 8 digits | `QHT51332862` | the freightcourse exemplar shape (research §3) |
| 2 | 2 letters + hyphen + 6 digits | `KV-204815` | invented; house refs have no standard to violate |
| 3 | `BKG` + 6 digits | `BKG481205` | invented; echoes "BKG SH Ref." labelling on ONE's form (research §1) |
| 4 | pure numeric, 7 to 9 digits | `50448121` | mirrors vizionapi's pure-numeric carrier style (research §6) |

Constraint: pure-numeric references are always >= 7 digits so they can never
collide with a rendered weight (max 5 digits), piece count, or volume. All
families stay within the DAKOSY character set (A-Z, digits, `.` `-` space,
research §5).

Letters are drawn uniformly from A-Z with the seeded rng. Truth is the exact
surface string as rendered (see §5.2).

### 2.5 Customer references (replaces always-`PO######`)

Existence of PO/contract references on commercial paperwork is pinned (UK gov
export-invoice checklist, research §7); format is not. Keep PO-prefixed
families only, so the string stays self-labelling wherever it lands in prose:

| family | shape | example |
|---|---|---|
| 1 | `PO` + 6 digits (current format, kept) | `PO448121` |
| 2 | `PO-` + year + `-` + 4 digits | `PO-2026-0448` |
| 3 | `PO` + space + 6 digits | `PO 448121` |

Family 3 exists to exercise the scorer's space handling (§5.4). Year drawn
from {2025, 2026} to sit plausibly against `BASE_DATE` (2026-03-02).

### 2.6 HS codes

Current state: 4-digit headings in `reference.py`, and `hs_code` truth is
deliberately null because no template renders it. The research pins the gap
(real commercial documents carry 6 to 10 digits: 8-digit HTS at US release per
19 CFR 142.6, 8-digit CN codes in the EU; Gap §8) but does **not** supply
verified 6/8-digit codes for the ten commodities in `reference.py`.
Recommendation: **no change in v0.3.** Extending `8517` to an invented
`85171200` would fabricate a real-looking code with a real-world meaning nobody
verified, which is exactly the failure mode this benchmark exists to punish.
If a later version renders HS codes, the prerequisite is a verified 6-digit
WCO subheading per commodity, sourced then, not guessed now. There is no HS
check digit; validation is registry membership only.

### 2.7 UN numbers

Format: `UN` + 4 digits (used throughout research §9; `naive.py` already greps
`UN\d{4}`). There is no check digit; a UN number is an assigned registry entry,
so the only honest validation is membership in a known list. For FreightBench
that list is derived from `COMMODITIES`, which also keeps the TruthIsEvidenced
derivation rule intact (un_number follows from the commodity, `tests`
`DERIVED` tuple). Verified by the research: UN3480, UN3481, UN3090, UN3091
(49 CFR 173.185 via Cornell LII, research §9). Already in the repo but not
re-verified by the research pass: UN1263 (flammable paint), UN1950 (aerosols);
both consistent with general knowledge, flagged here so the uncertainty is on
record. No v0.3 action.

---

## 3. The five-reference question: recommendation, stay with two

The finding (research §1, ONE's own booking guide): a real booking tracks up to
five reference numbers at once: Invoice Ref., BKG SH Ref. (booking-stage
shipper ref), BKG FF Ref. (booking-stage forwarder ref), S/I SH Ref. and
S/I FF No. (shipping-instruction-stage refs). DCSA's B/L standard similarly
carries forwarding-agent reference, consignee reference, export reference and
carrier booking number as distinct fields (research §6).

Recommendation: **do not add fields.** Three arguments, in descending weight:

1. **The five-slot taxonomy belongs to a carrier portal's lifecycle ledger,
   not to an email.** ONE's five slots span two document stages (booking and
   SI), and FreightBench generates only stage-one request emails. S/I-stage
   refs model a document type that does not exist in the corpus; adding fields
   for them is speculative by definition. The named owner of the five-slot
   requirement is ONE's portal, not any email this benchmark generates.
2. **The repo just paid for speculative fields once.** v0.1 shipped ten fields
   that no template rendered, which corrupted the floor and cost a versioned
   ground-truth confession (README, "Status and honesty" section). Three more
   almost-always-null reference fields would re-inflate the abstention floor
   (already 53.9% for the empty extractor) and dilute exactly the denominator
   the benchmark's discrimination lives in.
3. **The failure mode the five-reference reality creates is testable without
   schema growth.** The real intake failure is misattribution: binding the
   carrier's number, the invoice number, or the agent's file ref into
   `booking_reference` or `customer_reference`. That is tested by putting
   extra, clearly-typed reference strings in the *text* while the schema keeps
   asking for exactly two. The scorer already handles both outcomes: grabbing
   a distractor when truth has a value scores `wrong`; grabbing one when truth
   is null scores `hallucinated`, and hallucination is the benchmark's
   headline trust metric.

**The distractor design** (what v0.3 does instead of adding fields):

- A document may carry 0-2 distractor references drawn from §2.1-§2.3 (an AWB
  of a prior shipment, a container number, a house B/L number, a "carrier
  booking number to follow"). Prose owners choose wording; this spec fixes the
  strings and the rules.
- Rule 1: a distractor string never equals, contains, or is contained in any
  truth reference string in the same document.
- Rule 2: a distractor is always typed by its surrounding text as something the
  schema does not ask for ("AWB", "container", "carrier booking no."), never
  labelled in a way that makes it a defensible reading of `booking_reference`
  or `customer_reference`. If a wording makes two readings defensible, that
  field must go into `contested_fields`, and at that point the document is
  testing judgment, not extraction; avoid.
- Hazard flagged for prose owners: in `agent_not_shipper`, an agent's "our
  file ref" IS the sender's own reference under the schema description, so an
  agent file ref is not a distractor there; it is a truth candidate. Do not
  render both an agent file ref and another booking reference in that
  pathology without routing the field through `contested_fields`.

**The one field worth reconsidering later:** `carrier_booking_reference`. It is
the strongest of the five (Freightos: a forwarder confirmation restates the
carrier's booking number alongside its own file ref, research §3; DCSA lists it
as a first-class shipment field, research §6). But it only exists after a
carrier accepts a booking, and FreightBench documents are inbound requests
where it has not been issued yet. Defer until a confirmation-side document type
exists (the research's Gap §6 already flags that whole document class as
missing). Revisit then, not now.

---

## 4. Malformed-reference pathology: recommendation, against

The candidate (floated by Gap §2): a document carrying an AWB whose check digit
is arithmetically impossible (trailing 7, 8 or 9) or simply wrong.

Judged honestly, this fails the benchmark's own bar for a pathology, "a
distinct failure mode with a distinct correct behaviour" (`pathologies.py`):

1. **The correct behaviour is indistinguishable from no behaviour.** Ground
   truth for an extraction field must be the verbatim string in the document
   (TruthIsEvidenced). So a malformed AWB's truth is the malformed string, and
   every extractor that copies what it reads scores `correct`, from the naive
   regex to any LLM. A pathology that everything passes measures nothing, which
   is the same argument the repo already makes against clean documents.
2. **What it would actually test is mod-7 arithmetic performed mid-extraction.**
   That is a puzzle, not intake skill. In real operations nobody validates
   check digits at email-reading time; a bad AWB surfaces when a downstream
   carrier system rejects it. The research's closest real-world signal is MSC's
   "Typing Error" amendment reason code (research §4), and the amendment
   happens at the carrier portal, after intake, by the person who typed it.
3. **The failure it could theoretically catch, silent repair, is unevidenced.**
   The observed hallucination modes in the model runs are booleans asserted
   from silence and country codes inferred from legal suffixes (README, model
   results). No run showed a model "fixing" an identifier. Designing a
   pathology for a speculative failure mode is the speculative-field mistake
   in pathology form.
4. **The schema has no channel for "present but invalid."** `contested_fields`
   models two stated values in conflict, not one invalid value. Scoring
   invalidity would need new machinery for a behaviour nobody has observed.

**Where the check digits actually earn their keep:** in the generator and the
test suite. Every AWB and container number the corpus ever emits must pass its
own validator (tests in §7), which is a ground-truth trust property, the thing
this benchmark sells. Arithmetic belongs on the corpus side of the contract,
not in the extractor's obstacle course.

If evidence of silent identifier repair ever shows up in a model run, revisit
with a verbatim-truth design (the malformed string as truth, testing that
models copy rather than correct). And if a reference-focused pathology is ever
wanted, the real intake failure worth a slot is **misattribution** (the
distractor design in §3 already lays its groundwork); that call belongs to the
pathology owner, not this spec.

One line on a scorer-side alternative considered and dropped: a diagnostic
reporting what share of *predicted* identifiers fail their checksum would be a
cheap hallucination tripwire (an invented AWB passes mod 7 one time in seven).
But v0.3's truth references are house formats with no checksum, so the
diagnostic has nothing to bite on. Not now.

---

## 5. Integration requirements

### 5.1 Module layout

One new module, `freightbench/reference_formats.py` (Gap §2 already names it),
pure standard library, all generation driven by a caller-supplied
`random.Random`. Sketch in §6. `generate.py` swaps its two inline f-strings
(`BK-{...}`, `PO{...}`) for `make_booking_reference(...)` /
`make_customer_reference(...)` calls; distractor placement lands wherever the
prose owners put it, drawing strings from the same module.

### 5.2 TruthIsEvidenced

The invariant test checks `str(value).casefold() in text` for code fields, so:
**truth stores the exact surface form as rendered, always.** If the body says
`999-53729071`, truth (if it is truth at all) is `999-53729071`, not a
normalized 11-digit run. Distractor strings never enter ground truth, and the
invariant only binds truth to text, not text to truth, so distractors are free
difficulty with no invariant cost. `multi_shipment` keeps nulling its booking
references (still rendered nowhere); `ambiguous_port`'s hyphenated subject
keeps working since substring matching is indifferent to surrounding hyphens.

### 5.3 Determinism

All draws come from the document's existing rng in a fixed order. The one loop
(ISO 6346 remainder-10 re-draw) pulls from the same seeded rng, so it is
deterministic; expected iterations ~1.1. Corpus bytes change in v0.3 no matter
what (that is the point), so no stream-compatibility contortions are needed;
the README's version-comparability note already covers the break, and the
canonical corpus regenerates from the same seed constant.

### 5.4 Scorer amendment (recommended): `code` ignores spaces and hyphens

The `code` rule is currently `strip().upper()` equality, so `999-5372907-1`
vs `99953729071` and `PO 448121` vs `PO448121` score `wrong`. Both surface
forms of the AWB are cited (research §3, §5), and the spaced container
rendering is cited too (research §6), so surface-form variance is real, and
punishing a normalized prediction against a hyphenated truth measures
formatting, not extraction. The repo already accepts this argument for company
suffixes. Amendment, in `values_match`:

```python
if rule in ("exact", "code"):
    e = str(expected).strip().upper()
    g = str(got).strip().upper()
    if rule == "code":
        e = re.sub(r"[\s-]", "", e)
        g = re.sub(r"[\s-]", "", g)
    return e == g
```

`exact` (mode, incoterm, freight_terms) is deliberately untouched. Stripping is
harmless for the other `code` fields (LOCODEs, ISO-2, ISO-3, hs_code,
un_number contain neither character, and it forgives a predicted `UN 3480`).
Test vectors in §7.

### 5.5 Couplings that break and must be swept

- `naive.py`: the `\bBK-\d{5}\b` regex dies with the format. The
  afternoon-engineer replacement is label/position anchoring, e.g. take the
  trailing reference-shaped token of the subject line
  (`re.search(r"([A-Z]{2,3}-?\s?\d{5,9}|\bBKG\d{6}\b|\b\d{7,9}\b)\s*(?:\(corrected\))?\s*$", subject)`
  is one sketch; the naive owner decides). Naive degrading somewhat on
  heterogeneous references is informative, not a bug; naive collapsing to zero
  would break the CI bracket check (`naive` must stay between `empty` and
  0.95 critical), so it must still catch the common families.
- CI: the corpus-reproducibility step is unaffected (still byte-identical per
  seed); the reference-extractor bracket step is the one to watch after the
  naive sweep.
- `examples/naive-report.txt` regenerates.
- `llm.py`: no prompt change; the schema text is untouched, so
  `PROMPT_VERSION` stays. (Published v0.2 preview numbers are already
  non-comparable to v0.3 by the README's own versioning rule.)
- `tests/test_freightbench.py`: no existing assertion hardcodes `BK-` or
  `PO`; TruthIsEvidenced passes automatically if §5.2 is respected. New tests
  in §7 are additive.

---

## 6. Code sketch: `freightbench/reference_formats.py`

Implementable as-is; comments carry the citations so the module stays honest
without the spec open.

```python
"""Real-shaped reference identifiers, their generators and validators.

Formats are specced in research/v0.3-specs/spec-reference-formats.md with
per-claim citations into research/freight-document-research.md. Pure standard
library; deterministic given the caller's random.Random.
"""

from __future__ import annotations

import random
import re

_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# --- AWB numbers ------------------------------------------------------------
# 3-digit airline prefix + 7-digit serial + check digit = serial mod 7,
# unweighted (research §5, cross-confirmed; worked example 999-5372907-1).
# A trailing 7, 8 or 9 is arithmetically impossible. 999 is the cited neutral
# prefix (research §3); real prefixes name real airlines, which the corpus
# avoids by policy.

AWB_PREFIX = "999"

def awb_check_digit(serial: int) -> int:
    if not 0 <= serial <= 9_999_999:
        raise ValueError(f"AWB serial out of range: {serial}")
    return serial % 7

def make_awb(rng: random.Random) -> str:
    """Renders '###-########' (serial + check concatenated), the SLI box-13
    mask (research §4) and the Cargo-IMP sample form 777-12345675 (§11)."""
    serial = rng.randint(0, 9_999_999)
    return f"{AWB_PREFIX}-{serial:07d}{awb_check_digit(serial)}"

_AWB_RE = re.compile(r"^(\d{3})-?(\d{7})-?(\d)$")

def is_valid_awb(s: str) -> bool:
    m = _AWB_RE.match(re.sub(r"\s", "", str(s)))
    return bool(m) and int(m.group(3)) == int(m.group(2)) % 7

# --- ISO 6346 container numbers ---------------------------------------------
# Shape pinned by the research (4 letters ending U + 6 digits + check digit,
# research §6 / Gap §2). The check-digit arithmetic below is the published
# ISO 6346 algorithm, reproduced from general knowledge and NOT present in the
# research file; verify independently before ground truth ever depends on it.
# Self-check anchor: CSQU305438 -> 3 (the standard's canonical example).

_ISO6346_LETTERS = {
    "A": 10, "B": 12, "C": 13, "D": 14, "E": 15, "F": 16, "G": 17, "H": 18,
    "I": 19, "J": 20, "K": 21, "L": 23, "M": 24, "N": 25, "O": 26, "P": 27,
    "Q": 28, "R": 29, "S": 30, "T": 31, "U": 32, "V": 34, "W": 35, "X": 36,
    "Y": 37, "Z": 38,
}  # values 10..38 skipping 11, 22, 33

# Fictional owner codes echoing the repo's fictional forwarders; not checked
# against the BIC register (same accepted collision risk as company names).
CONTAINER_OWNER_CODES = ("KGFU", "HCYU", "PFLU")

def _iso6346_sum(stem: str) -> int:
    return sum(
        (_ISO6346_LETTERS[ch] if ch.isalpha() else int(ch)) * (2 ** i)
        for i, ch in enumerate(stem)
    )

def iso6346_check_digit(prefix_and_serial: str) -> int:
    """prefix_and_serial: 4 letters + 6 digits, e.g. 'KGFU123456' -> 0."""
    s = re.sub(r"[\s-]", "", str(prefix_and_serial)).upper()
    if len(s) != 10 or not s[:4].isalpha() or not s[4:].isdigit():
        raise ValueError(f"not a 4-letter + 6-digit stem: {prefix_and_serial!r}")
    return (_iso6346_sum(s) % 11) % 10

def make_container_number(rng: random.Random) -> str:
    owner = rng.choice(CONTAINER_OWNER_CODES)
    while True:  # deterministic: same seeded rng; P(reject) ~= 1/11
        stem = f"{owner}{rng.randint(0, 999_999):06d}"
        # Refuse remainder-10 serials so no emitted number relies on the
        # 10 -> 0 fold, the one corner the research cannot confirm.
        if _iso6346_sum(stem) % 11 != 10:
            return f"{stem}{iso6346_check_digit(stem)}"

def is_valid_container_number(s: str) -> bool:
    t = re.sub(r"[\s-]", "", str(s)).upper()
    if len(t) != 11 or not t[:4].isalpha() or not t[4:].isdigit():
        return False
    return int(t[10]) == iso6346_check_digit(t[:10])

# --- Ocean house B/L numbers ------------------------------------------------
# No universal format, no check digit; house B/Ls carry the issuer's SCAC and
# US manifest rules cap the identifier at 16 chars (research §6, vizionapi).
# SCAC + 9 digits = 13 chars. Fictional codes; never emit the DocShipper
# 'MAEU...' strings the research flags as probable fabrication.

HOUSE_BL_SCACS = ("HCYU", "PFLU", "KGFU")

def make_house_bl(rng: random.Random) -> str:
    return f"{rng.choice(HOUSE_BL_SCACS)}{rng.randint(0, 999_999_999):09d}"

# --- Sender house references (booking_reference) ----------------------------
# No source pins these; they are internal by nature. Families are chosen for
# heterogeneity, anchored on the one real-shaped exemplar BHK51332862
# (3 letters + 8 digits, freightcourse, research §3). Pure-numeric refs are
# always >= 7 digits so they cannot collide with a rendered weight or count.

def make_booking_reference(rng: random.Random, family: int | None = None) -> str:
    fams = (
        lambda: "".join(rng.choice(_UPPER) for _ in range(3))
                + f"{rng.randint(0, 99_999_999):08d}",
        lambda: "".join(rng.choice(_UPPER) for _ in range(2))
                + f"-{rng.randint(0, 999_999):06d}",
        lambda: f"BKG{rng.randint(100_000, 999_999)}",
        lambda: str(rng.randint(1_000_000, 999_999_999)),
    )
    pick = fams[family % len(fams)] if family is not None else rng.choice(fams)
    return pick()

# --- Customer references (customer_reference) -------------------------------
# Existence pinned (UK gov invoice checklist, research §7); format is not.
# PO-prefixed only, so the string stays self-labelling in prose.

def make_customer_reference(rng: random.Random) -> str:
    fams = (
        lambda: f"PO{rng.randint(100_000, 999_999)}",
        lambda: f"PO-{rng.choice((2025, 2026))}-{rng.randint(1000, 9999)}",
        lambda: f"PO {rng.randint(100_000, 999_999)}",
    )
    return rng.choice(fams)()
```

Note on `family`: passing `COMPANIES.index(shipper) % 4` gives each fictional
company a stable house format across the corpus at zero cost. Optional;
`generate.py` owner's call.

---

## 7. Test plan (unit vectors)

New test classes for `tests/` (or a `tests/test_reference_formats.py`), all
runnable from the worked examples in this spec alone:

```python
class TestAWBCheckDigit(unittest.TestCase):
    def test_worked_examples_from_the_research(self):
        self.assertEqual(awb_check_digit(5372907), 1)  # Freightos 999-5372907-1
        self.assertEqual(awb_check_digit(1234567), 5)  # Cargo-IMP 777-12345675

    def test_trailing_seven_eight_nine_impossible(self):
        self.assertTrue(all(awb_check_digit(s) < 7 for s in range(10_000)))

    def test_validator_accepts_cited_surface_forms(self):
        for form in ("999-53729071", "999-5372907-1", "99953729071"):
            self.assertTrue(is_valid_awb(form))
        self.assertFalse(is_valid_awb("999-5372907-2"))
        self.assertFalse(is_valid_awb("999-5372907-9"))  # impossible digit

    def test_generated_awbs_validate(self):
        rng = random.Random(20260811)
        for _ in range(1000):
            self.assertTrue(is_valid_awb(make_awb(rng)))


class TestISO6346(unittest.TestCase):
    def test_standard_canonical_example(self):
        # From the ISO 6346 standard itself, not the research file. This is
        # the anchor an independent verification must also reproduce.
        self.assertEqual(iso6346_check_digit("CSQU305438"), 3)

    def test_the_research_illustration_is_invalid(self):
        # exportnesthub's 'MSCU 123456 7' is a placeholder; arithmetic says 6.
        # Copied examples are not ground truth; the algorithm is.
        self.assertEqual(iso6346_check_digit("MSCU123456"), 6)
        self.assertFalse(is_valid_container_number("MSCU1234567"))

    def test_computed_vectors(self):
        self.assertEqual(iso6346_check_digit("KGFU123456"), 0)
        self.assertEqual(iso6346_check_digit("HCYU998877"), 4)
        self.assertEqual(iso6346_check_digit("KSGU000000"), 9)

    def test_remainder_ten_folds_to_zero_but_is_never_emitted(self):
        self.assertEqual(iso6346_check_digit("KSGU900000"), 0)  # raw remainder 10
        rng = random.Random(20260811)
        for _ in range(1000):
            n = make_container_number(rng)
            self.assertTrue(is_valid_container_number(n))
            self.assertNotEqual(_iso6346_sum(n[:10]) % 11, 10)


class TestCodeCompareNormalisation(unittest.TestCase):  # with the §5.4 amendment
    def test_hyphen_and_space_insensitive(self):
        self.assertTrue(values_match("booking_reference", "999-5372907-1", "99953729071"))
        self.assertTrue(values_match("customer_reference", "PO 448121", "PO448121"))
        self.assertTrue(values_match("booking_reference", "BHK51332862", "bhk 51332862"))

    def test_identity_still_matters(self):
        self.assertFalse(values_match("origin_location", "CNSHA", "CNPVG"))
        self.assertFalse(values_match("booking_reference", "BKG481205", "BKG481206"))
```

Plus one corpus-level invariant worth adding to `TestTruthIsEvidenced`'s
neighborhood: every string in a generated document that matches the AWB or
container shape must pass its validator (the corpus never emits an invalid
checksummed identifier, per §4's closing argument).

---

## 8. What this spec explicitly does not verify

Kept visible on purpose; each is a place where a future source could overturn
a choice made here.

1. The ISO 6346 letter table and mod-11 procedure (not in the research;
   self-consistent with the standard's canonical example; verify against the
   BIC calculator before container ground truth exists).
2. Whether the container category letter is always U (research shows only U).
3. Fictional 4-letter codes against the BIC register and NMFTA SCAC registry
   (unchecked; collision accepted as with fictional company names).
4. The IATA airline-prefix registry (unchecked; corpus uses the cited-neutral
   999 only).
5. UN1263 and UN1950 (pre-existing in the repo, not covered by the research
   pass).
6. PO and house booking-reference formats (unpinned by nature; families are
   design choices, not claims about reality).
7. The freightcourse "2 letters + 8 digits" gloss vs its own 3-letter example
   string (resolved in favor of the verbatim string).
8. The vizionapi 16-char cap vs its "SCAC + 13 chars" example (resolved in
   favor of the regulatory cap).
