# Cluster D Research: EDI Message Structures & Prior-Art Benchmarks

Research for FreightBench README positioning. Two areas: (1) real EDI/XML message field
structures used in freight forwarding, (2) prior public benchmarks for document/email
information extraction, for honest positioning against existing work.

Note on method: `service.unece.org` and `unece.org/fileadmin/DAM` (the official UNECE UNTDID
pages) returned HTTP 403 on every direct WebFetch attempt — likely bot-blocked. Segment lists
for IFTMIN/IFTMBF/IFCSUM below are sourced from Stedi's EDIFACT documentation instead, which
mirrors the same UN/EDIFACT specification text and was fetchable. Several IATA PDFs (Cargo-XML
white paper, ZRA Cargo-XML guide, IATA Cargo-XML Messages PDF) also failed to extract as
readable text (compressed/binary PDF streams) — these are noted as attempted-but-unreadable,
not used as sourced findings.

---

## AREA 1 — EDI Message Structures for Freight Forwarding

### UN/EDIFACT IFTMIN (Instruction Message)

**Source:** https://www.stedi.com/edi/edifact/messages/IFTMIN (EDIFACT Release D21A; segment
table cross-checked against WebSearch snippets of the official UNECE D03B/D96A specification
text, which agree on purpose wording and core segments)

**What it is:** Stedi is a commercial EDI documentation/tooling site that republishes the full
UN/EDIFACT message specifications (segment tables, status, repeat counts) in browsable form.

**Stated purpose (from the spec text):** "A message from the party issuing an instruction
regarding forwarding/transport services for a consignment under conditions agreed, to the party
arranging the forwarding and/or transport services."

**Full segment structure observed:**

Header level (all under UNH/UNT message envelope):
- UNH (Message header, M, 1) / BGM (Beginning of message, M, 1) / CTA (Contact information, C,
  1) / COM (Communication contact, C, 9) / DTM (Date/time/period, C, 9) / TSR (Transport service
  requirements, C, 9) / CUX (Currencies, C, 9) / MOA (Monetary amount, C, 99) / FTX (Free text,
  C, 99) / CNT (Control total, C, 9) / DOC (Document/message details, C, 9) / GDS (Nature of
  cargo, C, 9)

Segment groups (nested):
- **Group 1** (repeat 99): LOC (M,1) + DTM (C,9) — location identification with dates
- **Group 2** (repeat 2): TOD (M,1, terms of delivery/transport) + LOC (C,9)
- **Group 3** (repeat 999): RFF (M,1, reference) + DTM (C,9)
- **Group 4** (repeat 9): GOR (M,1, governmental requirements) + DTM/LOC/SEL/FTX (all C,9)
  - Subgroup 5 (repeat 9): DOC (M,1) + DTM (C,1)
- **Group 6** (repeat 9): CPI (M,1, charge payment instructions) + RFF(C,99)/CUX(C,1)/LOC(C,9)/MOA(C,9)
- **Group 7** (repeat 99): TCC (M,1, charge/rate calculation) + LOC/FTX/CUX/PRI/EQN/PCD (all
  C,1) + MOA(C,9)/QTY(C,9)
- **Group 8** (repeat 99): TDT (M,1, transport details/main-leg info) + DTM(C,9)
  - Subgroup 9 (repeat 9): TSR (M,1) + SCC (C,9, scheduling conditions)
  - Subgroup 10 (repeat 99): LOC (M,1) + DTM (C,9)
  - Subgroup 11 (repeat 9): RFF (M,1) + DTM (C,1)
- **Group 12** (repeat 99): NAD (M,1, name and address — the party segment) + LOC(C,9) + MOA(C,9)
  - Subgroup 13: CTA(M,1)+COM(C,9); Subgroup 14: DOC(M,1)+DTM(C,1); Subgroup 15: TCC + charge
    fields; Subgroup 16: RFF+DTM; Subgroup 17: CPI+RFF+CUX+LOC+MOA; Subgroup 18: TSR+RFF+LOC+TPL+FTX
- **Group 19** (repeat 99): EFI (M,1, external file identification) + CED/COM/RFF/DTM/QTY
- **Group 20** (repeat 99999): GID (M,1, goods item details — the per-shipment-line segment) +
  HAN(C,99, handling instructions)/TMP(C,9, temperature)/RNG(C,9, range)/TMD(C,1, transport
  movement details)/LOC(C,9)/MOA(C,9)/PIA(C,9, additional product ID)/FTX(C,99)/PCD(C,9)
  - Subgroup 21: NAD+DTM+LOC (party at goods-item level)
  - GDS (C,9, nature of cargo)
  - Subgroup 22: MEA (M,1, measurements) + EQN
  - Subgroup 23: DIM (M,1, dimensions) + EQN
  - Subgroup 24: RFF + DTM
  - Subgroup 25 (repeat 999): PCI (M,1, package identification) + RFF/DTM/GIN(C,10, goods
    identity number)
  - Subgroup 26: DOC + DTM
  - Subgroup 27: GOR + DTM/LOC/SEL/FTX (nested DOC+DTM sub-subgroup)
  - Subgroup 29/30: TPL (transport placement) + MEA/EQN
  - Subgroup 31/32: SGP (repeat 999, split goods placement) + MEA/EQN
  - Subgroup 33: TCC + charge fields (repeat 99)
  - Subgroup 34 (repeat 99): DGS (M,1, **dangerous goods**) + FTX(C,99)
    - nested CTA+COM, MEA+EQN, SGP+MEA+EQN
