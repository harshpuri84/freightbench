# v0.3 spec: new and revised pathologies

Scope: pathology design only. Prose register and layout are owned by
`spec-email-texture.md`; reference-number formats and the distractor rules are
owned by `spec-reference-formats.md`. Where a pathology here touches their
territory the coordination point is flagged explicitly and this spec defers to
them. Every regulatory claim cites `research/freight-document-research.md` by
line number ("research L717-731"); nothing regulatory is asserted from memory.
Where a value is invented rather than sourced, the text says so.

---

## 1. The problem, measured

The post-fix three-model run (200 documents, prompt v2, four ground-truth
defects repaired, the last being the airport-gateway LOCODE removal):

| System | Pass (all) | Pass (critical) | Wrong | Missed | Hallucination rate |
|---|---|---|---|---|---|
| Opus | 100.0% | 99.9% | 0 / 7,576 | 2 | 0.0% |
| Sonnet | between | between | | | ~0.7% |
| Haiku | | 85.3% | | | 4.4% |

Opus ranged 96.3% to 98.9% per pathology before the last fix and is now
essentially perfect on every one. The corpus cannot distinguish a frontier
model from a perfect one, and the 11 difficulty knobs produce one flat score.

### 1a. Why it saturated: the errors were prompt-shaped, and the prompt grew

Re-scoring the archived prompt-v1 predictions
(`research/model-run-2026-08-16/predictions-*.json`) against the fixed corpus
localises every residual frontier error to exactly two families:

- Opus, prompt v1, fixed corpus: 30 wrong, 280 missed. The 30 wrong are
  `dangerous_goods` flipped to false on dg_undeclared documents (18) and
  Shanghai air/sea LOCODE picks (12). The 280 missed are, without exception,
  `dangerous_goods`/`un_number` nulls where derivation from the commodity was
  expected but the email stated nothing.

Prompt v2 added two rules naming exactly those derivations ("dangerous_goods
and un_number follow from the commodity... even when the sender says no
declaration is needed"; "origin_location and destination_location are derived
from the named place and the mode"). The rerun then scored ~100%. Which means:
every pathology whose correct behaviour can be stated as one general prompt
rule is now solved at the frontier, because frontier models follow stated
rules essentially perfectly. Seven of the ten non-clean pathologies have
their answer spelled out in the canonical prompt (nulls for absent fields,
null on conflict, never merge shipments, kg, ISO dates, the two derivation
rules). What remains is template reading, which was never hard.

The design consequence is the central rule of this spec:

> **A v0.3 pathology must stay hard with its general rule disclosed.** The
> canonical prompt states the extraction contract, and v0.2 proves any
> difficulty that one added prompt sentence can delete will be deleted.
> Durable difficulty therefore has to come from (a) domain knowledge the rule
> cannot enumerate (which UN number these goods carry, which of two
> weight-shaped quantities is the gross weight), or (b) arbitration between
> sources that a rule can only name, not perform (who owns a field, which
> statement in a thread is live). Format tricks are out; the texture spec
> already owns surface difficulty.

### 1b. Two structural problems that cap what any pathology can show

**Probe dilution.** A pathology poisons one or two fields, but the
per-pathology score averages ~15 critical fields per document, so a probe
failed on every document moves its row by single digits. The per-pathology
spread this produces is visible in the archived run: under prompt v1 Opus's
per-pathology critical range was about one point wide even while it was
failing the dg probe on 18 of 18 documents. Fix in §2 (`probe_fields`).

**Some probes are not scored at all.** `weight_conflict`'s probe (null the
conflicted weight) is excluded from the denominator via `contested_fields`,
and the "conflict-detection check" that `score.py`'s comment promises does not
exist in the code. `multi_shipment`'s instruction sentence is likewise
contested-excluded. For those documents the scored surface is pure template
extraction. Rule for v0.3: **no new pathology may put its own probe in
`contested_fields`.** Contested is for genuinely unassertable truth only.

### 1c. Where failure still lives, and the error taxonomy to aim at

The tier separation that survives saturation is all in the expensive
categories: Haiku hallucinates booleans from silence (temperature_controlled
86 times, insurance_required 64, pickup/delivery 42 each in the archived run)
and holds a 4.4% hallucination rate against Sonnet's ~0.7% and Opus's 0.0%.
New pathologies should pull failures toward `wrong` and `hallucinated`, the
outcomes the benchmark exists to price, not toward `missed`.

One more rule, this one about fairness: **unambiguous ground truth, or
contested.** The airport-gateway defect was removed because it asserted a
routing judgment as truth. Every proposed truth value below carries an
explicit argument for why no reasonable freight professional reads it the
other way, and the one field where that argument fails (`shipper_name` in
§4.5) goes into `contested_fields`.

---

## 2. `probe_fields` on the Pathology declaration

```python
@dataclass(frozen=True)
class Pathology:
    key: str
    label: str
    what_it_tests: str
    correct_behaviour: str
    # The fields this pathology poisons. Reporting can then show pass rate on
    # exactly these fields per pathology, undiluted by the ~13 template fields
    # every document shares. Empty tuple = the probe is structural (record
    # count) or distributed (mass absence) rather than field-shaped.
    probe_fields: tuple[str, ...] = ()
```

Backfill for the existing eleven (informational; changes no scoring
semantics):

| key | probe_fields |
|---|---|
| clean | () |
| ambiguous_port | ("origin_location",) |
| weight_conflict | (), probe is contested-excluded today; see §1b |
| unit_ambiguity | ("gross_weight_kg",) |
| date_ambiguity | ("cargo_ready_date",) |
| agent_not_shipper | ("shipper_name",) |
| multi_shipment | (), probe is the record count |
| forwarded_thread | ("pieces",) |
| trailing_correction | ("gross_weight_kg",) |
| missing_critical | ("incoterm",) |
| dg_undeclared | ("dangerous_goods", "un_number") |

The reporting view that consumes this (per-pathology pass rate on probe fields
only) is a `score.py`/CLI change owned by whoever sweeps the scorer in v0.3;
this spec guarantees only that the declaration exists so the view is buildable.
Without it, even a perfectly discriminating pathology moves its headline row by
single digits, and the saturation story repeats one abstraction up.

---

## 3. REVISED: `dg_undeclared`: a real exemption, misapplied

### What is wrong with the current version

The v0.2 body always contains the flat sentence "No dangerous goods
declaration needed for this one" next to a commodity from a three-item
known-DG list. The research calls this out directly: the real-world "no DGD
needed" claim is "a real, narrowly-scoped exception, not a blanket rule"
(research L703-706), and the gap analysis names the v0.2 sentence a strawman
"catchable by keyword-matching" (research L969-973). Since prompt v2 names the
denial case explicitly, the pathology is fully solved at the frontier: it now
tests whether the model read the prompt.

### The real failure mode, per the research

Shippers invoke narrow, real relief provisions incorrectly. The machinery,
all from research L717-731 and L692-706:

- UN3480 is standalone lithium-ion; UN3481 is lithium-ion packed with or
  contained in equipment (research L695-698, L717-718).
- "Section II" is a relaxed provision that caps a consignment at one package
  (PI965/PI968) (L719-720); many carriers refuse Section II outright, and the
  industry is shifting to full Section IA/IB regardless (L720-722).
- UN3480 cells carry a ≤30% state-of-charge cap for air, and that cap "does
  not formally apply to UN3481" (L722-724).
- The research names the realistic wrong claims verbatim: "shipped under
  Section II, no DGD required" and "reduced state of charge, exempt", and the
  exact error of "conflating UN3480's SOC exemption with UN3481" (L725-731),
  which the gap analysis calls a distinction shippers "routinely get wrong in
  practice" (L973-977).

The point that keeps ground truth safe: every one of these provisions is
relief from paperwork and packaging, not a reclassification of the goods. A
lithium-ion battery is dangerous goods with an assigned UN number whether or
not any relief applies. That is already the benchmark's declared philosophy
(pathologies.py: hazard follows from the commodity), and prompt v2 already
states it. The revision keeps the same boolean truth while moving the
difficulty to where the prompt rule cannot reach: **which** UN number, when
the sender confidently states the wrong one.

### Variant A (60%): UN3481 goods, UN3480's allowance claimed, UN3480 printed

Commodity is equipment with installed cells, so UN3481 by definition
(L695-698, L717-718). The sender cites the state-of-charge provision, which
belongs to UN3480 and does not extend to UN3481 (L722-724), and names UN3480
as the basis. Requires one new `COMMODITIES` entry:

```python
"handheld barcode scanners with installed lithium-ion batteries":
    ("8471", True, "UN3481", True),
```

