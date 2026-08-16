# FreightBench v0.3 spec: email texture and register realism

Scope: how generated emails *read* and how they are *shaped*. Registers, body layouts,
subject lines, signatures, disclaimers, thread quoting, CC lists.

Out of scope (owned by other v0.3 specs): new schema fields, new or upgraded
pathologies (including the `dg_undeclared` sentence rewrite), reference-number
formats (`BK-#####` stays as-is here), lane-conditional logic, non-email document
types.

Numbering note: the task brief for this spec cited "gap-analysis finding #5
(template rigidity / register variance)". In the current
`research/freight-document-research.md` that content is **finding #1** ("One rigid
template shape vs. enormous real structural variance"); finding #5 is the
`dg_undeclared` strawman, which belongs to the pathology spec. All citations below
use the file's actual numbering.

---

## 1. The problem, measured

The v0.2 model run (`research/model-run-2026-08-16/results.md`) shows the naive
regex extractor beating Sonnet and Opus on exactly the pathologies where the
template is most rigid:

| Pathology | naive | sonnet | opus |
|---|---|---|---|
| agent_not_shipper | 96% | 90% | 91% |
| weight_conflict | 96% | 90% | 91% |
| forwarded_thread | 96% | 89% | 90% |

The README already calls this what it is: "The v0.1 templates are regex-friendly,
which flatters rules. That is a limitation of this corpus, not a finding about
models."

The mechanism is fully visible in the code. Every document is built from one shape:

- one greeting from {"Hi,", "Hello,", "Hi team,", "Dear colleagues,"},
- one intro sentence,
- `_block()`: a fixed-order `Field: value` list (`Mode:` / `Origin:` /
  `Destination:` / `Shipper:` / ... / `Our reference:`),
- `_sig()`: literally `Best regards,\n{name}\n{company}`.

And `naive.py` wins because it was written against exactly that shape: line-anchored
`^Label:\s*(.+)$` regexes for eleven labels, `^Gross weight:` and `^Pieces:`
patterns, `BK-\d{5}` anywhere, and the keyword "no dangerous goods". When 100% of
documents carry the labels, the label-reader is near-perfect on every pathology
whose *trap* does not live in the labels (agent_not_shipper's trap targets
sender-vs-shipper reasoning; the labels hand naive the answer for free).

The research says real booking mail does not look like this. Finding #1 of the gap
analysis, grounded in four independent sources:

- formal, ESL-influenced "Respected Sir/ Madam... at your earliest convenience"
  (emailsinenglish.com, research §2 / cluster-A source 2.3),
- casual "Dear Freight Team," with "Thanks," / "Regards," sign-offs
  (Freightamigo worked samples, research §2 / cluster-A source 2.2),
- terse single-paragraph asks: "FCL sea freight from Ho Chi Minh / Cat Lai Port,
  Vietnam to Nhava Sheva, India. 2 x 40'HC containers, general cargo, ready in
  early August" (mg-spl.com, research §1-2 / cluster-A sources 1.5, 2.1),
- checklists "copy and paste[d]... straight onto the email" with uneven formatting
  (Freightos, research §2 / cluster-A source 2.5),
- "RFQ - " subject prefixes carrying compressed shipment parameters
  (Freightamigo, research §2 / cluster-A source 2.2).

The fix is not to delete the labelled block. Real mail includes pasted checklists,
so the block stays as one shape among several. The fix is that no single shape may
be universal, so nothing regex-shaped can be *assumed* by an extractor.

---

## 2. Design: texture as an axis orthogonal to pathology

Every pathology keeps its semantic payload exactly as today (the conflicting
attachment weight, the quoted stale thread, the trailing correction, the DG denial
sentence). What changes is the *skin* around and through that payload. Each
document draws one `Texture` from the seeded RNG:

```python
from dataclasses import dataclass

REGISTERS = ("formal_esl", "terse_ops", "casual_internal", "newbie")
LAYOUTS   = ("block", "prose", "bullets", "table")   # + "one_liner", clean-only

@dataclass(frozen=True)
class Texture:
    register: str        # voice: greeting, connective phrasing, sign-off
    layout: str          # how the field values are physically arranged
    subject_style: str   # see section 5
    sig_style: str       # "full" | "name_company" | "mobile"
    footer: bool         # confidentiality disclaimer paragraph
    header_block: bool   # pasted To:/From:/Cc:/Subject: preamble
    cc_count: int        # 0..2 names in the Cc line (only if header_block)
```

Register and layout are deliberately independent draws: a formal-ESL sender can
paste a table, a casual internal sender can write prose. The four registers and
five layouts give the corpus 4x5 surface families before furniture variation,
against v0.2's exactly one.