- **Group 39** (repeat 999): EQD (M,1, equipment details — container/ULD) + EQN/TMD/MEA/DIM/SEL/
  TPL/HAN/TMP/RNG/FTX/RFF
  - Subgroup 40: TCC charge fields; Subgroup 41: NAD+DTM (+CTA+COM); Subgroup 43: EQA+EQN
    (attached equipment); Subgroup 44: DGS+FTX (+CTA+COM)
- UNT (Message trailer, M, 1)

**Notes on realism:** IFTMIN's structure maps closely onto what FreightBench's 35 fields are
trying to capture in plain-text form: BGM=booking/document reference, NAD=shipper/consignee/
notify party, LOC=origin/destination/port pairs, DTM=dates (ETD/ETA/cutoff), TDT=vessel/flight/
carrier info, GID/MEA/DIM=cargo description/weight/dimensions, EQD=container/equipment, DGS=
dangerous goods, RFF=references. The real spec has ~40 distinct segment types and 5+ levels of
nesting for a single booking instruction — a useful data point for the README to cite when
explaining why FreightBench uses a flat 35-field schema instead of attempting full EDI fidelity.

---

### UN/EDIFACT IFTMBF (Firm Booking Message)

**Source:** https://www.stedi.com/edi/edifact/messages/IFTMBF (EDIFACT Release D21A)

**Stated purpose:** "A message from a party definitely booking forwarding and/or transport
services for a consignment to the party providing those services" with conditions specified by
the sender.

**Full segment structure observed:** Structurally near-identical to IFTMIN at the header level
and through most segment groups (UNH/BGM/CTA/COM/DTM/TSR/MOA/FTX/CNT/GDS header; Group 1
LOC+DTM; Group 2 TOD+LOC; Group 3 RFF+DTM; Group 4 GOR+FTX with nested DOC+DTM; Group 6 TCC
charge block; Group 7 TDT+DTM with nested TSR+SCC, LOC+DTM, RFF+DTM; Group 11 NAD (party) with
nested CTA+COM, DOC+DTM, RFF+DTM, CPI+RFF+CUX+LOC+MOA, TSR+RFF+LOC+TPL+FTX; Group 17 GID (goods
item, repeat 99999) with nested NAD+DTM, MEA+EQN, DIM+EQN, RFF+DTM, PCI+RFF+DTM+GIN, DOC+DTM,
TPL+MEA+EQN, SGP+MEA+EQN (split goods placement), DGS+FTX dangerous-goods block with nested
CTA+COM and SGP+MEA+EQN; Group 33 EQD (equipment, repeat 999) with nested NAD+DTM+CTA+COM and
DGS+FTX+CTA+COM). UNT trailer.

**Difference from IFTMIN:** IFTMBF omits IFTMIN's separate CUX (currencies) and DOC
(document/message details) header segments and its Group 19 EFI (external file identification)
block — consistent with IFTMBF being the firm/confirmed booking commitment rather than the
fuller instruction message with attachable external files.

**Notes on realism:** IFTMBF is the closest real-world EDI analog to what FreightBench actually
generates — a party (shipper/forwarder) firmly booking transport for a consignment. The message
still carries the same deep goods-item (GID) and equipment (EQD) nesting as IFTMIN, reinforcing
that even a "simple firm booking" in real EDI carries far more structural depth than a flat
35-field schema — useful context for a README section on why FreightBench deliberately
flattens the schema instead of modeling full EDIFACT nesting.

---

### UN/EDIFACT IFCSUM (Forwarding and Consolidation Summary / Consignment Summary List)