(The 4-digit heading is inert: `hs_code` truth stays null and no template
renders it, per the reference spec §2.6. "8471" has the same
unverified-but-inert status as the existing headings.)

Exact email phrasing (illustrative values; rng fills them):

```
Subject: Booking BK-48213

Hi,

Booking request below.

Mode: AIR
Origin: Singapore
Destination: Chennai
Shipper: Arclight Electronics Inc
Consignee: Tamarind Textiles Pvt Ltd
Commodity: handheld barcode scanners with installed lithium-ion batteries
Pieces: 14 cartons
Gross weight: 1850 kg
Volume: 7.4 cbm
Incoterm: FCA
Cargo ready: 2026-03-18
Freight terms: PREPAID
Our reference: PO662101

Note on the scanners: our compliance team confirms these travel under the
UN3480 low state-of-charge provision, all cells held at 25% SOC, so the
consignment is fully excepted. No dangerous goods declaration or Class 9
handling needed, please book as general cargo.

Best regards,
Marta Vermeer
Arclight Electronics Inc
```

Exact correct extraction (probe fields; everything else as stated in the
block):

```json
{
  "dangerous_goods": true,
  "un_number": "UN3481",
  "commodity_description": "handheld barcode scanners with installed lithium-ion batteries",
  "mode": "AIR"
}
```

Why the claim is wrong, precisely: (1) the state-of-charge cap is a UN3480
air provision that does not formally extend to UN3481 (L722-724), so the
cited basis does not exist for these goods; (2) batteries contained in
equipment are UN3481 by definition (L695-698), so the sender's own UN number
misclassifies the goods their own sentence describes; (3) even valid relief
is relief from documentation, not from being dangerous goods (L703-706), and
carriers increasingly reject such bookings anyway (L720-722). The instruction
"book as general cargo" is false under every reading.

The load-bearing detail: **the only UN number printed in the document is the
wrong one.** Truth for `un_number` is UN3481, derived from the commodity.
An extractor that copies the stated code reproduces the shipper's
misdeclaration, which is precisely the intake failure that puts misdeclared
lithium on passenger aircraft. That failure is invisible to the v0.2 design,
where the commodity registry and the stated facts always agree.

### Variant B (40%): UN3480 spares, Section II claimed for a multi-package lot

Commodity is the existing `lithium-ion battery packs` entry (UN3480). The
builder forces `pieces` to 8-20 and the sender claims Section II relief:

```
These are spare packs held at 25% state of charge, shipping under Section II
as excepted lithium batteries. No dangerous goods declaration and no UN-spec
packaging needed, standard cargo handling is fine.
```