### 2.1 The four registers, concretely

**formal_esl** (source: emailsinenglish.com template, cluster-A 2.3; its note that
"Dear Sir/Madam" persists in shipping specifically even where general
business-English guides call it outdated)
- Greetings: "Respected Sir/ Madam,", "Dear Sir/Madam,", "Dear Sirs,"
- Connectives: "We kindly request you to...", "at your earliest convenience",
  "We shall be grateful for your confirmation."
- Sign-offs: "Thank you,", "Sincerely,", "Yours faithfully," (last one:
  assumption, see section 8)

**terse_ops** (source: mg-spl's compressed one-paragraph example, cluster-A 1.5;
Freightos's pasted-checklist note)
- Greeting: none, or "Hi -"
- Body compressed to shorthand: "LCL ex Shanghai to Rotterdam. 12 pallets,
  4550 kg / 18.75 cbm, cotton fabric rolls. Ready 14 Mar 2026. CIF, freight
  prepaid. Ref PO458123."
- Sign-offs: "Rgds", "Thx", or bare name (specific tokens are an assumption;
  the compression itself is sourced)

**casual_internal** (source: Freightamigo's two worked RFQ samples, cluster-A 2.2)
- Greetings: "Dear Freight Team,", "Hi team,", "Hi both,"
- Connectives: "Could you quote the below?", "Please confirm receipt and provide
  an itemized quote with transit times by EOD." (near-verbatim CTA from the
  source)
- Sign-offs: "Thanks,", "Regards,"

**newbie / first-time shipper** (source: emailsinenglish.com opening-line pattern
"We have learned about your company's... services, and I'm writing this email to
request a quotation for..."; mg-spl's warning that genuinely vague requests are
realistic)
- Over-explains: introduces their company, states this is their first export,
  asks a basic question ("do we need any special paperwork for this?").
- Values arrive scattered through prose rather than grouped.
- Sign-off: "Thank you very much in advance," (assumption)

### 2.2 The five layouts, concretely

**block** (v0.2's `_block()`, kept at reduced share). Real support: Freightos's
"copy and paste your prep list straight onto the email" (cluster-A 2.5). Two
sub-variants to avoid a single fingerprint: the current label set, and a
label-synonym set ("Gross wt:", "Cargo ready date:", "Ex:", "To:", "Ref:").

**prose**. Values embedded in running sentences (mg-spl example shape). See
section 4 for the evidence-safe formatting contract, and section 6 for a full
code sketch.

**bullets**. "- " or "* " prefixed lines with drawn label synonyms (Freightamigo
explicitly recommends "bullet points or short tables" over flat prose, cluster-A
2.2). Note the bullet prefix alone already defeats `naive.py`'s `^Label:` anchor
even when the label word is unchanged.

**table**. A pasted plain-text mini-table for the cargo numbers, with lane and
parties in short lines above it (Freightamigo "short tables", cluster-A 2.2):

```
Route: Shanghai -> Rotterdam (LCL), CIF, freight prepaid
Shipper: Vantage Components BV / Consignee: Kestrel Industrial Ltd

pcs   packaging   gross wt (kg)   volume (cbm)
12    pallets     4550            18.75

Cargo ready 2026-03-14. Ref PO458123.
```

**one_liner** (clean pathology only, roughly 1 in 8 clean docs). A genuinely
underspecified quote ask, directly modeled on mg-spl's "Please quote Singapore to
India" realism note and gap finding #12:

> "Hi, can you give us a price for air freight Shanghai to Rotterdam, about
> 800 kg of consumer electronics? Ready end of the month. Thanks, Marta"

Ground truth for a one-liner nulls every field the text does not state (pieces,
volume, incoterm, references, consignee, exact ready date). This uses the
mechanism `_base()` already has for never-rendered fields and `multi_shipment`
already has for `booking_reference`: the truth follows the rendered text, so
TruthIsEvidenced passes by construction. "About 800 kg" is rendered with the
exact stored number ("about" is allowed; rounding the rendered number is not,
see section 4). A vague ready window ("end of the month") means
`cargo_ready_date = None`. This raises the empty-extractor floor slightly on
clean docs and that is honest: abstention really is the right answer more often
on real vague mail.

### 2.3 Layout and register weights

Drawn with `self.rng.choices(population, weights=...)` (stdlib, deterministic
under a seeded `random.Random`).

| Draw | Weights |
|---|---|
| layout (clean) | block .30, prose .25, bullets .20, table .13, one_liner .12 |
| layout (all other pathologies) | block .35, prose .25, bullets .25, table .15 |
| register | terse_ops .30, casual_internal .30, formal_esl .25, newbie .15 |
| sig_style | full .40, name_company .40, mobile .20 (mobile only when register is terse_ops or casual_internal) |
| footer | .35 true |
| header_block | .20 true |
| cc_count | 0 with .55, 1 with .30, 2 with .15 (only when header_block) |

Block keeps the plurality share on purpose: labelled checklists are real, and the
naive baseline should keep partial credit rather than collapse to the empty
floor. The point is that a label-reader can no longer assume the labels exist.

### 2.4 Pathology x texture compatibility

Payload sentences are owned by the pathology builders and are not texture. The
matrix below is what the texture layer must respect; everything not listed is
unconstrained.

| Pathology | Constraints |
|---|---|
| clean | none; only pathology allowed the one_liner layout |
| ambiguous_port | origin must render as the bare city word ("Shanghai"), never a LOCODE, in every layout; the "please confirm the terminal" ask stays |
| weight_conflict | body weight in any layout; the attachment excerpt stays a visually distinct block (intro line drawn from a pool, section 3.4); attachment says "Total gross weight: {other} kg" as today |
| unit_ambiguity | weight must render with an explicit "lbs" unit in any layout; requires the one-line test amendment in section 7.1 |
| date_ambiguity | ready date renders in EU numeric format and the day>12 anchor sentence stays; subject_style must not carry any date (it would leak an unambiguous format) |
| agent_not_shipper | sender company is the agent (signature and, when header_block is drawn, the From: domain); shipper full name must appear in the body; on-behalf phrasing drawn from a pool of 3 (section 3.5) |
| multi_shipment | two clearly delimited segments; separator drawn from a pool ("=== SHIPMENT 1 ===", "Shipment 1:", "1)"); layouts: block, bullets, prose ("First shipment: ... Second shipment: ...") |
| forwarded_thread | newest-on-top; quoting marker drawn from the 3 styles in section 3.3; subject_style forced to the RE:/FW: family |
| missing_critical | renderers receive `omit=("incoterm",)` and must not mention terms in any phrasing; the existing test's `"Incoterm:" not in body` stays true trivially |
| dg_undeclared | the sentence "No dangerous goods declaration needed for this one." stays verbatim (the rewrite is the pathology spec's job; `test_dg_inferred_despite_sender_denial` greps the exact casing "No dangerous goods") |
| trailing_correction | correction sentence drawn from a pool of 3, every variant containing both the word "correction" and the literal "should be {int} kg" (both are grepped by `test_trailing_correction_truth_is_the_correction`) |

---

## 3. Email furniture

### 3.1 Signature blocks

v0.2: name + company, nothing else. Research basis: gap finding #11 states every
rate-request template found asks the requester to include contact details, but
also states a verified real signature block was *not* found. So signatures get
richer but stay conservative, and the whole feature is flagged medium-confidence
(section 8).

```
Best regards,
Priya Nair
Export Manager
Blue Harbour Foods Pte Ltd
+65 6xxx xxxx
```

- Titles drawn from a small pool ("Logistics Coordinator", "Export Manager",
  "Shipping Executive", "Supply Chain Officer"). Assumption: plausible, unsourced.
- Phone prefixes mapped from the company's ISO-2 country already present in
  `COMPANIES` (NL +31, GB +44, SG +65, DE +49, US +1, IN +91), digits drawn from
  the RNG. Entirely invented, consistent with the repo's "entirely invented"
  data stance.
- `sig_style="mobile"` replaces the block with `{name}\n\nSent from my iPhone`.
  This is a pure assumption: the research contains no source for mobile
  signatures. It is kept because it is a low-risk, universally recognizable email
  convention, at low weight, and it is listed in the assumptions register.

### 3.2 Confidentiality footer

Applied after the signature when `footer` is true:

> "This email and any attachments are intended only for the use of the individual
> or entity to which they are addressed and may contain confidential information.
> If you have received this email in error, please notify the sender."

Source: the first sentence is the generic pattern documented in cluster-A source
3.8, which explicitly could not confirm it on a named forwarder's own mail. The
second sentence is an assumption. Both flagged in section 8. The footer must be
appended *after* the signature so it reads as boilerplate, not content, and it
must never contain shipment values (it would otherwise create accidental
evidence).

### 3.3 Thread quoting styles (forwarded_thread, and RE: subjects generally)

Three markers, drawn per-document:

1. `-----Original Message-----\nFrom: planning\nSent: {date}\nTo: bookings\nSubject: {inner subject}` (v0.1's own established convention, plus Sent:/To: lines; the To/From/Subject header shape is supported by emailsinenglish's explicit To/Bcc/Cc/From/Subject block, cluster-A 2.3)
2. `On {long date}, {person} wrote:` followed by the quoted block with every line prefixed `> ` (assumption: universal mail-client convention, not in the research)
3. `________________________________\nFrom: {person}\nSubject: {inner subject}` (Outlook-web style; assumption)

The stale values live only inside the quoted block, as today. Note for style 2:
`> `-prefixing the quoted lines also defeats `^Label:` regexes inside the quote,
which is realistic and desirable, and the truth (newest) values are all rendered
in the top message, so evidence is unaffected.

### 3.4 Attachment-excerpt intros (weight_conflict)

Pool of 3, all keeping the excerpt visually separate from the body:

- `--- attached packing list (transcribed) ---` (v0.1 convention)
- `Packing list (attached) shows:`
- `From the attached PL:`

The packing-list-as-attachment device itself is supported by research §7
(invoice/packing-list totals must match; packing list is a standard companion
document).

### 3.5 On-behalf phrasing (agent_not_shipper)

Pool of 3, each unambiguous about the role split and each containing the
shipper's full stored name somewhere in the body:

- "On behalf of our client we would like to book the following." (v0.1; shipper named in the rendered values)
- "We act as forwarding agents for {shipper_name} and would like to place the booking below."
- "Our principal {shipper_name} has asked us to arrange the following shipment."

The trap deepens when `header_block` is drawn: the From: line carries the agent's
invented domain while the body names the shipper.

### 3.6 Header block and CC lists

When `header_block` is true, the body opens with a pasted header (source:
emailsinenglish shows To/Bcc/Cc/From/Subject as part of "the email", cluster-A
2.3):

```
From: Marta Vermeer <m.vermeer@vantage-components.com>
To: bookings@halcyonfreight.com
Cc: Samir Haddad <s.haddad@vantage-components.com>
Subject: RFQ - Ocean LCL Quote: 18.75 cbm Shanghai to Rotterdam
```

Domains are deterministic slugs of the invented company names (lowercase,
non-alphanumeric collapsed to "-", `.com`). All invented; no real domains.
The `Subject:` line inside the header must equal the document's actual subject
(one more place evidence can live, and an inconsistency there would be an
unintended pathology).

---

## 4. The evidence contract: keeping TruthIsEvidenced green in prose

`tests/test_freightbench.py::TestTruthIsEvidenced` checks every non-null,
non-contested, non-derived truth value against `(subject + "\n" + body).casefold()`
with these rules, which this spec treats as fixed law:

| Compare rule | What counts as evidence | Consequence for renderers |
|---|---|---|
| date | exact output of `_fmt_date(d, s)` for s in ("iso", "eu", "us", "long"), casefolded substring | prose dates must use one of the four formats verbatim. "long" is `%d %b %Y` and zero-pads the day ("05 Mar 2026"). "5 March 2026" would FAIL. Renderers call `_fmt_date`, never hand-format |
| numeric | `f"{v:g}"`, or `str(int(v))` when integral, or the lbs form for gross_weight_kg, as a plain substring | NO thousands separators ever ("4,550" fails). No rounding for display ("~4.5 t" alone fails). Weight in tonnes may only *accompany* a kg or lbs statement, never replace it |
| boolean | never evidenced (rule returns False) | non-derived boolean truths stay None, exactly as `_base()` already nulls them. Texture must not "helpfully" render pickup/insurance sentences with a non-null truth |
| everything else (exact/casefold/code) | `str(value).casefold()` as a contiguous substring | the stored string must appear intact at least once. Full company name with suffix once, shortened mentions allowed after. "PO458123" contiguous, never "PO 458123". Mode tokens "LCL"/"FCL"/"AIR" must appear literally ("less-than-container-load" alone fails). Commodity strings verbatim ("lithium-ion battery packs" cannot be reworded) |

Derived fields (`origin_location`, `destination_location`, `dangerous_goods`,
`un_number`) are exempt, so prose may and should say city names, not LOCODEs.

Two rules of construction that make compliance structural rather than hoped-for:

1. **One formatter per value type.** All renderers get values through shared
   helpers (`_wt(r)`, `_vol(r)`, `_ready(r, style)`, `_ref(r)`) that emit only
   evidence-safe forms. No renderer ever formats a truth value inline.
2. **Truth follows text, not the other way round.** When a layout chooses not to
   state a value (one_liner, terse variants with vague dates), the builder nulls
   that field in ground truth before emitting, the same way `_base()` handles
   never-rendered fields and `multi_shipment` handles `booking_reference`. A
   value is either rendered evidence-safe or nulled; there is no third state.

Worked example, prose renderer output for a clean doc, with the evidence check
annotated:

> "We need to move 12 pallets [pieces "12", packaging "pallets"] of cotton fabric
> rolls [commodity verbatim] (4550 kg [f"{v:g}"], 18.75 cbm [f"{v:g}"]) by LCL
> [mode literal] from Shanghai to Rotterdam. Shipper is Vantage Components BV
> [full name], consignee Kestrel Industrial Ltd [full name]. Cargo ready
> 14 Mar 2026 [_fmt_date long], CIF terms [incoterm literal], freight prepaid
> [freight_terms casefold]. Our reference is PO458123 [contiguous]."

Every non-null truth field is evidenced under the existing rules with zero test
changes.

Date-style guardrail: only `date_ambiguity` may render bare numeric EU or US
dates. All other pathologies draw from {"iso", "long"}, so no clean document can
accidentally become a date-ambiguity document.

Subject lines count as evidence (the test concatenates subject + body), which is
what makes reference-in-subject and RFQ-with-volume subjects legal.

---

## 5. Subject lines

v0.2 has one shape per pathology, all of the form "Booking request BK-12345".
Research-observed conventions to draw from (per-pathology constraints from 2.4
apply):

| Style | Example | Source |
|---|---|---|
| ref | `Booking request BK-48291` | v0.1 convention, kept |
| rfq | `RFQ - Ocean LCL Quote: 18.75 cbm Shanghai to Rotterdam, Ready 14 Mar 2026` / `RFQ - Air Freight Quote: 12 pallets Shanghai to Rotterdam` | Freightamigo verbatim patterns "RFQ - LTL Freight Quote: [qty] [origin] to [destination], Ready [date]" and "RFQ - Ocean LCL Quote: [CBM]...", cluster-A 2.2 |
| request_for | `Requesting Freight Quotation for cotton fabric rolls` | emailsinenglish verbatim subject pattern, cluster-A 2.3; pairs naturally with the newbie register |
| lane | `Shanghai to Rotterdam - cotton fabric rolls` | compressed-parameters convention generalized from the RFQ patterns (weak-source: marked assumption) |
| thread | `RE: booking BK-48291` / `FW: FW: booking draft` | forwarded_thread's home; RE:/FW: chaining is an assumption at the multi-prefix level, single RE: is v0.1 convention |
| useless | `booking`, `quote request`, `shipment`, `quick question` | mg-spl's vague-request realism note supports contentless asks; the specific strings are assumptions |

Interaction with evidence: several current builders evidence `booking_reference`
*only* in the subject. When a drawn subject style does not carry the reference
(rfq, request_for, lane, useless), the renderer must either state it in the body
("Our ref BK-48291" in the opening or closing line) or the builder nulls
`booking_reference` in truth. Default: state it in the body, so field coverage
does not shrink; the one_liner layout nulls it instead. Note `naive.py` greps
`BK-\d{5}` across subject+body, so the naive baseline keeps this field either
way, which is intended: the collapse should come from lost labels, not from
hiding references.

`date_ambiguity` never draws rfq-with-date (section 2.4). `forwarded_thread`
always draws thread. `multi_shipment` keeps a reference-free subject ("Two
bookings this week" family) because its truth nulls both booking references.

---

## 6. Code sketches

Pure standard library, single RNG stream, no new dependencies. Sketches show
shape and draw order; naming is final, wording pools may grow at implementation
time as long as every pool entry honors sections 2.4 and 4.

### 6.1 Texture draw (first RNG consumption of every builder)

```python
def _texture(self, pathology: str) -> Texture:
    """MUST be the first rng consumption in every builder, so the draw
    order is: texture -> base record -> pathology-specific draws."""
    if pathology == "clean":
        layout = self.rng.choices(
            ("block", "prose", "bullets", "table", "one_liner"),
            weights=(30, 25, 20, 13, 12))[0]
    else:
        layout = self.rng.choices(
            ("block", "prose", "bullets", "table"),
            weights=(35, 25, 25, 15))[0]
    register = self.rng.choices(REGISTERS, weights=(25, 30, 30, 15))[0]
    sig_style = self.rng.choices(("full", "name_company", "mobile"),
                                 weights=(40, 40, 20))[0]
    if sig_style == "mobile" and register in ("formal_esl", "newbie"):
        sig_style = "name_company"
    header = self.rng.random() < 0.20
    return Texture(
        register=register,
        layout=layout,
        subject_style=self._subject_style(pathology),
        sig_style=sig_style,
        footer=self.rng.random() < 0.35,
        header_block=header,
        cc_count=self.rng.choices((0, 1, 2), weights=(55, 30, 15))[0] if header else 0,
    )
```

### 6.2 Evidence-safe value helpers (the only formatters renderers may use)

```python
def _wt_text(self, r, unit: str = "kg") -> str:
    v = r["gross_weight_kg"]
    if unit == "lbs":
        return f"{round(v * 2.20462, 1):g} lbs"   # matches the test's lbs candidate
    return f"{int(v)} kg"                          # integral, no separators

def _vol_text(self, r) -> str:
    return f"{r['volume_cbm']:g} cbm"              # matches the numeric candidate

def _ready_text(self, r, style: str) -> str:
    from datetime import date as _d
    return _fmt_date(_d.fromisoformat(r["cargo_ready_date"]), style)
    # style is drawn from ("iso", "long") everywhere except date_ambiguity
```

### 6.3 Layout renderers behind one dispatcher

All renderers accept the same kwargs `_block()` already takes
(`weight_text`, `ready_text`, `origin_text`, `omit`), so pathology builders
change one call, not their logic:

```python
def _render(self, r, tex: Texture, **kw) -> str:
    return {
        "block":     self._block,        # v0.2 renderer, unchanged
        "block_syn": self._block_syn,    # same shape, synonym labels
        "prose":     self._prose,
        "bullets":   self._bullets,
        "table":     self._table,
    }[tex.layout if tex.layout != "block"
      else self.rng.choice(("block", "block_syn"))](r, **kw)
```

Prose renderer (register-flavored connectives, values via helpers only):

```python
def _prose(self, r, *, weight_text=None, ready_text=None,
           origin_text=None, omit=()) -> str:
    o = origin_text or LOCATIONS[r["_o"]][3]
    d = LOCATIONS[r["_d"]][3]
    wt = weight_text or self._wt_text(r)
    parts = [
        f"We need to move {r['pieces']} {r['packaging_type']} of "
        f"{r['commodity_description']} ({wt}, {self._vol_text(r)}) "
        f"by {r['mode']} from {o} to {d}.",
        f"Shipper is {r['shipper_name']}, consignee {r['consignee_name']}.",
    ]
    tail = []
    if "cargo_ready_date" not in omit:
        tail.append(f"cargo ready {ready_text or self._ready_text(r, 'long')}")
    if "incoterm" not in omit:
        tail.append(f"{r['incoterm']} terms")
    tail.append(f"freight {r['freight_terms'].lower()}")
    parts.append(", ".join(tail).capitalize() + ".")
    parts.append(f"Our reference is {r['customer_reference']}.")
    return " ".join(parts)
```

Bullets renderer with drawn label synonyms (the label pools are per-document
draws, so no two-doc regex generalizes):

```python
_LABEL_POOLS = {
    "weight": ("Gross weight", "Gross wt", "GW", "Weight"),
    "ready":  ("Cargo ready", "Cargo ready date", "Ready", "CRD"),
    "ref":    ("Our reference", "Our ref", "Ref"),
    "vol":    ("Volume", "Vol", "CBM"),
    # mode/origin/destination/shipper/consignee/commodity/pieces/terms similar
}

def _bullets(self, r, *, weight_text=None, ready_text=None,
             origin_text=None, omit=()) -> str:
    pick = {k: self.rng.choice(v) for k, v in _LABEL_POOLS.items()}
    bullet = self.rng.choice(("- ", "* "))
    lines = [
        f"{bullet}{pick['mode']}: {r['mode']}",
        f"{bullet}{pick['origin']}: {origin_text or LOCATIONS[r['_o']][3]}",
        # ... same field order variation: shuffle a copy of the middle lines
        f"{bullet}{pick['weight']}: {weight_text or self._wt_text(r)}",
        f"{bullet}{pick['vol']}: {self._vol_text(r)}",
    ]
    ...
    return "\n".join(lines)
```

### 6.4 Furniture

```python
def _open(self, tex: Texture, r) -> str:
    head = self._header_block(tex, r) if tex.header_block else ""
    greeting = self.rng.choice(GREETINGS[tex.register])
    intro = self.rng.choice(INTROS[tex.register])
    return f"{head}{greeting}\n\n{intro}\n\n" if greeting else f"{head}{intro}\n\n"

def _sig(self, tex: Texture, name=None, company=None) -> str:
    name = name or self._person()
    closing = self.rng.choice(SIGNOFFS[tex.register])
    if tex.sig_style == "mobile":
        block = f"\n\n{closing}\n{name}\n\nSent from my iPhone"
    elif tex.sig_style == "full":
        title = self.rng.choice(TITLES)
        block = (f"\n\n{closing}\n{name}\n{title}\n{company or ''}\n"
                 f"{self._phone(company)}").rstrip()
    else:
        block = f"\n\n{closing}\n{name}\n{company or ''}".rstrip()
    if tex.footer:
        block += "\n\n" + DISCLAIMER
    return block
```

### 6.5 A builder after the change (clean, full; the diff pattern for all others)

```python
def clean(self, doc_id: str) -> Document:
    tex = self._texture("clean")            # first rng consumption
    r = self._base()
    if tex.layout == "one_liner":
        return self._clean_one_liner(doc_id, tex, r)   # nulls unstated fields
    body = (self._open(tex, r)
            + self._render(r, tex)
            + self._ref_line(tex, r)        # "" when subject carries the ref
            + self._sig(tex, company=r["shipper_name"]))
    return Document(doc_id, "clean", self._subject(tex, r), body, [self._clean(r)])
```

`agent_not_shipper` shows the pattern for payload-carrying builders: the payload
(on-behalf sentence, agent signature, invoice ask) stays in the builder; only
`_block` -> `_render`, `_sig` -> `_sig(tex, ...)`, and the subject call change.

### 6.6 Determinism rules

- One `random.Random(seed)` stream, as today. Every texture decision draws from
  `self.rng`; nothing reads the clock, the platform, or `hash()`.
- Fixed draw order per builder: texture first, then `_base()`, then
  pathology-specific draws, then renderer-internal draws (label picks, line
  shuffles) in source order. Different documents may consume different draw
  counts; determinism only requires the same call sequence for the same seed,
  which round-robin generation guarantees.
- ASCII only (the corpus already is; "2 x 40'HC" style strings use "x", not the
  multiplication sign) so byte-identity claims stay trivial to verify.
- v0.3 texture changes the byte stream for the canonical seed by design. This is
  a corpus version bump: no v0.2 score is comparable to a v0.3 score, and the
  README must say so the same way it did for v0.1 -> v0.2. (README edit is
  downstream of this spec, not part of it.)

---

## 7. Test interactions: two amendments, exactly

The suite otherwise passes untouched. Both amendments are to tests whose intent
is unaffected; they currently over-fit the v0.1 rendering.

### 7.1 `test_unit_ambiguity_truth_is_kilograms` (required)

Currently parses the label: `d.body.split("Gross weight: ")[1].split(" lbs")[0]`.
Bullets/prose/table layouts render lbs without that exact label. Amend to parse
the unit, which is the actual invariant:

```python
import re  # top of file
lbs = float(re.search(r"([\d][\d.]*)\s*lbs", d.body).group(1))
```

### 7.2 `TestTruthIsEvidenced` (no change required; optional extension noted)

The four date styles in `_evidenced` are sufficient because renderers are
restricted to `_fmt_date` output (section 4). If implementation later wants
natural unpadded dates ("5 Mar 2026"), that is a paired change: add a style to
`_fmt_date` (compute the day with an f-string, `%-d` is not portable) and add its
key to the test's style tuple. Not required for this spec and not recommended in
the first pass; keep the change surface minimal.

New tests this spec adds (deterministic, no network, canonical seed):

```python
class TestTextureDiversity(unittest.TestCase):
    def setUp(self):
        self.docs = Generator(20260811).corpus(200)

    def test_no_universal_label_block(self):
        share = sum("\nMode: " in d.body for d in self.docs) / len(self.docs)
        self.assertLessEqual(share, 0.45)   # v0.2 value: 1.00

    def test_greeting_variety(self):
        firsts = {d.body.splitlines()[0] for d in self.docs if d.body.strip()}
        self.assertGreaterEqual(len(firsts), 6)

    def test_forwarded_thread_quote_styles_vary(self):
        markers = ("-----Original Message-----", "wrote:",
                   "________________________________")
        seen = {m for d in self.docs if d.pathology == "forwarded_thread"
                for m in markers if m in d.body}
        self.assertGreaterEqual(len(seen), 2)

class TestTemplateArtifactKilled(unittest.TestCase):
    """The v0.2 finding this spec exists to fix: naive regexes scored 96% on
    the rigid pathologies. If naive can still do that, the texture failed."""
    def test_naive_no_longer_aces_rigid_pathologies(self):
        docs = [d.to_json() for d in Generator(20260811).corpus(200)]
        report = score_corpus(docs, naive_predictions(docs))
        for key in ("agent_not_shipper", "weight_conflict", "forwarded_thread"):
            rate = report.pass_rate_for_pathology(key, "critical")  # small Report helper
            self.assertLessEqual(rate, 0.80, f"naive still aces {key}: {rate:.0%}")
```

(`pass_rate_for_pathology` is a five-line addition to `Report`; if the scoring
spec owner objects, the same assertion can be computed in the test from
`report.results` joined against doc pathologies.)

### 7.3 `naive.py` is frozen

The naive extractor is not updated to chase the new layouts. It is the
before/after instrument: the same afternoon-of-regexes, measured against a corpus
that no longer hands it universal structure. Its expected trajectory is graceful
degradation, not zero: it keeps the ~35% block-share documents, `BK-\d{5}`
references everywhere, and the DG keyword everywhere. Rewriting naive to handle
the new corpus would be re-fitting the baseline to the benchmark and would
destroy the comparison this change exists to make.

---

## 8. Assumptions register (things the research does not support)

Per the honesty constraint: every entry below is in the corpus on judgment, not
evidence. If any proves wrong against real correspondence, it is texture-only and
removable without touching ground truth.

| Feature | Status |
|---|---|
| "Sent from my iPhone" mobile signature | No source in research. Universal convention, low weight (.2 of sig draws, casual/terse only) |
| Specific ops shorthand tokens ("pls", "shpr", "cnee", "rgds", "thx") | Compression is sourced (mg-spl); these exact tokens are not |
| Job titles in signatures | Gap #11: contact-detail advice is sourced, verified signature blocks are not |
| `> ` and "On {date}, {name} wrote:" quoting | Not in research; "-----Original Message-----" is v0.1's own precedent, To/From/Subject header shape sourced via emailsinenglish |
| Second disclaimer sentence ("If you have received this email in error...") | First sentence is the sourced generic pattern (cluster-A 3.8, itself flagged as not freight-verified); second is standard boilerplate, unsourced |
| Invented email domains, phone numbers | Necessarily invented; consistent with the repo's synthetic-data stance |
| "lane" and "useless" subject styles' exact strings | Vague/compressed subjects are inferable from mg-spl and Freightamigo; the specific strings are ours |
| Multi-prefix "FW: FW:" chains | Single RE:/FW: is v0.1 convention; stacking is an assumption |
| Newbie persona details beyond the emailsinenglish opener | Grounded in mg-spl's vague-request warning, extrapolated |

The confidentiality footer deserves its own honesty note in the README when v0.3
ships: the research explicitly failed to verify a freight-specific disclaimer
(gap #11 / access-limitations section), so the corpus carries a generic one.

---

## 9. How we will know it worked

All checks run offline against the canonical seed (20260811, n=200) except the
last.

1. **The headline check: naive's rigid-pathology advantage collapses.**
   `python3 -m freightbench naive` per-pathology critical pass on
   agent_not_shipper, weight_conflict and forwarded_thread drops from 96% each to
   at most 80% (expected landing zone 55-70%, since naive keeps only the
   block-share docs plus references and the DG keyword elsewhere). Encoded as
   `TestTemplateArtifactKilled`.
2. **Naive stops beating frontier models overall.** Overall naive critical falls
   from 86.6% to at most 75%, while remaining above the empty extractor
   (`test_naive_beats_empty_but_is_far_from_solved` already enforces the floor
   and the <95% ceiling; both keep passing).
3. **Diversity is measured, not asserted.** `TestTextureDiversity` passes:
   labelled-block share <= 45%, >= 6 distinct opening lines, >= 2 quoting styles
   observed among forwarded_thread docs.
4. **The evidence invariant holds with a two-line test diff.** Full suite green
   with exactly the section 7.1 amendment (plus the new test classes); no other
   test file changes. `TestTruthIsEvidenced` passes over the texture-varied
   corpus unmodified, which is the proof that prose rendering kept every truth
   value findable.
5. **Determinism holds.** `test_same_seed_same_corpus` passes; two fresh clones
   generate byte-identical v0.3 corpora.
6. **The model gap reopens in the right direction (paid, not a merge gate).**
   On the next preview run, Sonnet and Opus should match or beat naive on every
   pathology, and the README's "naive still beats Sonnet and Opus on the
   rigid-template pathologies" paragraph gets deleted because it is no longer
   true. If an LLM's missed-rate rises slightly on prose documents, that is the
   benchmark getting honest, not a regression; the number to watch is
   hallucination rate, which should not move materially for Sonnet/Opus.

Non-goal restated: naive at 0% would mean the corpus stopped containing
labelled-block mail, which the research says is real (pasted checklists,
Freightos). The target is a corpus where no single surface form is load-bearing,
scored by an unchanged instrument.