**Source:** https://www.stedi.com/edi/edifact/messages/IFCSUM (EDIFACT Release D21A); message
purpose text cross-checked against WebSearch snippets of the UNECE D01B/D14B spec ("used by the
carrier to inform the insurer and/or the insurance intermediary about a consolidation of
consignments" for insurance purposes; general purpose text also references reconciliation)

**Stated purpose:** Enables "consolidation purposes from a party arranging forwarding and
transport services to the party for which the transport of the consolidated cargo is destined."
Per UNECE snippets, the message supports two forms: a **short form** that acts as a
reconciliation statement referencing previously sent messages, and an **extended form** that
includes full consignment detail inline.

**Header-level segments:** UNH, BGM (M,1 — carries Master B/L / Master AWB number, type, date,
function per UNECE snippet), DTM (C,9), MOA (C,99), FTX (C,99), CNT (C,9, control total — total
equipment count, total consignment count, total gross weight of the whole consolidation per
UNECE snippet), PCD (C,1), GDS (C,9).

**Detail/summary segment groups (large message, ~80 groups total):** Group 1 RFF+DTM; Group 2
GOR+DTM+LOC+SEL+FTX (governmental requirements) with nested Group 3 DOC+DTM; **Group 4 NAD**
(party, repeat 9 at this level) with nested CTA+COM, RFF+DTM; Group 7 TCC/CUX/PRI/EQN/PCD/MOA/
QTY/LOC (charge/rate detail); Group 8 ICD+DTM+FTX; Group 9 TDT+DTM (transport, main leg) with
~13 further nested sub-groups (TSR/SCC/LOC/DTM/SEL/FTX/MEA/EQN/DIM/CTA/COM/TCC/MOA/PCD/ICD/RFF/
NAD); **Group 23 EQD** (equipment, repeat up to 9999) with nested EQN/TPL/TMD/MEA/DIM/SEL/NAD/
LOC/HAN/TMP/FTX/RFF/PCD, plus nested EQA (attached equipment)+EQN and DGS (dangerous goods)+FTX
blocks; **Group 28 CNI** (Consignment information, M, repeat up to 9999) — "a segment to
indicate consignments included in the consolidation using the transport document/message number
or to replace the segment BGM of a single consignment based message structure" (per UNECE
snippet) — with a large nested block (SGP/MEA/EQN/TPL/CTA/COM/DTM/CNT/TSR/CUX/PCD/MOA/FTX/GDS/
LOC/TOD/RFF/GOR/CPI/TCC/ICD/TDT/NAD/EFI); **Group 55 GID** (goods item, M, repeat up to 99999)
with an equally large nested block (HAN/TMP/RNG/TMD/LOC/MOA/PIA/GIN/FTX/NAD/DTM/GDS/MEA/EQN/DIM/
RFF/PCI/DOC/GOR/TPL/SGP/SEQ/TCC/DGS); **Group 75 EQD** (equipment, summary level, repeat 999)
with nested EQN/TMD/MEA/DIM/SEL/TPL/HAN/TMP/RNG/FTX/PCD/TCC/NAD/DTM/EQA/DGS. UNT trailer.

**Real sample message (verbatim, retrieved from an open-source EDI parser's test fixtures):**

Source: https://github.com/indice-co/EDI.Net/blob/master/test/indice.Edi.Tests/Samples/edifact.D01B.IFCSUM.NewLines.EDI
(indice-co/EDI.Net, a .NET EDI parsing library — this is a real test fixture, not a spec example)

```
UNB+UNOA:1+5011408000007:14+5999999999952:14+180525:2030+2216+PASSWORD+IFCSUM
UNH+1+IFCSUM:D:01B:UN:EAN003
BGM+610+1000505549+9
DTM+137:20180525:102
DTM+11:20180525:102
CNT+10:5
CNT+7:25.784:KG
NAD+CZ+5011408000007.::9+UK2.
NAD+CA+5999999999950::9
TDT+20++10:SEA
CNI+1+311447177::I
DTM+2:201805290000:203
CNT+2:64:PA
CNT+11:1:PA
CNT+7:8.269:KG
TSR+3+++11
NAD+DP+PC+1919990312
RFF+DQ:5000706244
RFF+CR:TUESDAY 29TH MAY
GID+1+:350114081527920321:1:9+1:3600530124848:PK:9
PIA+1+B0918306:::91
FTX+AAA+++MAYB NAIL ForeverStrong 06 DeepRed 12
MEA+AAE+UCO:4+UN:3
GID+2+:350114081527920321:1:9+1:3600530521845:PK:9
PIA+1+B1297005:::91
FTX+AAA+++MAYB Found. Dream Satin Liquid Sand 30
MEA+AAE+UCO:4+UN:3
UNT+787+1
UNZ+1+2216
```

**Notes on realism:** This is genuinely useful as a realism reference — it shows how compact and
code-heavy real EDI segments are (e.g. `TDT+20++10:SEA` for transport mode = sea,
`CNT+7:25.784:KG` for a weight control total) compared to FreightBength's plain-English email
bodies. It also shows the CNI (consignment info) + GID (goods item) pairing that a
consolidation summary uses to list multiple house shipments/products under one control total —
structurally the closest real EDI analog to FreightBench's "multi-shipment email" pathology.

---

### CargoIMP FWB (Freight/Air Waybill) and FHL (House Waybill/Manifest)

**Sources:**
1. https://www.parse2.com/example-cargoimp-FWB16.shtml — Parse2 (aParse ABNF parser generator
   vendor) published example page for validating Cargo-IMP FWB/16 messages.