Correct extraction: `dangerous_goods: true`, `un_number: "UN3480"`. Wrong
because Section II caps the consignment at one package and the booking states
8-20 (L719-720, checkable from the document's own Pieces line); because
relief is not reclassification (L703-706); and because the research flags
"reduced state of charge, exempt" as the historically-true-ish claim that no
longer survives contact with carriers (L725-731). No UN number is printed in
this variant; truth is derived, as today.

Both variants force `mode="AIR"` (the SOC cap and PI965/PI968 are air
provisions, L719-724, so the claim is only coherent on an air booking), and
both keep the literal substring "No dangerous goods" so the existing test
grep and the texture spec's §2.4 note survive unchanged.

### What it tests / correct behaviour / frontier failure / why not a trick

- **Tests:** whether DG classification survives a confident, regulation-shaped,
  partially-true exemption claim, and specifically whether the UN number is
  derived from the goods or copied from the sender's citation.
- **Correct behaviour:** `dangerous_goods=true`; `un_number` from the
  commodity description, overriding the printed UN3480 in variant A.
- **Why a frontier model can fail it:** the prompt licenses derivation but the
  base instinct of an extractor is to prefer a stated value over a derived
  one, and the stated value here is specific, confident, and attributed to a
  compliance team. Passing variant A requires knowing that installed-in-
  equipment means UN3481 and that the SOC provision is scoped to UN3480. That
  is knowledge, not rule-following; no prompt sentence enumerates UN numbers.
  The v1 evidence shows exactly this deference pattern: before the prompt
  named the denial case, Opus believed the sender 18 times out of 18.
- **Why it is not a trick:** the research documents these exact claims as what
  real shippers write (L725-731) and the exact conflation as routine
  (L973-977). The commodity line states the battery content in plain words;
  nothing is hidden. A DG desk clerk who reads "scanners with installed
  li-ion batteries, shipper cites the UN3480 SOC provision" books it UN3481
  Class 9 and bounces the exemption claim; that is the weekly reality this
  models. The claim fails in at least two independent, citable ways per
  variant, so there is no reading under which the goods are not DG.

### Load-bearing companion change: schema wording

`schema.py` currently reads:

```python
Field("dangerous_goods", "boolean", "critical", "Whether the shipment is declared dangerous goods"),
Field("un_number", "code", "standard", "UN number, required when dangerous_goods is true"),
```

"Declared" makes false a defensible answer to a non-declaration, and nothing
tells the extractor whose UN number wins. Both must change before this
revision lands, or the pathology fails its own no-trick standard:

```python
Field("dangerous_goods", "boolean", "critical",
      "Whether the goods are dangerous goods. Classification follows the "
      "commodity, not the sender's assertion"),
Field("un_number", "code", "standard",
      "UN number for the goods as described. Follows the commodity, not a "
      "code the sender may have stated"),
```

The canonical prompt inherits these lines via `_field_lines()`, so this is a
PROMPT_VERSION bump (see §7). Note what is deliberately NOT added: no prompt
sentence about state of charge, Section II, or UN3480 vs UN3481. The general
rule is disclosed; the instance knowledge is the test. That is the §1a design
rule applied.

### Builder sketch

```python
def dg_undeclared(self, doc_id: str) -> Document:
    r = self._base(mode="AIR")  # SOC/Section II talk is an air regime (L719-724)
    if self.rng.random() < 0.6:
        # Variant A: UN3481 goods, UN3480's SOC allowance claimed and printed.
        commodity = "handheld barcode scanners with installed lithium-ion batteries"
        un = "UN3481"
        claim = ("Note on the scanners: our compliance team confirms these "
                 "travel under the UN3480 low state-of-charge provision, all "
                 "cells held at 25% SOC, so the consignment is fully excepted. "
                 "No dangerous goods declaration or Class 9 handling needed, "
                 "please book as general cargo.")
    else:
        # Variant B: UN3480 spares, Section II claimed for 8-20 packages.
        commodity = "lithium-ion battery packs"
        un = "UN3480"
        r["pieces"] = self.rng.randint(8, 20)
        claim = ("These are spare packs held at 25% state of charge, shipping "
                 "under Section II as excepted lithium batteries. No dangerous "
                 "goods declaration and no UN-spec packaging needed, standard "
                 "cargo handling is fine.")
    r.update(commodity_description=commodity, dangerous_goods=True, un_number=un)
    body = ("Hi,\n\nBooking request below.\n\n" + self._block(r) + "\n\n" + claim
            + self._sig(company=r["shipper_name"]))
    note = ("The sender invokes a real, narrow relief provision incorrectly. "
            "The state-of-charge cap is a UN3480 air rule that does not extend "
            "to UN3481; Section II is paperwork relief capped at one package, "
            "not reclassification. dangerous_goods is true and un_number "
            "follows the commodity, overriding any code the sender printed. "
            "(research L692-706, L717-731)")
    return Document(doc_id, "dg_undeclared", f"Booking {r['booking_reference']}",
                    body, [self._clean(r)], note=note)
```

Evidence invariant: `dangerous_goods` and `un_number` are already in the
tests' DERIVED tuple, so variant A's truth UN3481 needs no textual evidence
and the printed UN3480 decoy costs nothing (the invariant binds truth to
text, not text to truth). The commodity string and variant B's pieces are
rendered verbatim.

Test replacement for `test_dg_inferred_despite_sender_denial`:

```python
def test_dg_exemption_claim_does_not_flip_classification(self):
    for d in self.by_key["dg_undeclared"]:
        self.assertIn("No dangerous goods", d.body)      # sender still denies
        self.assertIn("state of charge", d.body.lower()) # via a real provision
        self.assertTrue(d.shipments[0]["dangerous_goods"])
        if "installed" in d.shipments[0]["commodity_description"]:
            self.assertIn("UN3480", d.body)              # the printed decoy
            self.assertEqual(d.shipments[0]["un_number"], "UN3481")
        else:
            self.assertEqual(d.shipments[0]["un_number"], "UN3480")
            self.assertGreaterEqual(d.shipments[0]["pieces"], 8)
```

Updated `Pathology` entry:

```python
Pathology(
    "dg_undeclared",
    "Real DG exemption, misapplied",
    "Whether classification survives a confident, regulation-literate "
    "exemption claim. The sender cites a real relief provision (state of "
    "charge, Section II) that does not apply to these goods, and may print "
    "the wrong UN number as its basis.",
    "dangerous_goods is true and un_number follows the commodity: installed "
    "in equipment means UN3481 even when the sender cites UN3480. Relief "
    "provisions are paperwork relief, never reclassification.",
    probe_fields=("dangerous_goods", "un_number"),
),
```

---

## 4. NEW pathologies

Five proposed, presented in rank order (ranking argued in §6). Each entry:
research basis, document, exact ground truth, what it tests, why a frontier
model can fail it, why it is not a trick, invariant safety, sketches.

---

### 4.1 `booking_amendment`: the delta rides on top, the truth sits below

**Research basis.** Real booking correspondence is "a thread with amendments
and re-confirmations, not one clean message": a single shipment generates 40+
messages, 10-20 in the booking phase alone (research L111-117). Amendments
are so routine that MSC's shipping-instruction channel enumerates amendment
reason codes ("Split B/L", "Seal Change due to physical inspection", "Typing
Error") (L349-355). The gap analysis names the missing "sense of an ongoing,
amended, multi-message conversation" directly (L1039-1047).

**Document.** A two-message thread, newest on top. The top message states one
change and explicitly leaves the rest standing. The quoted original below
carries the full booking, including the superseded value.

```
Subject: RE: Booking BK-51872 - amendment

Hi,

One amendment to the booking below: the consignee is now Meridian Trading Co.
Everything else stands exactly as per my message below. Please confirm the
update.

-----Original Message-----
From: exports
Subject: Booking BK-51872

Hi,

Please quote and book the following shipment.

Mode: LCL
Origin: Hamburg
Destination: Chennai
Shipper: Nordwind Maschinenbau GmbH
Consignee: Kestrel Industrial Ltd
Commodity: hydraulic pumps
Pieces: 18 crates
Gross weight: 5400 kg
Volume: 21.4 cbm
Incoterm: FCA
Cargo ready: 2026-03-21
Freight terms: PREPAID
Our reference: PO518204

Best regards,
Tomasz Kowalski
Nordwind Maschinenbau GmbH
```

**Ground truth, exactly.** One record. `consignee_name = "Meridian Trading
Co"` (the amendment). Every other field takes the quoted original's value:
`mode=LCL`, `pieces=18`, `gross_weight_kg=5400`, `volume_cbm=21.4`,
`incoterm=FCA`, `cargo_ready_date=2026-03-21`, and so on. Nothing contested.
A second variant (40% of draws) amends `cargo_ready_date` instead ("cargo
ready has moved to {date}"), so the amended field is not constant across the
pathology and the correct general rule (amended field from the top, the rest
from the quote) is what gets tested, not one memorized instance.

**What it tests.** Per-field thread-state tracking. This is the deliberate
inverse of `forwarded_thread`. There, the newest message restates everything
and the quoted values are stale. Here, the newest message restates one field
and the quoted values are the only statement of everything else, and remain
live. An extractor cannot pass both pathologies with a positional heuristic:
"ignore quoted material" fails this one across a dozen fields; "read
everything equally" fails forwarded_thread. The only policy that passes both
is the one a booking clerk actually runs: latest statement per field wins,
silence preserves.

**Correct behaviour.** Apply the delta to the base. Amended field from the top
message, all other fields from the quoted block, one record.

**Why a frontier model can fail it.** The corpus itself installs the wrong
prior: forwarded_thread and trailing_correction both reward discounting
earlier/quoted material, and models carry the same prior from real training
mail. The canonical prompt offers no rescue; its only relevant rule ("use
null for any field the email does not state") actually punishes the failure
correctly, since the quoted block does state the fields. The plausible
frontier failure is emitting a delta-only record (consignee plus nulls),
which is mass `missed` on critical fields, or keeping the quoted consignee,
which is `wrong` on a critical field. In production this exact failure ships
the original consignee on the B/L after the customer changed it, which is a
cargo-release-to-the-wrong-party incident.

**Why it is not a trick.** The top message says in plain words that everything
else stands and points at the quoted block. Amendment emails are the daily
bread of booking desks (L111-117, L349-355); nothing is hidden, misdirected,
or dependent on arcana. A human clerk gets this right without thinking. The
difficulty is entirely in whether the model's thread heuristic is a rule
about position or a rule about supersession.

**Ground-truth safety.** All truth values are stated verbatim in the body (the
evidence test concatenates subject and body, and quoted text is body text).
The amendment sentence names the new value in full; the old consignee remains
in the quote as the wrong-answer magnet, exactly as forwarded_thread already
does for pieces. No professional reads "the consignee is now X, everything
else stands" as anything but X plus the quoted base. Nothing contested.

**Builder sketch.**

```python
def booking_amendment(self, doc_id: str) -> Document:
    r = self._base()
    amend_date = self.rng.random() < 0.4
    old = dict(r)
    if amend_date:
        old_date = date.fromisoformat(r["cargo_ready_date"])
        new_date = old_date + timedelta(days=self.rng.randint(4, 12))
        r["cargo_ready_date"] = new_date.isoformat()
        change = (f"the cargo ready date has moved to {new_date.isoformat()}")
    else:
        new_consignee, _cc = self.rng.choice(
            [c for c in COMPANIES
             if c[0] not in (r["consignee_name"], r["shipper_name"])])
        r["consignee_name"] = new_consignee
        change = f"the consignee is now {new_consignee}"
    body = (f"Hi,\n\nOne amendment to the booking below: {change}. "
            "Everything else stands exactly as per my message below. "
            "Please confirm the update.\n\n"
            "-----Original Message-----\n"
            f"From: exports\nSubject: Booking {r['booking_reference']}\n\n"
            "Hi,\n\nPlease quote and book the following shipment.\n\n"
            + self._block(old)
            + self._sig(company=r["shipper_name"]))
    note = ("An amendment thread. The top message changes exactly one field "
            "and states that the rest stands; the quoted original is the only "
            "statement of every other field and remains live. Dropping or "
            "nulling the quoted fields is the failure, as is keeping the "
            "superseded value. (research L111-117, L349-355, L1039-1047)")
    return Document(doc_id, "booking_amendment",
                    f"RE: Booking {r['booking_reference']} - amendment",
                    body, [self._clean(r)], note=note)
```

(Draw order is fixed: variant coin, then the change draw; `_base()` precedes
both. The old record dict is rendered; the mutated record is truth. The
consignee variant renders the old value only inside the quote and the new
value only in the amendment sentence, both verbatim, so the evidence
invariant holds for whichever is truth.)

`Pathology` entry:

```python
Pathology(
    "booking_amendment",
    "Amendment thread: delta on top, base below",
    "Whether the extractor tracks thread state per field. The newest message "
    "amends exactly one field and says the rest stands; the quoted original "
    "below is the only statement of every other field and is still live. The "
    "inverse of forwarded_thread: no positional heuristic passes both.",
    "Apply the delta to the base: the amended field from the top message, "
    "every other field from the quoted block, one record. Quoted is not the "
    "same as stale.",
    probe_fields=("consignee_name", "cargo_ready_date"),
),
```

Test sketch:

```python
def test_amendment_merges_delta_onto_quoted_base(self):
    for d in self.by_key["booking_amendment"]:
        rec = d.shipments[0]
        self.assertIn("Everything else stands", d.body)
        self.assertEqual(len(d.shipments), 1)
        # the quoted base fields survive into truth
        self.assertIsNotNone(rec["gross_weight_kg"])
        self.assertIsNotNone(rec["incoterm"])
        if "consignee is now" in d.body:
            new = d.body.split("consignee is now ")[1].split(".")[0]
            self.assertEqual(rec["consignee_name"], new)
```

**Honest uncertainty.** The "everything else stands" sentence is explicit, and
a frontier model reading carefully will often pass. Ranked first anyway
because the failure pressure is systematic (the corpus and real mail both
train the discounting heuristic), the failure mass is large when it fires (a
dozen fields at once, most critical), and no prompt rule can perform the
merge for the model. If frontier models pass it cleanly, the pathology still
retires the "ignore quotes" shortcut permanently, which no current pathology
does.

---

### 4.2 `conditional_acceptance`: the carrier's status outranks the gloss

**Research basis.** Booking confirmations are three-valued: MSC's own IFTMBC
spec encodes Pending / Accepted / Conditionally Accepted (codes AJ / AP / CA)
(research L217-233, esp. L224-226 and realism note L228-230). The
confirmation reaches the shipper as email, and the shipper-facing message
restates the carrier's own confirmation (L244-250); "we received your
request" is explicitly not "confirmed" (Freightlink, L252-257). The
generator has no confirmation-side document at all (Gap-6, L984-990).

**Schema addition, minimal and justified.** One field:

```python
Field("booking_status", "exact", "standard",
      "Carrier's stated status where a carrier response is quoted: "
      "PENDING | ACCEPTED | CONDITIONALLY ACCEPTED. Null when no carrier "
      "response appears"),
```

Space-separated enum values so the evidence invariant's substring check
passes against rendered text; `exact` compare scores them strictly. The field
is null on all other pathologies. This is the minimal beachhead into the
confirmation-side document class Gap-6 says is missing entirely; the separate
deadline fields real confirmations carry (VGM cut-off, SI due, port cut-off,
L228-233) can follow in a later version without rework. The wording
"carrier's stated" is the minimal ownership marker that makes truth
assertable; without it, the sender's gloss would be a defensible reading and
the field would be contested, which per §1b would gut the probe.

**Document.** A thread. Bottom (quoted): the carrier's confirmation with its
own booking number and a `Status:` line. Top (newest): the shipper forwarding
it to the forwarder with an optimistic human summary. The status line is
drawn: CONDITIONALLY ACCEPTED (40%), PENDING (30%), ACCEPTED (30%). **The
gloss is identical in all three variants** ("good news, we are confirmed"),
so nothing about the document's shape reveals the answer; only reading the
quoted status line does. For ACCEPTED draws the gloss happens to be right,
which keeps the pathology honest: a system cannot learn "this shape means
emit CONDITIONALLY ACCEPTED".

```
Subject: RE: booking BK-60218 - carrier confirmation

Hi,

Good news, the carrier has come back and we are confirmed. Please go ahead
and arrange trucking and the export docs. Details again for your file:

Mode: FCL
[field block as usual, sender's own reference in the subject as today]

-----Original Message-----
From: carrier bookings desk
Subject: Booking Confirmation

Carrier booking number: 6071180550
Status: CONDITIONALLY ACCEPTED
Conditions: subject to equipment availability at origin and receipt of VGM
by the stated cut-off. The booking is not final until both conditions clear.
```

(PENDING variant's quoted block: "Status: PENDING. Your request has been
received and space is awaited; a booking receipt notice follows.": the
received-vs-confirmed distinction is the documented one, L252-257, L103-104.
ACCEPTED variant: "Status: ACCEPTED. Equipment and space confirmed.")

**Ground truth, exactly.** `booking_status` = the quoted Status line,
verbatim ("CONDITIONALLY ACCEPTED" / "PENDING" / "ACCEPTED").
`booking_reference` = the sender's own reference (subject line, as existing
builders render it). The carrier's number has no schema slot and lands
nowhere; per the reference spec's distractor rules it is typed by its label
("Carrier booking number") as something the schema does not ask for, and
extracting it into `booking_reference` scores `wrong`.

**What it tests.** Field ownership. The inversion of forwarded_thread along
the other axis: there, one party restates its own values and recency wins;
here, two parties speak, and the newest, plainest, most human sentence in the
email ("we are confirmed") is wrong for two of three draws, because the field
belongs to the carrier and a shipper cannot upgrade the carrier's status by
paraphrasing it. Together with §4.1 this completes the pair: 4.1 kills
"quoted means stale", 4.2 kills "newest means true".

**Correct behaviour.** Report the carrier's stated status verbatim; ignore
the gloss; leave the carrier's number out of the reference slots.

**Why a frontier model can fail it.** Every general heuristic points the
wrong way on the CA/PENDING draws: recency, plain language over stiff blocks,
deference to the live sender, and holistic summarization ("this email is
about a confirmed booking"). The schema description arbitrates ownership but
cannot read the status line for the model. The expensive real-world failure
this prices: a conditionally accepted booking trucked to port as confirmed
and rolled when the condition fails.

**Why it is not a trick.** The three-valued status is how carriers actually
answer (wire-format codes in MSC's own spec, L224-226); the
shipper-forwards-the-confirmation email is the documented delivery path
(L244-250); the optimistic gloss is ordinary human summarization, not an
adversarial plant. No ops handler hesitates over the rule ("the carrier's
formal status stands until the carrier changes it"). And in 30% of draws the
gloss is simply right.

**Ground-truth safety.** The status string is stated verbatim in caps in the
quoted block. The sender's reference and the carrier's number are kept
non-colliding (reference spec Rule 1), and the carrier number's label types
it unambiguously (Rule 2). Nothing contested.

**Builder sketch.**

```python
def conditional_acceptance(self, doc_id: str) -> Document:
    r = self._base(mode="FCL")
    status = self.rng.choices(
        ("CONDITIONALLY ACCEPTED", "PENDING", "ACCEPTED"),
        weights=(40, 30, 30))[0]
    detail = {
        "CONDITIONALLY ACCEPTED":
            "Conditions: subject to equipment availability at origin and "
            "receipt of VGM by the stated cut-off. The booking is not final "
            "until both conditions clear.",
        "PENDING":
            "Your request has been received and space is awaited; a booking "
            "receipt notice follows.",
        "ACCEPTED":
            "Equipment and space confirmed.",
    }[status]
    r["booking_status"] = status
    carrier_no = str(self.rng.randint(6_000_000_000, 6_999_999_999))
    body = ("Hi,\n\nGood news, the carrier has come back and we are "
            "confirmed. Please go ahead and arrange trucking and the export "
            "docs. Details again for your file:\n\n"
            + self._block(r)
            + "\n\n-----Original Message-----\n"
              "From: carrier bookings desk\nSubject: Booking Confirmation\n\n"
              f"Carrier booking number: {carrier_no}\n"
              f"Status: {status}\n{detail}\n"
            + self._sig(company=r["shipper_name"]))
    note = (f"The carrier states {status}; the sender glosses it as "
            "confirmed. booking_status is the carrier's stated value; a "
            "sender cannot upgrade it by paraphrase. The carrier booking "
            "number has no schema slot. (research L217-233, L244-257, "
            "L984-990)")
    return Document(doc_id, "conditional_acceptance",
                    f"RE: booking {r['booking_reference']} - carrier confirmation",
                    body, [self._clean(r)], note=note)
```

(The carrier-number shape is a pure-digit invention in the sketch; the
implementation should draw it via the reference-formats module and enforce
its Rule 1 non-collision against the document's truth references.)

`Pathology` entry:

```python
Pathology(
    "conditional_acceptance",
    "Carrier status vs sender gloss",
    "Whether the extractor ranks the quoted carrier confirmation above the "
    "sender's optimistic paraphrase. Real confirmations are three-valued "
    "(Pending / Accepted / Conditionally Accepted); 'we are confirmed' from "
    "the shipper does not change the carrier's stated status, and sometimes "
    "it happens to match it.",
    "booking_status is the carrier's stated value, read from the quoted "
    "block. Recency is not authority: the newest message is a paraphrase by "
    "a party who does not own the field.",
    probe_fields=("booking_status",),
),
```

Test sketch:

```python
def test_status_is_the_carriers_not_the_gloss(self):
    for d in self.by_key["conditional_acceptance"]:
        self.assertIn("we are confirmed", d.body)
        stated = d.body.split("Status: ")[1].splitlines()[0].strip()
        self.assertEqual(d.shipments[0]["booking_status"], stated)
        self.assertIn(stated, ("CONDITIONALLY ACCEPTED", "PENDING", "ACCEPTED"))
```

**Honest uncertainty.** Two softeners. The field description necessarily
coaches ownership ("carrier's stated"), which a careful frontier model will
use; and a weak model may omit the new field entirely, which scores `missed`,
the cheap failure, rather than `wrong`. Expected to separate mid-tier from
frontier more than frontier from perfect. It also opens the
confirmation-side document class, which is worth a slot on its own.

---

### 4.3 `reference_soup`: five references, two slots

**Research basis.** A real booking tracks up to five reference numbers at
once: shipper ref, forwarder ref, invoice ref, and two SI-stage refs (ONE's
booking guide, research L95-104); a forwarder confirmation carries the
carrier's booking number as a distinct field (L244-250); AES ITN and other
customs references are real, lane-conditional strings (L86-89, L101-104).
The reference spec §3 chose to keep the schema at two reference fields and
test misattribution with typed distractor strings instead, and explicitly
left the concentrated-pathology call to this spec.

**Document.** A booking request whose references arrive as a labelled list,
with the two schema-relevant references and three typed decoys. The subject
carries no reference, and the block's "Our reference:" line is omitted, so
the list is the only source.

```
Subject: Booking and shipping details

Hi,

Please book the below. References for your file:

- Our file reference: KV-204815 (quote on all correspondence)
- PO to show on all shipping docs: PO-2026-0448
- Carrier booking, already placed by us: QHT51332862
- Our invoice reference for last month's shipment: INV-30112 (settled, context only)
- AES ITN from that previous shipment: X-2026-0219-8814

[field block with the "Our reference:" line omitted]
```

**Ground truth, exactly.** `booking_reference = "KV-204815"` (the sender's
own file reference, matching the schema description "Sender's own booking or
quote reference"). `customer_reference = "PO-2026-0448"` (the schema's
"Customer PO or internal reference"; it is the only PO in the document and is
labelled as the one for the shipping docs). The other three land nowhere:
the carrier's number is not the sender's own reference, and the invoice ref
and ITN are explicitly scoped to a previous shipment. Truth strings are drawn
from the reference-formats module's families, so formats stay consistent
with that spec; the decoy strings obey its Rule 1 (never equal to, containing,
or contained in a truth reference) and Rule 2 (always typed by their label as
something the schema does not ask for).

**What it tests.** Reference-role mapping under decoy pressure: whose
reference is this (sender / carrier / customs), and which shipment does it
belong to (this one / last month's). Two sub-skills, role and temporal
scoping, both of which real intake systems get wrong often enough that ONE's
form keeps five separate slots (L95-104).

**Correct behaviour.** Fill the two slots from the two matching roles;
extract the three decoys nowhere; invent nothing for other code-shaped
fields.

**Why a frontier model can fail it.** The carrier's number is deliberately
drawn in the same shape family as sender house references (the one
real-shaped exemplar the research pinned, BHK51332862, is itself a carrier
confirmation reference, L240-242, and the reference spec anchored its sender
family 1 on the same shape). So shape carries zero signal and the labels
carry all of it, which is exactly the real situation. A model ranking
"most reference-looking string" or "first reference mentioned" grabs the
carrier number or the file-adjacent invoice ref; both score `wrong` on a
critical field, or `hallucinated` where truth has no slot.

**Why it is not a trick.** Every string is labelled with its role in plain
words; the decoys are excluded by reading, not by arcana. This is the "for
your file" email every forwarder receives from an organised shipper. The
failure it models (carrier number filed as the house reference, invoice
reconciliation against the wrong string) is among the most common intake
defects there is; the five-slot taxonomy exists because systems must keep
these apart (L95-104).

**Ground-truth safety.** Both truths are stated verbatim; the labels map
one-to-one onto the two schema descriptions; each decoy carries an explicit
disqualifying marker ("Carrier", "last month's shipment", "that previous
shipment"). Two hazards from the reference spec, handled: the sender here is
always the shipper, never a forwarding agent, so the agent's
"our-file-ref-is-truth" hazard (reference spec §3) cannot arise; and the ITN
string is an invented shape under an authentic label, since the research
evidences the label and its lane-conditionality but no ITN digit format
(L86-89), and this spec asserts none.

**Builder sketch.**

```python
def reference_soup(self, doc_id: str) -> Document:
    r = self._base()
    # Truth strings via the reference-formats module (its families, its rng
    # discipline). Decoys re-drawn until Rule 1 holds against both truths.
    ours = make_booking_reference(self.rng)
    po = make_customer_reference(self.rng)
    r["booking_reference"], r["customer_reference"] = ours, po
    def _fresh(maker):
        while True:
            s = maker()
            if all(s not in t and t not in s for t in (ours, po)):
                return s
    carrier_no = _fresh(lambda: "".join(self.rng.choice(_UPPER) for _ in range(3))
                                + f"{self.rng.randint(0, 99_999_999):08d}")
    inv = _fresh(lambda: f"INV-{self.rng.randint(10000, 99999)}")
    itn = _fresh(lambda: f"X-2026-{self.rng.randint(1000, 9999)}"
                         f"-{self.rng.randint(1000, 9999)}")
    refs = ("References for your file:\n"
            f"- Our file reference: {ours} (quote on all correspondence)\n"
            f"- PO to show on all shipping docs: {po}\n"
            f"- Carrier booking, already placed by us: {carrier_no}\n"
            f"- Our invoice reference for last month's shipment: {inv} "
            "(settled, context only)\n"
            f"- AES ITN from that previous shipment: {itn}\n")
    body = ("Hi,\n\nPlease book the below.\n\n" + refs + "\n"
            + self._block(r, omit=("customer_reference",))
            + self._sig(company=r["shipper_name"]))
    note = ("Five reference-shaped strings, two schema slots. "
            "booking_reference is the sender's own file reference; "
            "customer_reference is the PO. The carrier number (same shape "
            "family as house references on purpose) and the two "
            "prior-shipment strings belong nowhere. (research L86-104, "
            "L240-250)")
    return Document(doc_id, "reference_soup", "Booking and shipping details",
                    body, [self._clean(r)], note=note)
```

Enabler: `_block()`'s `omit` must learn `"customer_reference"` (today the
"Our reference:" line is unconditional). Two-line change in `generate.py`.

`Pathology` entry:

```python
Pathology(
    "reference_soup",
    "Five references, two slots",
    "Whether the extractor maps references to roles. Real bookings carry up "
    "to five reference numbers at once (sender's own, PO, carrier booking, "
    "invoice ref, customs ITN); the schema has slots for two, shape carries "
    "no signal, and two of the five belong to a previous shipment.",
    "booking_reference takes the sender's own file reference and "
    "customer_reference the PO. The carrier's number and anything scoped to "
    "a previous shipment are extracted nowhere. Grabbing the most "
    "reference-looking string is the failure.",
    probe_fields=("booking_reference", "customer_reference"),
),
```

Test sketch:

```python
def test_reference_soup_slots(self):
    for d in self.by_key["reference_soup"]:
        rec = d.shipments[0]
        self.assertIn(f"Our file reference: {rec['booking_reference']}", d.body)
        self.assertIn(rec["customer_reference"], d.body)
        self.assertIn("Carrier booking", d.body)
        self.assertNotIn(rec["booking_reference"], d.subject)
        carrier = d.body.split("already placed by us: ")[1].split("\n")[0]
        self.assertNotEqual(rec["booking_reference"], carrier)
```

**Honest uncertainty.** Labels resolve everything for a careful reader, and a
frontier model reads carefully; expected frontier failure is low-to-moderate
and concentrated in the shape-collision draws. Mid-tier and rules-based
systems fail it hard (naive's reference regex has no label logic at all).
Ranked on the strength of the critical-field probe and its zero-cost
operationalization of the reference spec's misattribution groundwork.

---

### 4.4 `vgm_vs_gross`: VGM per container is not the cargo weight

**Research basis.** VGM is submitted per container, keyed to container ID and
vessel, "not per shipment or booking" (research L762-764). Method 2 defines
VGM = Cargo Gross Weight + Container Tare Weight (L761); Method 1 weighs the
packed container whole (L750-751); the tare is a physical CSC-plate marking
(L766-771). So a VGM and a cargo gross weight are different quantities
separated by the tare, and a two-container booking carries two VGMs beside
one cargo weight. Container numbers legitimately appear at booking time only
for shipper-owned containers, which is a real booking-form field (S.O.C.,
ONE guide, L88-90; placement rule per reference spec §2.2).

**Document.** An FCL booking for two shipper-owned, already-packed
containers. The body states the cargo gross weight once, labelled, and a VGM
line per container with per-container carton counts.

```
Hi,

Please book 2 x 40' shipper-owned containers, packed and weighed, details
below. VGMs are already declared per Method 1.

Mode: FCL
...
Pieces: 405 cartons
Gross weight: 30150 kg (cargo)
Volume: 118.6 cbm
...

VGM as declared, per container:
  KGFU3054383: 18240 kg  (210 cartons)
  HCYU9988774: 15710 kg  (195 cartons)
```

**Ground truth, exactly.** One record. `gross_weight_kg = 30150` (the stated
cargo weight). `pieces = 405` (stated, and equal to the per-container carton
sum by construction). The VGM figures are a different quantity, not a second
statement of the same one, so nothing is contested: this is deliberately not
a `weight_conflict` document. The VGMs sum to 33950, outside the scorer's
0.5% tolerance by an order of magnitude, so summing them scores `wrong`. The
two aggregations run in opposite directions on purpose: per-container cartons
do sum to the truth, per-container VGMs do not. Knowing which numbers
aggregate into which field is the competence probed.

**What it tests.** Quantity-role knowledge. "Verified gross mass" contains
the words "gross mass"; the VGM table is the most structured numeric block in
the email; summing it is the locally reasonable move for a reader who does
not know a VGM includes tare.

**Correct behaviour.** One record; cargo weight in `gross_weight_kg`; carton
total in `pieces`; VGM figures nowhere (no schema slot); no
`chargeable_weight_kg` invented.

**Why a model can fail it, in tiers.** (a) Sum the VGMs into
`gross_weight_kg`: confident wrong on a critical field. (b) Emit one record
per container: the multi_shipment lesson misapplied; containers are not
shipments. (c) Park a VGM in `chargeable_weight_kg`: hallucination, the
trust metric. Failure (b) is currently under-priced because the scorer
ignores extra predicted records (§7, flagged).

**Why it is not a trick.** The SOLAS regime itself exists because the two
numbers differ (the formula on L761 is the whole point), VGM is per-container
by regulation (L762-764), and email is a real VGM submission channel (MSC
charges per-container fees for it, L773-777). The cargo weight is stated
plainly and labelled; a reader who knows what VGM is cannot get this wrong,
and a reader who does not is who the benchmark should catch.

**Ground-truth safety.** Weight and pieces are stated verbatim (no thousands
separators, matching the numeric evidence rule). No expert argues the cargo
gross weight equals the VGM sum, because the sum includes two tares by
definition (L761). Container numbers come from the reference-formats module
(fictional owner codes, valid ISO 6346 check digits, satisfying that spec's
corpus invariant that every emitted container-shaped string validates). The
tare-sized gaps (3650-3950 kg per box) are invented plausible values, not
research-pinned; nothing depends on them beyond being far outside numeric
tolerance, which any positive tare is.

**Builder sketch.**

```python
def vgm_vs_gross(self, doc_id: str) -> Document:
    r = self._base(mode="FCL")
    total = self.rng.randrange(24000, 38000, 50)
    c1 = self.rng.randrange(int(total * 0.42), int(total * 0.58), 10)
    c2 = total - c1
    t1 = self.rng.randrange(3650, 3950, 10)   # tare-sized gap; invented,
    t2 = self.rng.randrange(3650, 3950, 10)   # the email never names it
    p1 = self.rng.randint(120, 260)
    p2 = self.rng.randint(120, 260)
    r["gross_weight_kg"], r["pieces"] = float(total), p1 + p2
    r["volume_cbm"] = round(self.rng.uniform(96.0, 136.0), 1)  # 2 x 40' plausible
    box1 = make_container_number(self.rng)   # reference-formats module:
    box2 = make_container_number(self.rng)   # fictional codes, valid checksums
    body = ("Hi,\n\nPlease book 2 x 40' shipper-owned containers, packed and "
            "weighed, details below. VGMs are already declared per Method 1.\n\n"
            + self._block(r, weight_text=f"{total} kg (cargo)")
            + "\n\nVGM as declared, per container:\n"
              f"  {box1}: {c1 + t1} kg  ({p1} cartons)\n"
              f"  {box2}: {c2 + t2} kg  ({p2} cartons)\n"
            + self._sig(company=r["shipper_name"]))
    note = (f"Cargo gross weight is {total} kg. The VGM figures include "
            f"container tare (VGM = cargo + tare, SOLAS) and sum to "
            f"{c1 + t1 + c2 + t2} kg. Summing VGMs into gross_weight_kg is "
            "the failure; so is one record per container. (research "
            "L750-777)")
    return Document(doc_id, "vgm_vs_gross",
                    f"Booking {r['booking_reference']} + VGM", body,
                    [self._clean(r)], note=note)
```

`Pathology` entry:

```python
Pathology(
    "vgm_vs_gross",
    "VGM per container is not the cargo weight",
    "Whether the extractor knows a per-container VGM includes container tare "
    "and is a different quantity from the cargo gross weight stated once for "
    "the booking. VGM is per container by regulation; bookings are not.",
    "gross_weight_kg is the stated cargo weight; the carton counts sum to "
    "pieces but the VGMs sum to nothing the schema asks for. Summing VGMs "
    "into the gross weight is wrong by two container tares, and one record "
    "per container is wrong structurally.",
    probe_fields=("gross_weight_kg", "pieces"),
),
```

Test sketch:

```python
def test_vgm_sum_is_not_the_gross_weight(self):
    for d in self.by_key["vgm_vs_gross"]:
        vgms = [int(m) for m in
                re.findall(r": (\d+) kg", d.body.split("VGM as declared")[1])]
        self.assertEqual(len(vgms), 2)
        self.assertGreater(sum(vgms), d.shipments[0]["gross_weight_kg"] * 1.05)
        self.assertEqual(len(d.shipments), 1)
        self.assertNotIn("gross_weight_kg", d.contested_fields)
```

**Honest uncertainty.** The labelled "Gross weight: ... (cargo)" line means a
label-reading system, including naive and probably every frontier model,
takes the right number. Expected frontier failure is low; this is a mid-tier
discriminator and, more importantly, a permanent guard against the summing
regression, which no other pathology would catch if a future model or prompt
started aggregating tables. If everyone passes it, it cost 1/16th of the
corpus to close a real failure class for good.

---

### 4.5 `sparse_request`: two lines, mostly absence

**Research basis.** Real requests are frequently compressed single-paragraph
asks ("FCL sea freight from Ho Chi Minh / Cat Lai Port, Vietnam to Nhava
Sheva, India... ready in early August", research L135-140); mg-spl warns that
genuinely vague requests are common and realistic (L155-157); the gap
analysis names underspecification as missing negative space (Gap-12,
L1039-1047).

**Document.**

```
Subject: Quote request

Hi, could you quote LCL Singapore to Chennai? About 900 kg / 6 cbm, 24
cartons of cotton fabric rolls. Ready date TBC.

Thanks,
Priya Nair
Tamarind Textiles Pvt Ltd
```

**Ground truth, exactly.** Non-null: `mode=LCL`, `origin_location=SGSIN`,
`destination_location=INMAA`, `pieces=24`, `gross_weight_kg=900`,
`volume_cbm=6`, `commodity_description="cotton fabric rolls"`,
`packaging_type="cartons"`. Everything else null, including
`cargo_ready_date` ("TBC" is not a date). `shipper_name` goes into
`contested_fields`: the signature company is presumptively the shipper but
the email never says so, and both extracting it and abstaining are defensible
readings; per the benchmark's own rule that means excluded, not scored either
way. The contested field is not the probe, so §1b is respected. Origin and
destination draw only from cities whose sea and air LOCODEs coincide
(singapore, chennai, hamburg and the other single-LOCODE cities), so the
derivation is mode-independent and this pathology does not re-test
ambiguous_port through a side door.

**What it tests.** Abstention discipline at scale. Roughly 26 of 35 fields
are legitimately absent on a document that feels like a failed extraction if
you return that many nulls, and the stated values live in prose with no
labels. The probe is distributed: leave the nulls alone, and pull the stated
handful out of a sentence.

**Correct behaviour.** Extract the stated fields from prose; null everything
else; no date coerced from "TBC"; no booleans asserted from silence; no
country codes inferred from company suffixes.

**Why models fail it.** The archived run names the exact behaviour: Haiku's
hallucinations are dominated by booleans asserted from silence
(temperature_controlled 86, insurance_required 64, pickup/delivery 42 each)
plus inferred country codes. This document is maximal surface for all of
them, concentrated where the hallucination-rate denominator can see it.

**Why it is not a trick.** Real inbound mail looks exactly like this
(L135-140, L155-157). There is no trap value, only absence, and the correct
behaviour is the benchmark's founding rule applied at realistic scale
instead of one field at a time.

**Coordination with the texture spec.** The texture spec's `one_liner` layout
(clean docs, ~12% weight) is this document's cousin, folded into the clean
row. This pathology is the same realism promoted to a named, reported-by-
cause row with maximal absence and its own builder-owned wording; the
texture layer does not restyle it (like one_liner, it owns its own minimal
prose). Whether clean keeps its one_liner share afterwards is the texture
owner's call; both can coexist, since the corpus is supposed to contain a
spectrum of vague mail. This spec's only requirement: the two must not
diverge on ground-truth policy (truth follows text, unstated means null),
which both already state.

**Builder sketch.**

```python
SPARSE_CITIES = ("singapore", "chennai", "hamburg", "rotterdam", "busan")
# all have sea LOCODE == air LOCODE in the fixed reference table

def sparse_request(self, doc_id: str) -> Document:
    r = _blank_record()
    o_key, d_key = self.rng.sample(list(self.SPARSE_CITIES), 2)
    commodity = self.rng.choice([c for c, v in COMMODITIES.items() if not v[1]])
    company, _cc = self.rng.choice(COMPANIES)
    w = self.rng.randrange(300, 2400, 50)
    v = self.rng.randrange(2, 14)
    p = self.rng.randint(6, 60)
    r.update(mode="LCL",
             origin_location=self._locode(o_key, "LCL"),
             destination_location=self._locode(d_key, "LCL"),
             pieces=p, gross_weight_kg=float(w), volume_cbm=float(v),
             commodity_description=commodity, packaging_type="cartons")
    o_city, d_city = LOCATIONS[o_key][3], LOCATIONS[d_key][3]
    body = (f"Hi, could you quote LCL {o_city} to {d_city}? About {w} kg / "
            f"{v} cbm, {p} cartons of {commodity}. Ready date TBC."
            f"\n\nThanks,\n{self._person()}\n{company}")
    note = ("A realistic underspecified request. Eight fields are stated in "
            "prose; everything else is legitimately absent and the correct "
            "extraction is null, including cargo_ready_date (TBC is not a "
            "date). shipper_name is contested: the signature company is "
            "presumptively but never stated to be the shipper. (research "
            "L135-140, L155-157, L1039-1047)")
    return Document(doc_id, "sparse_request", "Quote request", body,
                    [r], contested_fields=["shipper_name"], note=note)
```

`Pathology` entry:

```python
Pathology(
    "sparse_request",
    "Two-line request, mostly absence",
    "Whether abstention discipline survives scale. A realistic vague request "
    "states eight fields in unlabelled prose and nothing else; roughly 26 "
    "fields are legitimately absent on a document that feels like a failed "
    "extraction if you return that many nulls.",
    "Extract the stated handful from prose, null the rest. TBC is not a "
    "date, a destination is not a consignee country, and silence is not a "
    "boolean.",
    probe_fields=(),  # distributed; read the hallucination rate
),
```

Test sketch:

```python
def test_sparse_request_is_mostly_null(self):
    for d in self.by_key["sparse_request"]:
        rec = d.shipments[0]
        stated = [k for k, val in rec.items() if val is not None]
        self.assertLessEqual(len(stated), 8)
        self.assertIsNone(rec["cargo_ready_date"])
        self.assertIn("TBC", d.body)
        self.assertIn("shipper_name", d.contested_fields)
```

**Honest uncertainty, stated as a feature.** This will not fail Opus: its
hallucination rate is 0.0% and abstention is prompt-covered. It is included
because the trust metric needs denominator mass (thirteen sparse documents
multiply the legitimately-absent field count where today only template
coincidence provides it), because it amplifies the one axis where the tiers
already separate cleanly (4.4% / ~0.7% / 0.0%), and because the empty
extractor's strong showing here is honest: on real vague mail, abstention is
usually right. Rank it last on frontier discrimination and first on the
trust metric.

---

## 5. Killed ideas, with reasons

**KILLED: `lane_conditional_missing` (US-origin booking missing its AES
ITN).** The lane-conditionality finding is real and well-sourced (AES ITN
only for US origin, CERS for Canada, TAX IDs for Mexico: ONE's guide,
research L86-89, L101-104, Gap-9 L1012-1017). It does not survive contact
with the extraction contract. The correct extractor output for an absent ITN
is null whether or not the lane makes the field mandatory; mandatory-ness
changes what a downstream completeness validator should flag, not what the
extractor should emit. Adding an `aes_itn` field would make US-origin
documents score a trivial `abstained_ok` and every other document a
trivially-null field: corpus without signal, and the exact speculative-field
mistake v0.2 paid to fix. As an extraction pathology it is missing_critical
in a customs costume. The finding is salvaged where it does carry extraction
signal: the ITN rides in `reference_soup` as an authentically-labelled,
temporally-scoped decoy. If FreightBench ever adds a per-document
actionability output ("booking not actionable: reasons"), this returns as
the first validation pathology; that is a benchmark-contract change, out of
v0.3 scope.

**KILLED: `stale_quoted_rate` (expired quote in a forwarded thread).** The
distinctive part, staleness, has no schema slot: no rate field, no validity
field, and adding them drags the benchmark into quoting workflow, a
different document class with its own lifecycle. What remains after
de-staling ("a freight rate is present; `declared_value` must stay null and
`currency` may take the quoted amount's currency") is a number-role probe
that `vgm_vs_gross` and `reference_soup` already cover on higher-stakes
fields, and the archived run says frontier models do not stuff stray numbers
into `declared_value` (Opus hallucinations: zero). Killed rather than built
thin. Salvage note for the texture owners: a rate line in a quoted thread
("USD 1850/40HC all-in, offer valid to 28 Feb") is good distractor texture,
and if it ever renders, `currency="USD"` becomes evidenced truth under the
schema's own description, so place it deliberately or not at all.

**KILLED: `cross_document_mismatch` (invoice says 12 cartons, packing list
says 11).** The research proposes it directly (L594-604) and it is real. But
its probe is definitionally a two-sources-one-quantity conflict, so the
truth is unassertable, the probe lands in `contested_fields`, and per §1b
the pathology would measure only its template fields, exactly like
weight_conflict does today. Until the scorer grows the conflict-detection
check its own comment promises, every conflict-family pathology added is
corpus without a scored probe. Revisit the whole family (body-vs-attachment,
invoice-vs-packing-list, house-vs-master consistency per L530-537) together
with that scorer change, as one workstream.

**KILLED: `malformed_reference` (AWB with an impossible check digit).** The
reference spec already killed this on its side (§4 there) and this spec
concurs on the pathology side: a reference is a label, not a claim about
the world, so the correct extraction of a malformed reference is the
malformed string verbatim, which every extractor produces by default. No
distinct correct behaviour, therefore not a pathology. The check-digit
arithmetic earns its keep in the generator's own tests (research L431-437),
which is where the reference spec put it.

**KILLED: `pieces_nesting` ("14 pallets (each 48 cartons)": is pieces 14 or
672?).** Tempting and extremely real, but it fails the contested rule from
the wrong side: freight practice genuinely splits on whether piece count
means handling units or inner cartons (the AWB world even keeps SLAC,
"shipper's load and count", as a separate field for the inner number,
research L375-379). Reasonable professionals disagree, so the truth is not
assertable, so the probe would have to be contested, so it measures nothing.
This is the airport-gateway defect's shape wearing a cargo label; killing it
here is the §1c fairness rule doing its job.

**KILLED: `ghost_second_shipment` (a mentioned-but-unbookable balance, "the
remaining 400 units follow in April", must not become a second record).**
Real intake failure, structural probe, and the natural complement to
multi_shipment. Unbuildable today for a scoring reason: `score_corpus`
silently ignores extra predicted records, so the failure it exists to catch
(emitting the phantom second record) scores identically to the correct
behaviour. Flagged in §7 for the scorer owner; build it the release after
extra records are priced.

**KILLED: assorted no-slot compliance probes.** The unmonitored
"24-hour" emergency number (L733-740), the ocean-only container-packing
certificate absence (L673-684), buyer-vs-consignee separation (L569-580),
and the FHL/FZB naming trap (L856-863) are all real findings with no schema
slot and no extraction-shaped failure; they are validation, coverage, or
EDI-world concerns. No pathology should exist to justify a field, per the
v0.2 lesson.

**ABSORBED, not killed: `dg_misclassified` as a standalone pathology.** An
earlier sketch of this spec deferred "sender states UN3480 on goods the
description says are installed in equipment" pending a prompt-contract fix.
The §3 revision absorbs it: variant A is exactly this probe, and the
companion schema wording ("follows the commodity, not a code the sender may
have stated") is the contract fix, landing together. A separate slot would
double-count one failure mode.

---

## 6. Ranking by expected discriminating power

Against a model that currently scores ~100%: expected probe-field failure at
the frontier, then at mid-tier, with the mechanism named. Honesty column
states the case against each rank.

| Rank | Pathology | Mechanism | Frontier bite | Case against |
|---|---|---|---|---|
| 1 | `booking_amendment` | Per-field thread state; the corpus's own newest-wins training plus real-mail priors push toward dropping the quoted base. Failure mass is a dozen mostly-critical fields at once, and no prompt rule can perform the merge. | Moderate, and the largest per-failure cost of any candidate | The "everything else stands" sentence is explicit; a careful frontier read passes. Even then it permanently retires the ignore-quotes shortcut |
| 2 | `dg_undeclared` (revised) | Knowledge scope: the only printed UN number is the wrong one, and passing requires knowing installed-in-equipment means UN3481 and that the SOC provision is UN3480-scoped. Prompt v1 evidence shows frontier deference to confident sender claims (18/18) | Moderate on `un_number`; low on the boolean, which prompt v2 already covers | If frontier models simply know the regulation, the probe collapses to mid-tier separation. It still deletes a documented strawman, which the benchmark's credibility needs |
| 3 | `conditional_acceptance` | Field ownership vs recency and paraphrase; the identical-gloss/varied-status design blocks shape learning | Low-to-moderate; the field description necessarily coaches ownership | Weak models may skip the new field entirely, converting the expensive failure into cheap `missed`. Opens the confirmation document class either way |
| 4 | `reference_soup` | Role and temporal scoping under decoy pressure with shape deliberately uninformative | Low-to-moderate, concentrated in shape-collision draws | Labels resolve everything for a careful reader. Probes a critical field and operationalizes the reference spec's distractor design at zero schema cost |
| 5 | `vgm_vs_gross` | Quantity-role knowledge (VGM includes tare); three failure tiers, all expensive | Low; the labelled cargo line is probably taken by everyone | Its value is the permanent regression guard on aggregation behaviour, and mid-tier separation |
| 6 | `sparse_request` | Abstention at scale; amplifies the hallucination denominator | Effectively zero (Opus hallucinates nothing) | Included for the trust metric and tier separation, stated openly; last on the headline, first on the number that decides unattended trust |

A calibration note against overclaiming: if the frontier models pass all six,
the corpus is still better than today's, because the mid-tier separation
becomes interpretable by cause (which knob failed, at what cost) instead of
flat, and the two shortcut heuristics (ignore quotes, newest wins) are
retired permanently. But the honest expectation is that ranks 1-2 produce
real frontier errors, 3-4 produce occasional ones, and 5-6 do not. The
`probe_fields` reporting (§2) is what makes even occasional frontier errors
visible instead of vanishing 14:1 into template averages.

---

## 7. Compatibility, coordination, and companion changes

- **Pathology count 11 → 16.** Round-robin at n=200 gives 12-13 documents per
  pathology. Acceptable without weighted sampling.
- **Corpus bytes change; scores are not comparable across versions.** Same
  README versioning language as v0.1 → v0.2. All new builders draw
  exclusively from `self.rng` in fixed order; pure stdlib; determinism tests
  unaffected.
- **Schema deltas, complete list.** One new field (`booking_status`, §4.2,
  `exact`, standard, inserted in the identity group) and two description
  rewrites (`dangerous_goods`, `un_number`, §3). One new `COMMODITIES` entry
  (§3). The empty-extractor and naive reference numbers regenerate for the
  README table.
- **PROMPT_VERSION 2 → 3.** The prompt embeds schema descriptions via
  `_field_lines()`, so the §3 and §4.2 schema changes change the canonical
  prompt text. Deliberately, nothing else is added to the prompt: no
  amendment rule, no status-ownership rule, no lithium provisions. The §1a
  design rule is that the new difficulty must survive the contract as
  stated; adding per-pathology coaching would repeat the v0.2 saturation
  mechanism at the next version boundary.
- **Reference-formats module (peer spec).** `reference_soup`,
  `conditional_acceptance`, and `vgm_vs_gross` draw their reference and
  container strings from `freightbench/reference_formats.py` once it lands,
  honoring its Rule 1 (no truth/distractor string containment) and Rule 2
  (distractors always typed by label as something the schema does not ask
  for). `vgm_vs_gross` satisfies its corpus invariant that every
  container-shaped string validates under ISO 6346. Sketches above show
  invented placeholders where the module's makers slot in.
- **Texture spec coordination.** The five new pathologies need rows in that
  spec's §2.4 constraint matrix. Proposed constraints, for the texture owner
  to adopt: `booking_amendment` (newest-on-top; the amendment sentence and
  the full quoted block are payload; subject stays in the RE: family; quote
  markers may draw from the §3.3 pool), `conditional_acceptance` (the quoted
  carrier block with its verbatim `Status:` line is payload and stays
  visually distinct; the gloss sentence is payload; subject RE: family),
  `reference_soup` (the labelled reference list is payload; the subject must
  carry no reference; the block omits the reference line), `vgm_vs_gross`
  (the labelled cargo-weight line with its "(cargo)" qualifier and the
  per-container VGM lines are payload), `sparse_request` (owns its own
  minimal prose entirely, like one_liner). The revised dg_undeclared keeps
  the literal substring "No dangerous goods", so the texture spec's §2.4
  note and the test grep survive; its claim paragraphs are payload,
  verbatim.
- **`_block()` change.** `omit` must support `"customer_reference"` (§4.3).
- **naive.py stays frozen** (texture spec §7.3), and the expected effects are
  informative: it keeps `dangerous_goods=false` on the revised dg documents
  (its "no dangerous goods" keyword branch fires first, still wrong, as
  designed), reads the quoted stale consignee in `booking_amendment` (first
  `^Consignee:` match, wrong, correctly priced), has no `booking_status`
  extractor (missed), and its label-reading takes the right weight in
  `vgm_vs_gross`. Net: naive drops; the CI bracket (above empty, below 0.95
  critical) holds with margin, but re-verify after the reference-format
  change lands since that also moves naive.
- **Scorer gaps observed, not fixed here, flagged for the scorer owner.**
  (a) The "conflict-detection check" promised by `score.py`'s comment does
  not exist, which is why weight_conflict measures only template fields and
  why the conflict family stays frozen (§5). (b) `score_corpus` silently
  ignores extra predicted records, so per-container splits (§4.4 failure b)
  and phantom records (§5, ghost_second_shipment) are under-priced; a
  records-count outcome would price both and unlock a killed pathology.
  (c) The `probe_fields` reporting view (§2) needs a small `Report` helper.
- **Tests.** Replacements and additions sketched inline (§3, §4.1-4.5).
  `TestTruthIsEvidenced` passes for every builder as argued per-entry: all
  stated truths render verbatim without thousands separators; derived fields
  (`dangerous_goods`, `un_number`, LOCODEs) are already whitelisted, which
  is what lets variant A's printed UN3480 decoy coexist with UN3481 truth;
  `booking_status` uses space-separated enum values so the substring check
  holds; contested fields (`shipper_name` in sparse_request only) are
  skipped by the invariant. `test_every_pathology_represented` passes
  automatically since it derives from `PATHOLOGIES`.

---

## 8. Research citations used (all `research/freight-document-research.md`)

| Claim | Lines |
|---|---|
| UN3480 standalone vs UN3481 in/with equipment; lithium marks | 692-706, 717-718 |
| "No DGD required" is a narrow real exception, not a blanket rule | 703-706 |
| Section II caps a consignment at one package (PI965/PI968) | 719-720 |
| Carriers refuse Section II / shift to full IA/IB | 720-722 |
| ≤30% SOC cap is a UN3480 air rule, not formally UN3481 | 722-724 |
| Verbatim realistic wrong-exemption claims; the SOC/UN3481 conflation | 725-731 |
| dg_undeclared strawman critique; "routinely get wrong in practice" | 969-982 |
| Booking confirmation status three-valued, codes AJ/AP/CA | 217-233 |
| Forwarder confirmation restates the carrier's booking number | 244-250 |
| "Thank you page" is not the confirmation; receipt vs confirmed gap | 252-257, 103-104 |
| No confirmation-side document class exists in the generator (gap) | 984-990 |
| VGM Method 1 / Method 2 definitions | 750-753 |
| VGM = cargo gross + container tare (Method 2 formula) | 761 |
| VGM submitted per container, not per booking | 762-764 |
| Tare from the CSC plate marking | 766-771 |
| Email as a real VGM channel (per-container fee) | 773-777 |
| Five simultaneous reference numbers per booking (ONE guide) | 95-104 |
| Lane-conditional customs fields (AES ITN, CERS, TAX IDs) | 86-89, 101-104, 1012-1017 |
| S.O.C. (shipper-owned container) as a real booking-form field | 88-90 |
| Real carrier confirmation reference exemplar BHK51332862 | 240-242 |
| Threads with amendments; 40+ messages per shipment | 111-117 |
| MSC amendment reason codes | 349-355 |
| Compressed one-paragraph real requests; vague requests realistic | 135-140, 155-157 |
| Underspecification and thread density as missing negative space | 1039-1047 |
| Cross-document totals must match (killed idea) | 594-604 |
| House/Master B/L field-identity rule (deferred conflict family) | 530-537 |
| AWB mod-7 check digit (killed idea; generator-side tests) | 431-437 |
| 24-hour emergency number requirement (killed idea) | 733-740 |
| Ocean container-packing certificate, no air analog (killed idea) | 673-684 |
| Buyer and consignee are separate roles (killed idea) | 569-580 |
| FHL/FZB naming trap (killed idea) | 856-863 |
| SLAC as a separate inner-count field (pieces_nesting kill) | 375-379 |