2. https://flaks.io/glossary/cargo-imp — Flaks (logistics-tech vendor) glossary page explaining
   Cargo-IMP terminology.
3. http://xmlpipelineserver.com/data-sources/edi-standards/iata-cargo-imp/ — XML Pipeline
   Server (commercial EDI middleware vendor) compatibility matrix for Cargo-IMP versions 21–28.

**What Cargo-IMP is:** IATA's Cargo Interchange Message Procedures, introduced 1975, using
compact Type B EDI text messages (not EDIFACT) between airlines, freight forwarders, and ground
handlers. Its 34th edition (effective 2015-01-01) is now frozen — no further updates planned.
Messages are subdivided into "segments" identified by three-letter tags at the start of each
segment (per flaks.io and general search results).

**Real sample FWB/16 message (verbatim, from parse2.com's published validation example):**

```
FWB/16 777-12345675BOMSUV/T1K3.5 RTG/SUVII SHP /T. ULSIDAS LTD. /105 VEER TAMAN ROAD /MUMBAI /IN
CNE /J. JONES IMPORTERS /. /SUVA /FJ AGT//1430288 /SPEEDAIR SERVICES /MUMBAI CVD/INR//PP/NVD/1500.00/XXX
RTD/1/P1/K3.5/CM/W3.5/R800.00/T800.00 /NG/CLOTH SAMPLES /2/ND//NDA PPD/WT800.00 /CT800.00
CER/T.ULSIDAS LTD. ISU/01OCT05/MUMBAI/SPEEDAIR SERVICES REF///AGT/SPEEDAIRSERVICES/BOM
```

Segment tags identified in this sample: **FWB/16** (message + version), **777-12345675** (AWB
number: 3-digit airline prefix + 8-digit serial), **BOMSUV** (origin/destination airport pair),
**RTG** (routing), **SHP** (shipper name/address block), **CNE** (consignee name/address block),
**AGT** (agent — IATA cargo agent code + name + location), **CVD** (currency/valuation/charges
declared), **RTD** (rate description — pieces/weight/rate class/weight/rate/total), **NG**
(nature of goods description), **PPD** (prepaid charges summary), **CER** (certification/
signatory), **ISU** (issue date/place/issuing agent), **REF** (reference).

**FHL (Consolidation List) clarification — a real naming trap worth noting for FreightBench's
"ambiguous naming" pathology angle:** Per flaks.io, FHL is commonly *misnamed* as "house waybill
data" but is actually the **consolidation summary/manifest** (listing houses under a master);
the dedicated House Air Waybill Data message is actually **FZB**. Practitioners and even some
airline systems conflate the two. Per xmlpipelineserver.com's version matrix, Cargo-IMP FHL
exists in versions 2–3, FWB in versions 12–15 (later versions per parse2.com: FWB/17, FHL/5 were
added to their validator in Nov 2021), FFM (Airline Flight Manifest) in versions 5–7, FSU
(Status Update) in versions 8–12. Full list of Cargo-IMP message families per flaks.io: **FWB**
(Air Waybill Data / master AWB), **FFM** (Airline Flight Manifest), **FSU** (Status Update —
shipment event/milestone messages), **FHL** (Consolidation List), **FZB** (House Waybill Data —
the actual HAWB message), **FFR** (AWB Space Allocation Request — i.e. a booking request, often
confused with a flight manifest).

**Notes on realism:** The real FWB sample shows how densely-coded and abbreviation-heavy actual
air cargo messaging is (e.g. `RTD/1/P1/K3.5/CM/W3.5/R800.00/T800.00` packs pieces, weight unit,
commodity class, weight, rate, and total into one slash-delimited segment) — a strong contrast
point for FreightBench's plain-English synthetic emails, and useful ammunition for a README
paragraph on why FreightBench targets email-shaped extraction rather than trying to simulate
Cargo-IMP's terse wire format. The FHL/FZB naming confusion is also a nice real-world precedent
for FreightBench's "ambiguous/confusable field" pathology category.

---

### Cargo-XML (IATA's XML message standard)

**Sources:**
1. https://github.com/riege/one-record-converter — Riege Software's open-source Java library
   converting Cargo-XML XFWB/XFZB messages into IATA's newer ONE Record data model; live demo
   at onerecord.riege.com.
2. https://flaks.io/glossary/cargo-imp — same glossary page as above, covers the Cargo-XML
   relationship.
3. Search-snippet confirmation (WebSearch only, not independently fetched — IATA's own PDFs
   returned unreadable/binary content on WebFetch): IATA published the "Cargo-XML Manual and
   Toolkit" (1st edition, December 2012) covering 14 Cargo-XML messages; XFWB (XML Waybill) and
   XFNM (XML Response) were the first two messages recommended for phased migration.

**What it is:** Cargo-XML (introduced ~2010) is IATA's XML-based successor to Cargo-IMP,
re-expressing the same message content in XML while removing Cargo-IMP's fixed character-set
and message-size constraints. Each Cargo-XML message keeps a 1:1 mapping to its Cargo-IMP
ancestor with an "X" prefix: **XFWB** (↔ FWB, air waybill), **XFHL** (↔ FHL, consolidation
list), **XFZB** (↔ FZB, house waybill), **XFSU** (↔ FSU, status update), etc. Per the riege
repo's README, XFWB3 is described as "a message from a forwarder to an airline," and XFZB3
(house waybill) has "more basic mapping support" in their converter than XFWB3 — implying XFZB
is structurally simpler/less complete in practice.

**Schema location (not independently verified as readable — noted for completeness):** IATA
states schema information from the Cargo-XML Toolkit is published on IATA's own "Cargo-XML
validation portal" (cargo-xml-autocheck.iata.org) — this was referenced in search snippets but
not fetched directly (not attempted as it sits behind IATA's own tooling, not a plain document).

**Notes on realism:** The XFWB/XFZB ↔ FWB/FHL/FZB 1:1 correspondence is a clean way to explain
in the README that "EDI" for air cargo now has two live wire formats (legacy Cargo-IMP text and
modern Cargo-XML) carrying identical field semantics — reinforcing that FreightBench's 35 fields
are a deliberately-simplified superset of what several real, non-interoperable formats already
try to standardize.

---

### Other Area 1 sources consulted (general context, not message-structure-specific)

- **https://github.com/nerdocs/pydifact** — general-purpose Python EDIFACT parser/serializer
  library (port of a Perl `metroplex-systems/edifact` library). No freight-specific message
  examples in the README; useful only as evidence that open-source EDIFACT tooling exists but
  doesn't ship domain (freight) sample messages out of the box.
- **https://github.com/parcelLab-archive/edi-iftmin** — archived (Nov 2022, read-only) parser
  specifically for IFTMIN/IFTSTA built by parcelLab (a parcel-tracking company), confirming
  real industry use of IFTMIN for carrier booking integration. README shows only *parsed JSON
  output* structure, not raw EDI text, so not usable as a message-text sample.
- WebSearch-only note: per a transportmanagement.org search snippet, "most European road
  freight carriers won't accept bookings through a REST API — they want EDIFACT IFTMIN
  messages, with status updates sent back as IFTSTA" — background color confirming IFTMIN's
  continued real-world relevance (not independently fetched/verified beyond the search snippet).

---

## AREA 2 — Prior Public Benchmarks for Document/Email Information Extraction

### CORD (Consolidated Receipt Dataset)

**Source:** https://github.com/clovaai/cord (NAVER CLOVA AI Research, official repo)

- **What it is:** Receipt-image key information extraction / post-OCR semantic parsing dataset.
- **Size:** 11,000+ real Indonesian receipts collected from shops and restaurants in the
  original paper; the publicly released version ships a 1,000-receipt sample (800 train / 100
  dev / 100 test) — some fields (store_info, payment_info, etc.) were removed from the public
  release for legal/privacy reasons.
- **Task:** OCR box/text annotation + multi-level semantic parsing — 8 superclasses, 54
  subclasses (menu, void menu, subtotal, void total, total, etc.), plus quadrilateral
  coordinates, row groupings, and key/value flags.
- **License:** CC-BY-4.0.
- **Real vs synthetic:** Real receipts, real OCR.
- **Vs. FreightBench:** Image/OCR-first (not plain text), receipt domain (not freight), no
  correct/wrong/missing separation — it's a parsing-accuracy task, not an error-taxonomy
  benchmark.

### FUNSD (Form Understanding in Noisy Scanned Documents)

**Sources:** https://guillaumejaume.github.io/FUNSD/ (official project page) and
https://huggingface.co/datasets/nielsr/FUNSD_layoutlmv2 (dataset card, for license check)

- **What it is:** A form-understanding dataset from a 2019 ICDAR workshop paper (Jaume et al.,
  arXiv:1905.13538).
- **Size:** 199 real, fully annotated scanned forms — 31,485 words, 9,707 semantic entities,
  5,304 relations. Split 149 train / 50 test.
- **Task:** Text detection, OCR, spatial layout analysis, and entity labeling/linking. Each
  semantic entity has a label (question/answer/header/other), bounding box, and links to other
  entities.
- **License:** Not clearly stated — the HuggingFace dataset card lists licensing info as "more
  information needed," so this should be flagged as unconfirmed if cited precisely.
  Documents are noisy real-world scanned forms (not synthetic).
- **Vs. FreightBench:** Visual/layout-first scanned-image task (bounding boxes + entity
  linking), general forms (not freight-specific), tiny by ML standards (199 documents) vs.
  FreightBench's deterministic/regeneratable synthetic corpus of any size.

### Kleister (NDA and Charity datasets)

**Source:** https://arxiv.org/abs/2105.05796 (Stanisławek et al., ICDAR 2021, "Kleister: Key
Information Extraction Datasets Involving Long Documents with Complex Layouts")

- **What it is:** Two key information extraction (KIE) datasets for long, complex-layout
  formal documents.
- **Size:** **Kleister NDA** — 540 non-disclosure agreements, 3,229 pages, 2,160 entities to
  extract. **Kleister Charity** — 2,788 annual financial reports of charities, 61,643 pages,
  21,612 entities to extract.
- **Task:** Entity/key-information extraction requiring both textual and structural
  (layout) features, over documents far longer than typical KIE benchmarks.
- **Real vs synthetic:** A mix of scanned and born-digital real documents.
- **Baselines:** Flair, BERT, RoBERTa, LayoutLM, LAMBERT — best F1 81.77% (NDA) / 83.57%
  (Charity), showing the long-document setting is genuinely hard for 2021-era models.
- **License:** Referenced on the page but not confirmed in detail from what was fetched.
- **Vs. FreightBench:** Long multi-page legal/financial documents (NDAs, annual reports) —
  closer to FreightBench in spirit (real-world entity extraction with a defined entity list)
  but a completely different document domain and no per-field wrong-vs-missing distinction
  called out in the abstract.

### DocVQA (Document Visual Question Answering)

**Source:** https://arxiv.org/abs/2007.00398 (Mathew et al., WACV 2021) + WebSearch
confirmation of document provenance

- **What it is:** A visual-question-answering benchmark over document images.
- **Size:** 50,000 question-answer pairs over 12,767 document page images from 6,071 unique
  documents (40k/5k/5k train/val/test question split).
- **Document domain:** Sourced from the real UCSF Industry Documents Library (1900–2018),
  spanning five industry sectors — tobacco, food, drug, fossil fuel, chemical. Questions and
  answers are manually annotated (real documents, human-authored QA).
- **Task:** Free-form natural-language question answering grounded in a document image (not
  fixed-schema field extraction) — human accuracy benchmark is 94.36%, with a stated large gap
  for contemporary models.
- **Vs. FreightBench:** VQA framing (open-ended questions) rather than fixed-schema field
  extraction; real scanned documents vs. synthetic email text; no freight/logistics content;
  no explicit abstention/hallucination scoring category.

### DocILE (Document Information Localization and Extraction)

**Source:** https://docile.rossum.ai/ (official benchmark site, Rossum + co-authors, ICDAR
2023, Šimsa et al., arXiv:2302.05658)

- **What it is:** A large benchmark for Key Information Localization and Extraction (KILE) and
  Line Item Recognition (LIR) on semi-structured business documents (invoices, orders).
- **Size:** 6,680 real annotated documents + 100,000 synthetically generated documents + ~1
  million unlabeled documents for unsupervised pretraining.
- **Task:** Two tasks — KILE (localize + extract key fields, 55 annotated classes, more granular
  than prior KIE datasets) and LIR (assign extracted values to line items in a table — pieces/
  quantities/amounts per row).
- **License/access:** Requires filling out a "Dataset Access Request form" citing personal-data
  processing terms for research use — not a fully open CC-style release.
  Baselines: RoBERTa, LayoutLMv3, DETR-based Table Transformer.
- **Vs. FreightBench:** Closest of the reviewed benchmarks in *task shape* — real + synthetic
  mix, line-item-level structure (comparable to FreightBench's per-shipment-line fields in a
  multi-shipment email) — but invoice/order domain, not freight booking, and gated access
  rather than a fully open pip-installable generator.

### RealDocBench

**Source:** https://arxiv.org/abs/2606.07401 ("RealDocBench: A Benchmark for Field-Level QA and
Layout Understanding on Real-World Regulated Documents," June 2026)

- **What it is:** A two-track benchmark built specifically to move past "clean academic layouts
  or synthetic prose" (the paper's own framing) toward real regulated-industry documents.
- **Domains:** Four — mortgage underwriting, financial reporting, **supply-chain logistics**
  (explicitly named, includes bills of lading among its document types per the WebSearch
  summary), and clinical records.
- **Size:** QA track — 1,356 field-level questions over 581 real documents, each paired with a
  typed `gold_dict` of key→value answers, scored **per-field and strict per-question**. Layout
  track — 1,500 human-verified page images with COCO-style bounding boxes under a 9-class
  taxonomy, scored via a Hungarian matcher with "adjacency-aware split/merge recovery."
- **Real vs synthetic:** Explicitly real, sourced from actual regulated workflows (not
  synthetic).
- **Vs. FreightBench:** **The closest match found to FreightBench's own scoring philosophy** —
  per-field typed-answer scoring against a gold dict, plus an explicit critique of
  synthetic-prose benchmarks. Key differences: RealDocBench uses real (not synthetic,
  not-reproducible) documents, spans 4 broad regulated domains rather than being freight-
  specific, and — as far as retrieved — doesn't appear to separate "wrong" from "missing" as
  distinct outcome categories the way FreightBench's 5-category scoring does. Bills of lading
  are one example document type within its logistics slice, not a dedicated freight-booking
  focus, and it evaluates on scanned/real documents rather than testing pathology-tagged
  synthetic traps.

### RealKIE

**Source:** https://arxiv.org/pdf/2403.20101 ("RealKIE: Five Novel Datasets for Enterprise Key
Information Extraction")

- **What it is:** Five real-document KIE datasets aimed at enterprise use cases.
- **The five datasets:** Charity Filings (financial disclosures), SEC Filings, FCC Filings,
  Resource Contracts (Resource Contracts Transparency Initiative), Political Advertisements
  (campaign finance/political ad disclosures).
- **License:** CC-BY-4.0.
- **Real vs synthetic:** All five are real documents from official public repositories/
  government agencies; OCR performed with Kofax OmniPage and Microsoft Computer Vision.
- **Logistics/freight relevance:** None — confirmed no dataset in this collection touches
  logistics, shipping, or freight. Included here only to rule it out explicitly, since it's a
  frequently-cited "enterprise KIE" benchmark that a reader might otherwise assume overlaps.

### Customs Import Declaration Datasets

**Source:** WebSearch snippets of arXiv:2208.02484 and its companion GitHub repo
(Seondong/Customs-Declaration-Datasets) — not independently fetched via WebFetch, so treat
figures below as search-snippet-sourced, not page-verified.

- **What it is:** A synthetic customs import-declaration dataset built for fraud-detection
  research, developed with customs domain experts.
- **Size:** 54,000 artificially generated trade records with 22 key attributes, synthesized via
  a conditional tabular GAN trained on a real base of 24.7 million customs declarations
  (Jan 2020–Jun 2021), preserving correlated features without exposing real underlying trades.
- **Task:** Binary/structured classification (fraud vs. critical-fraud labels) over tabular
  attributes — not text/document extraction.
- **Vs. FreightBench:** Same broad "trade/logistics" domain and same synthetic-generation
  instinct (both use synthetic data to avoid using real commercially-sensitive shipment data),
  but it's tabular fraud classification, not free-text field extraction — worth a one-line
  mention as "adjacent synthetic-logistics-data precedent," not a direct comparator.

### LLMStructBench

**Source:** https://arxiv.org/abs/2602.14743 and https://arxiv.org/html/2602.14743v1
("LLMStructBench: Benchmarking Large Language Model Structured Data Extraction")

- **What it is:** A benchmark for LLM structured-extraction-to-JSON, explicitly built around
  **email-shaped natural-language messages** — the paper frames itself around "email-based
  workflows in domains such as IT support, human resources, or project management."
- **Size:** 995 total tests across 5 use-case scenarios: Support Tickets (5 keys, depth 2),
  Sick Leave (7–9 keys, depth 3), Project Extension (7–9 keys, depth 3), Conference Registration
  (9 keys, depth 3), Loan Request (~10 keys avg, depth 4, includes nested object arrays).
- **Generation method:** Fully synthetic and LLM-generated — GPT-4o first produces a fully
  populated JSON object per schema, then an "email generation prompt" transforms that JSON into
  a natural-language message, with entity names/dates/numbers randomized for diversity. Tested
  across 22 models and 5 prompting strategies.
- **License/real vs synthetic:** Synthetic, open dataset (per abstract), no real personal data.
- **Vs. FreightBench:** **The closest match found to FreightBench's generation methodology**
  (schema → synthetic text via templated/generative transformation) applied to email-shaped
  text — but the domain is generic office/admin workflows, not freight, there's no named-
  pathology taxonomy (ambiguity, unit-conversion traps, conflicting values, etc.), and scoring
  is token-level/document-validity accuracy rather than a 5-category
  correct/abstained/wrong/missed/hallucinated split.

### ExtractBench

**Source:** https://arxiv.org/abs/2602.12247 ("ExtractBench: A Benchmark and Evaluation
Methodology for Complex Structured Extraction")

- **What it is:** A PDF-to-JSON structured extraction benchmark focused on enterprise-scale
  schema breadth.
- **Size:** 35 PDF documents paired with JSON Schemas and human-annotated gold labels, yielding
  12,867 evaluatable fields, with schema complexity ranging from tens to hundreds of fields
  (one financial-reporting schema has 369 fields).
- **Task/finding:** Frontier LLMs "remain unreliable on realistic schemas" — 0% valid output on
  the largest (369-field) schema across all tested models, a strong data point for motivating
  any benchmark (including FreightBench) built around realistic, imperfect extraction rather
  than toy schemas.
- **Domain:** General "economically valuable domains" (financial reporting named as an
  example); no logistics/freight domain mentioned in the retrieved abstract.
- **Vs. FreightBench:** Similar spirit (stress-testing LLMs on real-world schema complexity,
  not toy examples) but PDF-based, not email-based, and general-enterprise rather than freight-
  specific; no named-pathology taxonomy.

### Matrix / Kuehne+Nagel freight-forwarding invoice dataset

**Source:** https://arxiv.org/abs/2412.15274 ("Memory-Augmented Agent Training for Business
Document Understanding") + WebSearch confirmation of the named industry partner

- **What it is:** An academic paper (Penn State, Oregon State, and **Kuehne+Nagel** — one of
  the world's largest freight-forwarding/logistics providers) introducing "Matrix," a
  memory-augmented LLM agent training method, evaluated on a real freight-forwarding company's
  invoice data.
- **Task:** Extracting **transport reference numbers** from Universal Business Language (UBL)
  format invoices — a narrow, single-field-family extraction task (not FreightBench's 35-field
  multi-category schema).
- **Data:** Anonymized real UBL invoices prepared in collaboration with Kuehne+Nagel; per
  WebSearch summary, open-source data was made available on GitHub (not independently browsed/
  verified in this session — flagging as search-snippet-sourced, not page-confirmed).
- **Results:** Matrix beats standard chain-of-thought prompting by 30.3% and a vanilla LLM
  agent by 35.2%.
- **Vs. FreightBench:** **This is the single most directly on-domain prior-art result found** —
  a real freight-forwarding company's documents, real extraction task, published academic
  benchmark. But it differs sharply in shape: invoices (not booking emails), UBL-structured
  source documents (not free text with deliberately injected ambiguity), single-field-family
  extraction (transport references) rather than a full 35-field/11-pathology taxonomy, and an
  agent-training paper rather than a benchmark-for-benchmarking's-sake release. Worth citing in
  the README as proof that (a) real LSPs are actively building/publishing extraction
  evaluations, and (b) no one has yet published a freight *booking-email* benchmark with a
  named-pathology error taxonomy — that gap is what FreightBench fills.

### Other Area 2 findings noted but not deep-dived (lower confidence / tangential)

- **FATURA** — an invoice-image dataset described in search snippets as "the most extensive
  openly accessible invoice document image dataset" with 50 unique layouts; not independently
  fetched, mentioned only as one of several invoice-specific datasets alongside DocILE.
- **"From Synthetic to Native: Benchmarking Multilingual Intent Classification in Logistics
  Customer Service"** (arXiv:2603.23172) — confirmed via WebFetch abstract: ~30,000 de-
  identified real logistics customer-service queries (from 600k historical records), English/
  Spanish/Arabic plus zero-shot Indonesian/Chinese, 13 parent/17 leaf intents, native vs.
  machine-translated paired test sets. This is the **closest logistics-domain NLP benchmark
  found in terms of subject matter** (a real global logistics platform's customer-service
  traffic) but it is an **intent-classification** task, not field extraction — worth a one-line
  mention as "no logistics-domain extraction benchmark exists, but logistics-domain
  classification benchmarks are starting to appear."
- **ExStrucTiny** and **VAREX** (arXiv:2602.12203 and 2602.14743-adjacent 2603.15118) — general
  schema-variable / multi-modal structured extraction benchmarks surfaced in search results;
  not fetched in depth, no indication of logistics/email specificity, listed only for
  completeness of the search sweep.

---

## Summary Table (Area 2)

| Dataset | Domain | Size | Task | Real/Synthetic | Freight-specific? |
|---|---|---|---|---|---|
| CORD | Receipts | 11k (1k public) | Post-OCR parsing | Real | No |
| FUNSD | Scanned forms | 199 docs | Entity labeling/linking | Real | No |
| Kleister NDA/Charity | Legal/financial | 540 / 2,788 docs | Key info extraction | Real | No |
| DocVQA | Mixed industry docs | 50k QA / 12.7k pages | Visual QA | Real | No |
| DocILE | Invoices/orders | 6.7k real + 100k synth | KILE + line items | Real+Synthetic | No |
| RealDocBench | Mortgage/finance/**logistics**/clinical | 1,356 Q / 581 docs | Field-level QA | Real | Partial (BoL is one doc type) |
| RealKIE | Financial/govt/political | 5 datasets | Key info extraction | Real | No |
| Customs Import Declaration | Customs/trade | 54k records | Fraud classification | Synthetic (GAN) | Adjacent (tabular, not text) |
| LLMStructBench | Generic office **email** | 995 tests | Structured JSON extraction | Synthetic | No |
| ExtractBench | Enterprise PDFs | 35 docs / 12.9k fields | PDF-to-JSON extraction | Real | No |
| Matrix/Kuehne+Nagel | **Freight invoices** | Not disclosed in abstract | Transport-ref extraction | Real (anonymized) | Yes |
| **FreightBench** | **Freight booking emails** | Unlimited (generator) | 35-field, 5-outcome scoring | **Synthetic, deterministic** | **Yes** |
