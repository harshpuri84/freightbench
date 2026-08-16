# FreightBench: Real-World Document Inventory & Gap Analysis

Research pass to ground FreightBench v0.2 in reality. Method: WebSearch + WebFetch only,
against publicly available pages/PDFs. No binary files were downloaded to disk; PDFs were
read as text (via WebFetch, or by re-reading WebFetch's own cached copy with the Read
tool when its summarizer couldn't parse the binary — no separate download tool was used
in either case). All web content was treated as data, not instructions — nothing fetched
attempted to redirect the research itself. Verbatim quoting was kept under 15 words per
source; field/segment/box names are reproduced fully and exactly since they are short
technical labels, not copyrightable prose.

**Total: ~80 source citations across 11 document types, plus 13 dataset/benchmark
citations for positioning.** Every document type in the brief has at least 4 sources;
several (booking confirmations, DG declarations, HAWB/MAWB, House/Master B/L, EDI) have
7-12.

---

## Access limitations (read before trusting anything below)

- **Reddit was completely unreachable.** WebFetch returned an explicit tool-level block
  for every reddit.com / old.reddit.com URL tried, including r/freightforwarding and
  r/logistics search URLs. WebSearch queries targeting reddit.com never returned actual
  Reddit threads in the result set. **Zero Reddit sources** are in this inventory despite
  many attempts with varied phrasing. The "forum threads quoting real emails" angle from
  the original brief is genuinely not covered — not papered over with paraphrase.
- **LinkedIn was also unreachable.** No fetchable LinkedIn posts with real quoted
  booking/quote emails surfaced in any search. **Zero LinkedIn sources.**
- Many vendor/carrier help-center pages returned HTTP 403 to WebFetch (Flexport support
  articles, several Hapag-Lloyd and MSC and CMA CGM shipping-instruction PDFs, IATA's own
  fillable DGD PDF and Lithium Battery Guidance PDF, PHMSA's lithium-battery page, gwp.co.uk,
  Grokipedia, Magaya). Where a 403'd page's content could still be characterized from a
  substantial, specific WebSearch snippet, it's included below and explicitly marked
  "WebSearch snippet only, not independently fetched" — treat those as lower confidence.
- Several important PDFs (ONE's booking guide, MSC's IFTMBC EDIFACT guide, DAKOSY's
  Cargo-IMP FWB spec, IATA Resolution 600b, DCSA's B/L standard, the FIATA/CAREC slide
  deck, a Maersk specimen B/L) came back from WebFetch as unparsed binary. Full content
  was recovered by re-reading WebFetch's own auto-saved local cache copy with the Read
  tool (real PDF text/image extraction) — not by downloading anything new. These are
  full-confidence sources despite the extra step.
- One source (DocShipper's booking-number glossary) returned carrier-prefixed booking
  number examples via WebFetch's summarizer that pattern-match the **container** number
  format (ISO 6346) rather than a booking number, and may be the fetch tool's own
  plausible-sounding fabrication rather than text actually on the page. **Flagged as
  low-confidence; do not use those specific digit strings as ground truth.**
- No verified freight-industry-specific confidentiality/disclaimer email footer was found
  despite several search attempts — flagged as an open gap in the gap analysis, not
  invented to fill the hole.
- `service.unece.org` (the official UNECE UN/EDIFACT spec host) 403'd on every attempt;
  EDIFACT segment tables were sourced from Stedi's documentation instead (a commercial EDI
  docs site that republishes the same spec text) and cross-checked against WebSearch
  snippets of the official spec where possible.

---

## Summary table

| Document type | # sources | Best source | Key fields / facts worth stealing |
|---|---|---|---|
| Booking request emails | 4 | ONE (Ocean Network Express) Booking Request eCommerce Guide (PDF) | 5 distinct reference-number fields per booking (shipper ref / forwarder ref / invoice ref / 2× SI-stage refs); country-conditional customs fields (AES ITN, CERS, Mexico TAX IDs, China MOT No.); DG certificate-upload file types |
| Rate requests / spot quote emails | 6 | Freightamigo worked RFQ email samples | "RFQ - " subject-line prefix carrying compressed shipment params; itemized cost-breakdown asks; genuinely underspecified one-line requests are realistic |
| Booking confirmations (ocean & air) | 8 | MSC IFTMBC EDIFACT implementation guide (PDF) | Confirmation status is 3-valued (Pending/Accepted/Conditionally Accepted), not binary; VGM cut-off, SI-due date, and port cut-off are 3 separate deadlines |
| Shipping Instructions / SLI | 4 | NTCBFFA specimen SLI (40 numbered boxes) | USPPI EIN, per-line Schedule B/HTS + ECCN/EAR99/USML, routed-export-transaction flag; "SLI" and carrier "Shipping Instructions" are two different documents with the same name |
| HAWB / MAWB | 7 | eAWBlink AWB field guide + IATA Resolution 600b (Conditions of Contract) | 11-digit AWB number = 3-digit prefix + 7-digit serial + check digit (serial mod 7, verifiable); SPH/SCI/SSR/OSI/OCI handling codes; hard front-page-grid/back-page-legal-boilerplate split |
| House / Master Bill of Lading | 7 | DCSA "Standard for the Bill of Lading" (industry-consensus data standard) | Every field has a Mandatory/Conditional/Optional status **per lifecycle stage** (booking request → confirm → prepare B/L → issue); House and Master B/L must match on every field except shipper/consignee/notify/pickup |
| Commercial invoice & packing list | 5 | UK gov business.gov.uk export-invoice guide | Buyer and consignee are separate roles; "N of M" package-mark convention; invoice and packing-list totals must match exactly (a plantable pathology) |
| Arrival notices & pre-alerts | 4 | Freightos arrival-notice glossary | Vessel name and voyage number are separate fields; "location of goods" (terminal/CFS) is distinct from port of discharge; pre-alert is fundamentally a cover-email bundling other documents, not its own field schema |
| Dangerous goods declarations | 8 | UK MCA IMDG guidance + 49 CFR 173.185 (Cornell LII) | Tabular UN-No./Proper-Shipping-Name/Class-Division/Packing-Group grammar, not key:value; lithium-ion UN3480 vs. UN3481 Section II nuance; ocean DG needs a **second**, separate container-packing certificate air doesn't have |
| VGM declarations (SOLAS) | 4 | IncoDocs VGM explainer + IMO SOLAS page | Method 1 (weigh whole) vs. Method 2 (sum parts + tare); submitted **per container**, not per booking; container tare comes from a physical CSC-plate marking |
| EDI message samples | 12 | Stedi IFTMIN/IFTMBF/IFCSUM specs + a real IFCSUM sample message + a real Cargo-IMP FWB/16 sample message | ~40 segment types, 5+ nesting levels per booking message; real segments are dense and code-heavy (`TDT+20++10:SEA`) vs. FreightBench's plain English |

---

## 1. Booking Request Emails (shipper/customer → freight forwarder)

### ONE (Ocean Network Express) — "Outbound eCommerce Guide," Booking Request section
`https://ecomm.one-line.com/ecom/DocRoot/guide/How_to_booking_request.pdf`
Official 20-page guide from a top-6 container carrier explaining every field on its
online Booking Request form. The single richest field taxonomy found in this whole
research pass.
- **Fields:** Manual Booking Number; Template; Customer Information (Name, multi-recipient
  e-Mail, Phone, Fax, Contract No., Address, Named Account, Person placing Request);
  Parties (Shipper, Freight Forwarder, Consignee — each address-book-validated);
  Service Type per leg (CY/CFS/Door); Origin/Loading Port/Discharging Port/Destination;
  country-conditional customs fields — **US**: House Manifest Filing, AMS for House B/L,
  AES ITN; **Canada**: House Manifest Filing, ACI for House B/L, CERS License; **Mexico**:
  Shipper/Consignee/Notify TAX ID; **China origin**: MOT No.; Schedule (Departure Date or
  Vessel); Pick Up Date/Time; Container Type/Size/Quantity/S.O.C., FLEX OK, SPLIT OK;
  Pick Up Information (Supplier Name, Contact, Address, Drop-off/Pick-up Date & Time);
  Cargo (Commodity via HS-style code lookup, Total Estimated Weight); Reefer Cargo
  (Unit F/C, Degree, Ventilation, Nature, Humidity, Genset); Dangerous Cargo (UN No.,
  Class, Flash Point, Package Group, Certificate Upload — types: DGD-Final,
  DGD-Preliminary, MSDS, Pkg Certificate, Tank Certificate, and 6 more "Other-" types);
  Awkward Cargo (Package/Gross/Net Weight, Dimensions, Remarks); Special Instruction
  (free text, explicitly described as "the box to make notes... in an email booking or
  phone booking"); Reference No. (Invoice Ref., BKG SH Ref., BKG FF Ref., S/I SH Ref.,
  S/I FF No.); e-Mail Notification subscriptions; post-submit status columns (Request No.,
  Booking No., Split Y/N, Via, Status).
- **Realism notes:** Real bookings track up to five separate reference numbers
  simultaneously (shipper's own, forwarder's own, invoice, two SI-stage refs) — not one
  flat "our reference." Customs/compliance fields are **lane-conditional** (AES ITN only
  if US origin, CERS only if Canada, TAX IDs only if Mexico, MOT No. only if China +
  NVOCC), not a fixed list applied uniformly. The system distinguishes "booking uploaded"
  from the later "Booking Receipt Notice" — two separate confirmation events.

### Tier2 Systems — "Freight Booking Management: An Ops Guide"
`https://tier2systems.com/en/blog/freight-booking-management-guide/`
Freight-tech vendor blog for forwarder ops staff.
- **Fields:** origin/destination ports, commodity + HS code, gross weight, dimensions,
  container type/count, cargo ready date, special requirements (reefer/hazmat/OOG),
  preferred carrier; confirmation-side: vessel/voyage, ETD/ETA, doc cutoffs; SI submission
  deadline, DG declarations, certificates of origin.
- **Realism note:** states a single shipment "can generate 40 or more messages across its
  lifecycle," 10-20 in the booking phase alone. Real booking correspondence is a thread
  with amendments and re-confirmations, not one clean message — something the generator's
  single-shot model (outside the `forwarded_thread` pathology's one quoted layer) never
  represents.

### freightcourse.com — "How to Book a Container in Shipping"
`https://www.freightcourse.com/how-to-book-a-container-in-shipping/`
Freight-training site walkthrough.
- **Fields:** Shipper, Consignee, Notify Party, cargo type/dimensions/weight, handling
  requirements, load type, Cargo Ready Date, origin/destination, permits, container
  type/quantity, vessel, voyage, ETD/ETA, "Booking Instructions."
- **Note:** calls the resulting document a "booking confirmation (also referred to as
  pro forma booking)... acts like a receipt" — a useful alternate label.

### IncoDocs — "Create and Download a Shipper's Letters of Instruction Document"
`https://incodocs.com/blog/shippers-letters-of-instruction-freight-export/`
Trade-documentation vendor blog on the SLI as a booking companion document (full field
list under Section 4 below).
- **Confirms two fields the generator's flat list omits entirely: seal number and
  shipping marks** — both real, both commonly present in a booking-adjacent document.

*(A related source, `mg-spl.com`'s "What Information Do You Need to Request a Freight
Quote?", gives a terse real-world booking-request example — "FCL sea freight from Ho Chi
Minh / Cat Lai Port, Vietnam to Nhava Sheva, India. 2 × 40'HC containers, general cargo,
ready in early August" — logged fully under Section 2 since that's its primary framing.
Worth noting here: real requests are frequently this compressed, single-paragraph, not a
labeled field block.)*

---

## 2. Rate Requests / Spot Quote Emails

### mg-spl.com (Matrix Global Singapore) — "What Information Do You Need to Request a Freight Quote?"
`https://mg-spl.com/what-information-do-you-need-to-request-a-freight-quote/`
Singapore forwarder's shipper-facing advisory.
- **Fields:** Company name/contact/email/phone/WhatsApp, company type, operating
  location; POL/POD, place of receipt, final delivery; mode (FCL/LCL/air/reefer/DG/other);
  commodity, HS code, cargo value, packaging, fragile/high-value/regulated flags;
  container count/type or package count+weight+dimensions+CBM; cargo ready date,
  preferred shipment week, required arrival period; service scope (port-to-port vs.
  door/customs/insurance included); reefer settings; DG details (UN No., IMO class, MSDS).
- **Realism note:** explicitly warns a bare "Please quote Singapore to India" is
  unusably vague in practice — real incoming requests vary enormously in completeness.
  A realistic corpus needs some genuinely underspecified requests, not just complete ones.

### Freightamigo — "Freight Quote Email Templates: Pro Tips 2026"
`https://www.freightamigo.com/en/blog/logistics/how-to-craft-an-effective-freight-quote-request-email-samples-and-best-practices/`
Digital forwarder blog with two full worked sample RFQ emails.
- **Content:** Sample 1 (domestic LTL) greets **"Dear Freight Team,"**, covers
  pickup/delivery addresses, cargo specs, Incoterms, ready date; signs **"Thanks,
  [Name/Company/Phone]"**; subject **"RFQ - LTL Freight Quote: [qty] [origin] to
  [destination], Ready [date]"**. Sample 2 (international ocean LCL) uses the same
  greeting/sign-off pattern with a **"RFQ - Ocean LCL Quote: [CBM] [origin] to
  [destination]..."** subject.
- **Realism note:** recommends bullet points/short tables over flat prose, and an
  itemized cost breakdown ask (freight + THC + demurrage for ocean; chargeable-weight
  rate for air) rather than a single number — real RFQs often ask for pricing structure,
  not just a total.

### emailsinenglish.com — "Request for Freight Quotation Email"
`https://www.emailsinenglish.com/request-for-freight-quotation-email/`
ESL/business-English reference template.
- **Content:** shows an explicit **To/Bcc/Cc/From/Subject** header block; greeting
  **"Respected Sir/ Madam,"**; deferential register ("at your earliest convenience");
  closing **"Thank you," / "Sincerely,"**.
- **Realism note:** materially more formal/deferential than the Freightamigo sample —
  consistent with South Asian/subcontinent business-English conventions that are common
  in real freight-ops correspondence. "Dear Sir/Madam" persists in shipping specifically
  even where general business-English style guides now call it outdated. Directly
  supports diversifying greeting register beyond the generator's flat "Hi,"/"Hello,".

### sfi.com (Straight Forwarding Inc.) — "How to Ask For a Freight Quote"
`https://sfi.com/blog/how-to-ask-for-a-freight-quote`
US forwarder/broker blog.
- **Fields:** origin (city/ZIP/warehouse/port), destination, weight, dimensions,
  container size, hazmat designation, licensing needs, transit timeframe, ready date.
- **Note:** positions email as the fallback channel behind self-serve quote forms —
  rate requests skew toward less-standardized, more free-form phrasing than carrier
  booking systems.

### Freightos — "Request For Freight Quote"
`https://www.freightos.com/freight-resources/request-for-freight-quote/`
- **Fields:** contact details (both sides), pickup/delivery address, weight (from
  packing list), CBM, ready/delivery dates, mode, HS code (from commercial invoice),
  shipment value, certificate of origin/MSDS/fumigation cert if applicable, insurance
  need, Incoterm, budget/priorities.
- **Realism note:** recommends "for email submissions... copy and paste your prep list
  straight onto the email" — real RFQ emails are frequently a checklist literally pasted
  in, uneven formatting, not polished generated prose.

### Flexport Help Center quoting articles (WebSearch snippets only — 403'd on fetch)
`support.portal.flexport.com/.../International-Freight-only-Quoting-Guide`,
`flexport.com/help/386-...`, `flexport.com/help/382-...`
- Digital-forwarder quoting is structured-form-first, not email-first: freight
  method/shipment/container type, origin as address-or-port, destination as
  fulfillment-center/warehouse, a "flexible timeline" toggle. Reinforces that real rate
  requests range from unstructured shipper emails to structured web forms that only
  become email once an ops rep replies.

---

## 3. Booking Confirmations (Ocean and Air)

### MSC — IFTMBC "Booking Confirmation Message" EDIFACT implementation guide (PDF)
`https://developerportal.msc.com/content/MSC_MIG_EDIFACT_IFTMBC_Booking_Confirmation.pdf`
MSC's own 101-page message spec — EDI, not prose, but the authoritative real-carrier
definition of what a booking confirmation legally carries.
- **Segments/codes:** UNB/UNH/BGM/CTA/COM/DTM/TSR/FTX/CNT/GDS/LOC/RFF/TCC/TDT/NAD/GID/
  HAN/TMP/RNG/TMD/PCD/MEA/EQN/DIM/DOC/DGS/EQD/UNT/UNZ. Concrete example:
  `BGM+770+7685967039:1.2019+6+AP` — doc code **770 = "Booking confirmation"**; response
  codes **AJ = Pending, AP = Accepted, CA = Conditionally accepted**. DTM qualifier
  **265 = "Container(s) VGM cut-off date"**; **407 = "Date by which SI... should be
  received."** TSR service-scope codes: 27 = door-to-door, 28 = door-to-pier, 29 =
  pier-to-door, 30 = pier-to-pier.
- **Realism notes (high value):** (1) confirmations are **3-valued** — Pending / Accepted
  / Conditionally Accepted — not binary confirmed/not; (2) **VGM cut-off** and **SI-due
  date** are explicit, separate deadlines from vessel/port cutoff, all distinct from
  "cargo ready"; (3) service scope is one of four door/pier combinations, not a plain
  origin→destination shorthand.

### freightcourse.com — "What Is a Booking Confirmation in Shipping?"
`https://www.freightcourse.com/booking-confirmation/`
- **Fields:** Booking Reference Number, Shipper/Consignee Details, Cargo & Commodity
  Type, Cargo Weight, Equipment Qty & Type (e.g. "3 x 40' General Purpose Container"),
  Requested Sailing/ETD, ETA, CY Cutoff, Vessel Name & Voyage Number, POL, POD,
  Transshipment Port, Special Remarks.
- **Worked example:** LA→Melbourne, reference **BHK51332862** (2 letters + 8 digits, no
  hyphen), vessel **OOCL California**, transshipping through Shanghai — a real-feeling
  reference format and an explicit transshipment leg, neither modeled today.

### Freightos — "Booking Confirmation Document" (glossary)
`https://www.freightos.com/glossary/booking-confirmation/`
- Frames it as "a receipt for the main shipment leg," notes the booking number often
  becomes the main tracking code, and — important structurally — the shipper-facing
  confirmation usually **re-states** the carrier's own confirmation via the forwarder,
  so a forwarder confirmation plausibly carries a "carrier booking no." field distinct
  from its own file/job number.

### Freightlink (UK) — booking confirmation FAQ
`https://www.freightlink.co.uk/knowledge/faq/how-do-i-get-confirmation-my-booking`
- States the on-screen "thank you" page after an online booking is explicitly **not**
  the confirmation — the real confirmation is a follow-up email, with a documented gap
  between "received your request" and "confirmed." Mirrors ONE's own distinction between
  "booking uploaded" and "Booking Receipt Notice."

### IAG Cargo — "eBooking guide" (air)
`https://www.iagcargo.com/en/e-booking-guide/`
- **Fields:** AWB number (formats: "125-0000000" / "075-0000000"); origin/destination;
  preferred ship date; commodity code; load type; weight per piece; unit type (e.g.
  "PMC Lower Deck"); booking type (Free sale / Allotments — BSA/CPA/Permanent); **named
  product tiers** (Perform, Prioritise, Constant Fresh, Constant Climate Passive); rate
  type (Standard/Flex); flight number; handling flags (non-stackable, non-turnable, DG,
  battery ELM/ELI codes, dry-ice).
- **Realism note:** named airline product tiers would realistically appear as a field
  value on a real air confirmation — a generic "Mode: Air" flattens this completely.

### Freightos — "Air Waybill (AWB): Meaning, Number, Types, and Examples"
`https://www.freightos.com/freight-resources/air-waybill-awb/`
- Worked AWB number **99953729071** = 999 (neutral prefix) + 5372907 (serial) + 1
  (check digit = serial mod 7). Confirms 8 colour-coded physical AWB copies exist.
  The check-digit rule is directly implementable and verifiable — unlike the
  generator's current random-looking `BK-#####`.

### DocShipper — "Booking Number: Definition & Guide" (low confidence — flagged)
`https://docshipper.com/glossary/booking-number-definition-logistics/`
- States booking confirmation "typically occurs within 15 minutes to 48 hours" and that
  the booking number recurs across invoice, packing list, VGM, SLI, and customs filings
  (plausible, consistent with other sources). **But** the specific carrier-prefixed
  example strings it returned ("MAEU123456789," "MSCU2024987654") look like the fetch
  tool's own container-number-shaped invention rather than verified booking-number
  format — do not use those digit strings as ground truth.

### Cross-cutting structural note (pattern-level, multiple sources)
A generic confidentiality-footer pattern recurs across disclaimer-template sites
("This email and any attachments are intended only for..."), but **no source
specifically confirmed this wording on a named freight forwarder's own confirmation
email** — treat as a plausible generic register to sample from, not a verified
freight-specific quote. Closest evidence found for the "no legal disclaimers" gap; still
genuinely thin.

---

## 4. Shipping Instructions / SLI

*Two genuinely different documents share the "SLI"/"SI" name — see the realism note at
the end of this section.*

### NTCBFFA — specimen "Shipper's Letter of Instructions (SLI)" (PDF)
`https://ntcbffa.org/ftp/webdocs/DCB_SLI_NTCBFFA.pdf`
A filled-in specimen of the widely-circulated NCBFAA-descended US export-compliance SLI.
- **All 40 numbered boxes, in order:** (1) USPPI Name (2) USPPI Contact Name (3) USPPI
  Contact Phone (4) USPPI EIN (5) USPPI Address (6) Freight Location Address (7) State
  of Origin (8) Shipment Reference Number (9) Mode of Transportation (Air/Vessel/Rail/
  Truck/Other) (10) Carrier Code per mode (IATA/SCAC) (11) Carrier/Vessel Name per mode
  (12) Containerized? per mode (13) Transportation Reference # (AWB in ###-######## mask
  / Booking #) (14) Port of Unlading (15) Port of Export (16) Hazmat? Y/N (17)
  USPPI/Ultimate-Consignee related? Y/N (18) Routed Export Transaction? Y/N (19) Ultimate
  Consignee Name & Address (20) Ultimate Consignee Type (21) Country of Ultimate
  Destination (22) Date of Export (23) In-Bond Code (24) In-bond Entry Number (25) FTZ
  Identifier (26) Domestic/Foreign per line (27) Schedule B/HTS Number & Description
  (vehicles: VIN/Year/Make/Model) (28) Quantity in Schedule B/HTS units (29) Shipping
  Weight kg (30) ECCN/EAR99/USML Category (31) Export Information Code (32) Export
  License No./Exception Symbol/DDTC Exemption/DDTC ACM/NLR (33) Value in whole USD (34)
  License Value by item (35) Additional PGA info (AMS/ATF/DEA/EPA/FWS/NMFS/TTB
  checkboxes) (36) Certification checkbox (37) Printed Name (38) Title (39) Signature
  (40) Date — plus a free-text Notes box.
- **Realism notes:** dense single-page grid form, not prose — closer to a customs filing
  than an email. Boxes 9-13 form a **multi-mode sub-grid** (a single SLI can carry
  Air+Vessel+Rail+Truck data side by side). Commodity lines (26-34) **repeat per HTS
  line item** — the generator's single flat commodity field can't represent a multi-line
  shipment. Structured codes present: EIN, SCAC, Schedule B/HTS, ECCN/EAR99/USML, DDTC
  exemption codes, "NLR" (No License Required).

### IncoDocs — "Create a Shipper's Letter of Instruction (SLI) [Free Template]"
`https://incodocs.com/template/shippers_letter_of_instruction`
- **Fields:** Shipper/Consignee/Notify Party/Forwarding Agent details, product
  description, package count/type, gross weight (kg), measurement (m³), shipping marks
  and numbers, hazardous-goods declaration, L/C status, POL/POD, dispatch method
  (sea/air/road/rail), shipment type (FCL/LCL/breakbulk), pickup requirement, freight
  terms (prepaid/collect), authorized signatory, company seal/stamp.
- **Realism note:** this is the "commercial/logistics" flavor of SLI (Incoterm, FCL/LCL,
  marks & numbers) vs. NTCBFFA's "customs/export-filing" flavor (EIN, ECCN, Schedule B).
  A realistic generator should pick one flavor deliberately, not blend both incoherently.

### NCBFAA — "Shipper's Letter of Instruction Model" (page, form itself is gated)
`https://www.ncbfaa.org/membership-benefits/shipper's-letter-of-instruction-model`
- Confirms NCBFAA is the current custodian of "the" model SLI referenced
  industry-wide, but explicitly states it's a **recommended format only** — member
  companies customize field numbering/wording/delivery mechanism freely. **Important:**
  there is no single rigid universal SLI layout; the underlying *data elements* (USPPI
  identity/EIN, ultimate consignee, HTS/Schedule B, ECCN, routed-transaction flag, hazmat
  flag) are stable because they map to mandatory AES/EEI filing requirements, even though
  exact form layout varies.

### Carrier-side "Shipping Instructions" — distinct from the shipper's SLI (WebSearch snippets only, fetches blocked)
Hapag-Lloyd (`hapag-lloyd.com/.../shipping-instructions.html`), MSC (`mscmkt3.com/.../MyMSC_ShippingInstruction.pdf`), CMA CGM (`cma-cgm.com/.../Shipping instructions format...pdf`) — all 403/502'd on direct fetch.
- Per snippets: these are carrier web-portal forms submitted **to the carrier**
  (not the forwarder) to feed B/L preparation. Hapag-Lloyd's requires Shipper/Consignee/
  Notify + a comments field + Container/Seal Number per container. MSC's covers booking
  reference, vessel, payment terms, B/L info, per-container detail, and names specific
  amendment reason codes ("Split B/L," "Seal Change due to physical inspection," "Typing
  Error").
- **Critical distinction for the generator:** "Shipping Instructions" (carrier-portal
  term, feeds the B/L) and "Shipper's Letter of Instruction / SLI" (forwarder-facing,
  authorizes AES export filing) are **two different documents that share a confusingly
  similar name**. A realistic corpus should treat them as distinct types with distinct
  field sets, not one.

---

## 5. HAWB / MAWB (House / Master Air Waybill)

### eAWBlink — "5 Create Air Waybill" user guide
`https://www.eawblink.org/UserGuide/5_Create_Air_Waybill.htm`
Walks every data-entry field on a standard IATA-layout AWB — the richest field-level
source in this cluster.
- **17 field groups, in form order:** AWB Number; Template; Shipper's Name & Address;
  Issuing Carrier's Name & Address; Consignee's Name & Address; Accounting Information;
  Issuing Carrier's Agent Name & City; Shipping Information (Reference No., Optional
  Shipping Info); Requested Routing (departure/destination airport, carrier code, flight
  no., dates); Charges Information (Currency, Charges Codes, Weight & Valuation Charge,
  Other Charges, Declared Value for Carriage, Declared Value for Customs, Amount of
  Insurance); Also Notify; Handling Information (**SPH/SCI/SSR/OSI/OCI** codes with
  Country Code + Info Identifier); Consignment Rating Details (Pieces, RCP, Gross Weight,
  Rate Class Code, Commodity Item No., Harmonized Commodity Code, Chargeable Weight,
  Rate/Charge, Goods Description, Dimensions, Volume, ULD info, SLAC); Charge Summary
  (auto-computed); Other Charges; Shipper Certification; Charges Collect Summary
  (Destination Currency, Conversion Rates, CC Charges).
- **Realism note:** the generator's flat "Shipper/Consignee/Commodity/Pieces/Gross
  weight/Volume" corresponds to a small slice of just 3 of these 17 groups — nothing for
  Accounting Information, the SPH/SCI/SSR/OSI/OCI handling codes, Rate Class Code, ULD
  info, or the two-tier Charges/Charges-Collect structure.

### DAKOSY — "Cargo-IMP Amendments for ZAPP-Air / Message FWB" v1.6.1e (PDF)
`https://www.dakosy.de/fileadmin/Redakteur/Support/Dokumentation/Entwicklerdokumentation/EDI/ZAPP-Air/FWB_v161_en.pdf`
German air-cargo community-system's technical spec for the Cargo-IMP **FWB** message —
the electronic form of a Master AWB.
- **Segment order (tag — name — occurrence):** FWB (Std Msg ID) → AWB Consignment
  Details → ZEV/ZPI (community-specific envelope/processing info) → FLT (Flight
  Bookings) → TRK (Trucking, 0-1) → SEC (Security, 0-1) → RTG (Routing) → SHP (Shipper) →
  CNE (Consignee) → AGT (Agent, 0-1) → ZFC (community-specific forwarder contact) → SSR
  (Special Service Request, 0-1) → NFY (Also Notify, 0-1) → ACC (Accounting, 0-1) → CVD
  (Charge Declarations) → *(spec continues beyond what was retrieved)*.
- **Format rules:** capital A-Z + digits + `.`/`-`/space only, no diacritics; max 70-char
  lines with `/`-prefixed continuations; whole message wrapped in a UN/EDIFACT
  UNB/UNH...UNT/UNZ envelope; structured 7-field "PIMA" addressing. **This is the
  clearest evidence that a real e-AWB is a structured EDI record with M/O/D/X occurrence
  rules, not free text.**

### IATA Resolution 600b — "Air Waybill — Conditions of Contract" (PDF)
`https://www.iata.org/contentassets/783ac75f30d74e32a8eaef26af5696b6/csc-600b-en-28dec2019.pdf`
The official IATA resolution defining the legal notice on every AWB face and the 12
numbered clauses on the reverse.
- **Structure:** Part I = short "Notice" on the face (acceptance subject to reverse
  conditions, carrier's routing discretion, liability-cap pointer). Part II = 12
  numbered clauses on the reverse (definitions; Warsaw/Montreal applicability;
  incorporation of carrier tariffs by reference; agreed stopping places; **default
  liability cap of 22 SDRs/kg** absent a higher declared value; shipper's payment
  guarantee; right to declare higher value for a fee; partial-loss apportionment; claim
  time limits — **14 days damage, 21 days delay, 120 days non-delivery, 2-year suit
  limit**; compliance obligations).
- **Realism note:** confirms a hard front/back split — variable data grid up front,
  virtually-invariant legal boilerplate on the back. A generator "quoting" an AWB
  realistically should treat this block as a static template, not something regenerated
  per shipment.

### LegalClarity — "Air Waybill (AWB): Definition, Legal Requirements, and Data"
`https://legalclarity.org/air-waybill-awb-definition-legal-requirements-and-data/`
- Confirms minimum 8 copies/colours (green=carrier retained, pink=consignee, blue=
  shipper, rest for customs/delivery/admin). Confirms the MAWB/HAWB functional split but
  gives no box-level layout or check-digit formula.

### AltexSoft — "Air Waybill (AWB) and e-AWB Explained"
`https://www.altexsoft.com/blog/awb-air-waybill/`
- Confirms 11-digit format (3-digit prefix + 7-digit serial + check digit = serial mod
  7). MAWBs print on the carrier's own branded form; HAWBs use a neutral, unbranded form.

### AWB check-digit algorithm (cross-confirmed, multiple sources)
Australian Border Force official page, freight.domains calculator, airwaybilltracker.com
- **AWB number = `XXX-XXXXXXX-X`**: 3-digit IATA airline prefix (e.g. 020 = Lufthansa
  Cargo) + 7-digit serial + check digit = **serial mod 7** (unweighted). Worked example:
  999-5372907-1 (5372907 ÷ 7 remainder = 1, matches). **A trailing check digit of 7, 8,
  or 9 is mathematically impossible** — a clean, implementable validity rule a generator
  could enforce, or deliberately violate for a new "malformed AWB" pathology.

### MAWB vs HAWB (WebSearch snippets: Ship4wd, gocargonet, howtoexportimport, tlstechno)
- MAWB (airline→forwarder) shows total consolidated weight/volume, drives airline
  billing/customs/ops. HAWB (forwarder→each shipper) carries more granular detail and is
  each shipper's own customs-clearance reference. Same one-master/many-house nesting as
  ocean B/Ls.

---

## 6. House / Master Bill of Lading

### DCSA — "Standard for the Bill of Lading: A roadmap towards eDocumentation" (PDF, Dec 2020)
`https://www.digitalizetrade.org/files/projects/documents/20201208-DCSA-P4-DCSA-Standard-for-Bill-of-Lading-v1.0-FINAL.pdf`
The Digital Container Shipping Association's (Maersk/MSC/Hapag-Lloyd/ONE/CMA CGM/COSCO/
Evergreen/HMM/Yang Ming/ZIM-backed) published data standard for the ocean B/L, covering
both physical and electronic (eBL/eSWB) forms. **The single most useful find in this
whole research pass.**
- **Standardized field categories:** **Party** — Shipper, Consignee, Notify party, Also
  notify, Shipper/Consignee forwarding agent + reference number, Freight payer, SCAC
  code, Tax ID/LEI, Address/Phone/Email/Fax, Consignee reference number. **Transport
  document** — Date/Place of issue, doc number, # of originals, issuer, signature,
  onboard date, terms, disclaimer, doc type, # copies. **Shipment** — Place of Receipt,
  POL, POD, Place of Delivery, declared value, service type, shipment terms, onward
  inland routing, precarried by, export ref number, origin, carrier booking number.
  **Vessel** — Vessel, Voyage number. **Cargo item** — Marks & numbers, description,
  measurement, container/package count, HS code, gross weight, reefer humidity/
  temperature/ventilation, part-load indicator. **Shipment equipment** — VGM, total
  container weight, tare weight, container type/number. **Seal** — number, source.
  **Charges** — prepaid/collect amounts, freight & charges, payable-at location,
  currency. **Carrier clauses**; **Booking** — service contract, commodity.
- **The killer feature:** every field carries a Mandatory/Conditional/Optional status
  **per process step** (Booking request → Booking confirmation → Prepare B/L → Issue
  B/L). Example given directly: Shipper is mandatory at every step; Onward Inland Routing
  is conditional (only if the customer arranges onward transport); Also Notify is
  optional throughout. Full appendix table structure: `# | Field | UN Assigned ID |
  Current definition | Data input format | 1.1 Booking request | 1.2 Booking
  confirmation | 1.3 Prepare B/L | Conditions | 1.4 Issue B/L`.
- This is exactly the kind of ground truth a generator needs to model realistic
  *omissions* (blank Consignee for a "to order" B/L, blank Notify Party, conditional
  Onward Inland Routing) instead of guessing which fields are "usually" blank.

### FIATA Standards presentation (CAREC/CFCFA training deck, PDF, 2013)
`https://www.carecprogram.org/uploads/Module-06-FIATA-Standards.pdf`
Embeds a full specimen **FBL** (FIATA Multimodal Transport B/L) form image.
- **The 8 FIATA standard documents:** FBL (negotiable multimodal B/L), FWB (FIATA's own
  non-negotiable waybill — **name-collides** with IATA/Cargo-IMP's air-cargo FWB, an
  unrelated message, see Section 5), FCR (Forwarders Certificate of Receipt), FCT
  (Forwarders Certificate of Transport), FWR (Warehouse Receipt), SDT (Shippers
  Declaration for DG Transport), FFI (Forwarding Instructions), SIC (Shippers Intermodal
  Weight Certificate).
- **Specimen FBL fields, top to bottom:** Consignor; FBL No.; Consigned to order of;
  Notify address; Place of receipt; Ocean vessel; POL; POD; Place of delivery; Marks and
  numbers; Number and kind of packages; Description of goods; Gross weight; Measurement;
  Declaration of Interest in timely delivery (Clause 6.2); Declared value for ad valorem
  rate (Clauses 7-8); negotiability/liability boilerplate; Freight amount; Freight
  payable at; Place and date of issue; Cargo insurance checkboxes; Number of Originals;
  Stamp/signatures; printed serial number.
- **Issuance rules:** only qualifying FIATA-member national associations may issue FBLs;
  continuous serial numbers required; issuer must stamp the association seal and carry
  forwarder liability insurance; English is the legally controlling text; validity is
  **5 years**, auto-renewing unless 6 months' notice is given; in active use across ~45
  named countries. The FBL is conceptually the FIATA-standard analog of a House B/L, even
  though issued by a forwarder taking on carrier-like liability.

### Maersk sample Bill of Lading (specimen PDF, third-party-hosted)
`https://africactn.com/staging/wp-content/uploads/2023/02/Example-Maersk-BIll-of-Lading.pdf`
A blank Maersk-named specimen, full text recovered.
- **Fields by region:** top-right **SCAC / B/L No.**; **Booking No.**; **Export
  references / Svc Contract**; **Onward inland routing** (captioned "For account and
  risk of Merchant"); **Vessel / Voyage No. / Place of Receipt** (multimodal-only,
  captioned as such); **Port of Discharge / Place of Delivery** (same caption); a single
  wide **"PARTICULARS FURNISHED BY SHIPPER"** box combining Kind of Packages +
  Description of goods + Marks and Numbers + Container No./Seal No. into **one free-text
  cell**, with only Weight and Measurement as separate columns; **Freight & Charges /
  Rate / Unit / Currency / Prepaid / Collect**; **Carrier's Receipt / Place of Issue**;
  **Number & Sequence of Original B(s)/L / Date of Issue**; **Declared Value / Shipped on
  Board Date**; Forwarder + Carrier signature blocks; a dense "SHIPPED, as far as
  ascertained..." boilerplate paragraph referencing 26 numbered reverse-side clauses.
- **Notable wrinkle:** Shipper/Consignee/Notify Party are **unlabeled blank boxes** at
  the top — conveyed by position/convention, not printed captions. A synthetic generator
  would never guess this without seeing a real specimen.

### exportnesthub — "How to Read a Bill of Lading: Field-by-Field Guide"
`https://exportnesthub.com/how-to-read-bill-of-lading/`
- Full field walkthrough (Shipper, Consignee, Notify Party, B/L Number, Booking Number,
  Carrier/Forwarder, Vessel, Voyage, Place of Receipt, POL, POD, Place of Delivery,
  Container/Seal Number, Marks and Numbers, Packages, Goods, HS Code, Gross Weight, CBM,
  Freight Terms, # Originals, Place/Date of Issue, Signature).
- **Container number format:** ISO 6346 — 3-letter owner code + 1-letter equipment
  category + 6 serial digits + 1 check digit (example: "MSCU 123456 7") — precise and
  checkable, complementary to the AWB's mod-7 rule.

### iContainers — "House and Master Bill of Lading: A Complete Guide"
`https://www.icontainers.com/help/differences-between-house-master-bill-of-lading/`
- Master B/L: carrier→NVOCC, on the carrier's own form, Shipper=NVOCC/agent,
  Consignee=destination agent/NVOCC. House B/L: NVOCC→customer, on the NVOCC's own form,
  Shipper=actual exporter, Consignee=actual importer. **All other fields (vessel,
  cargo description, container/seal numbers, weight, sail date) must be identical
  between the two for the same cargo** — a directly implementable consistency rule, and
  a deliberate mismatch is a ready-made new pathology.

### B/L number format (docs.vizionapi.com, plus WebSearch on SCAC/CBP conventions)
`https://docs.vizionapi.com/docs/formatting-bl`
- No universal numeric format exists (unlike the AWB's strict rule) — each carrier has
  its own. Patterns cited: pure 9-12 digit numeric (Maersk/OOCL-style), 3 letters +
  7-9 digits (APL/CMA CGM-style), SCAC + 13 chars (Hapag-Lloyd-style, "HLCU..."). US
  customs manifest rules cap the identifier at 16 characters (4-char SCAC + up to 12
  more); Ocean House B/Ls are always required to carry a SCAC as part of the number.
  **Practical implication:** realism here comes from mimicking a specific carrier's known
  SCAC+format, not inventing an arbitrary string.

---

## 7. Commercial Invoice & Packing List

### Cornell Law LII mirror of 19 CFR § 142.6 (US release-stage invoice requirement)
`https://www.law.cornell.edu/cfr/text/19/142.6`
- **Minimal release-stage fields:** adequate description, quantities, values/approximate
  values, HTS classification (8-digit, waivable at release, required later at entry
  summary), name/address of the invoicing foreign party.
- **Note:** the fuller invoice data set (§§141.86-141.89, ~11 categories) can be supplied
  later at entry summary — i.e. a commercial invoice is legitimately a **two-stage**
  document (fields required now vs. fields that trail behind), not one flat
  always-complete form.

### trade.gov — "Commercial Invoice" (US Dept. of Commerce/ITA)
`https://www.trade.gov/commercial-invoice`
- HS code flagged optional-but-recommended; recommends a standing **"destination control
  statement"** clause protecting against diversion to restricted destinations — fixed
  boilerplate text, not a data field, that a realistic invoice generator currently omits.

### UK gov business.gov.uk — export invoice guidance
`https://www.business.gov.uk/export-from-uk/learn/categories/funding-financing-and-getting-paid/get-paid/how-create-export-invoice/`
- **15-item checklist:** invoice number+date; seller details; buyer details; consignee
  details **(explicitly separate from buyer)**; related-paperwork references (proforma/
  PO/contract number+date); unit price/payment method/currency/discounts;
  gross/net weight+package details; HS code+description; Incoterms; packaging marks
  ("1 of 6 boxes" convention); country of origin; transport details; total value;
  additional charges; language/certification.
- **Realism notes:** buyer and consignee are explicitly separate roles (many generators
  collapse them, unrealistic for door shipments to a different receiving address than
  the paying party); marks follow an "N of M" formatting convention.

### IncoDocs — "How to Create and Download a Packing List for Export Shipments"
`https://incodocs.com/blog/packing-list-document-template-export-import-shipping/`
- **Fields by group:** Exporter (name/logo/address/phone/registration numbers);
  Consignee & buyer (each, if different); Shipping details (dispatch method, FCL/LCL/
  Breakbulk, origin/destination country, vessel/aircraft, voyage no., POL, departure
  date, POD); References (invoice number+date, B/L number, buyer's PO, delivery notes);
  Product/packaging (code, description, quantity, "kind & number of packages" e.g.
  "Pallet x 12", net weight kg, gross weight kg, m³); Signature (company, signatory,
  digital signature/stamp).
- **Note:** a genuinely distinct field taxonomy from the invoice — volumetric
  measurement (m³), FCL/LCL/Breakbulk flag, and net-vs-gross weight split are packing-
  list-canonical, not invoice fields.

### EU customs commercial invoice/packing list requirements (WebSearch synthesis)
Anchored on `https://trade.ec.europa.eu/access-to-markets/en/content/additional-customs-clearance-documents`
- EU importer's **EORI number**; 8-digit HS code per line; unit+total value; Incoterms
  2020 with **named place**; invoice number/date/payment terms. Packing list:
  package-by-package gross/net weight, dimensions, marks, contents.
- **Structural fact worth encoding as a pathology:** EU guidance stresses **package
  count and gross weight on the invoice must match the packing list exactly**, and
  consignee name/address must be identical across invoice, packing list, and transport
  document. A deliberate mismatch (invoice says 12 cartons, packing list says 11) is a
  ready-made new "cross-document conflict" pathology, distinct from the existing
  body-vs-attachment `weight_conflict`.

---

## 8. Arrival Notices & Pre-Alerts

### Maersk Insights — "Your cargo has arrived: Understanding arrival notice in ocean freight shipping"
`https://www.maersk.com/insights/digitalisation/2024/11/15/arrival-notice`
- Carries customs-relevant info echoed from the B/L and invoice; **per-container free
  time and last free day**; an itemized demurrage estimate through expected gate-out.
- **Note:** an arrival notice is not just "cargo is here" — it doubles as a financial-
  deadline document. A generator modeling only ETA/container fields misses the
  charges-and-deadline block entirely.

### Freightos Glossary — "What is an Arrival Notice?"
`https://www.freightos.com/glossary/what-is-an-arrival-notice/`
- **Fields:** vessel name (called out separately from voyage number), B/L number,
  container number, cargo description, package count, weight, arrival date, **location
  of goods** (which terminal/CFS/warehouse — distinct from port of discharge),
  release instructions/requirements, charges due before release. Sender: carrier or
  handling forwarder → consignee/notify party/importer of record.

### Extensiv Glossary — "Arrival Notice"
`https://www.extensiv.com/glossary/arrival-notice`
- Contact info, goods description, units arrived, charges due at pickup, Incoterms/
  port/tariff details, customs docs needed, ETA.
- **Note:** states arrival notices commonly go out **3-5 days before ETA**, not
  strictly after — blurring the line with a pre-alert. In practice the two document
  types overlap in timing more than a hard taxonomy suggests.

### Pre-alert (WebSearch synthesis: terminal49.com, freightcourse.com, luwjistik.com)
- A pre-alert is sent by the **origin** forwarder to the **destination**
  forwarder/broker (sometimes cc'ing the consignee) at/shortly after departure —
  the opposite timeline end from an arrival notice. Typical bundle: B/L, commercial
  invoice, packing list, certificates, plus ETA/container/terminal info. Purpose:
  lead time for destination doc verification/customs pre-filing, and consignee
  planning visibility.
- **Structural note for the generator:** a pre-alert is fundamentally a **cover email
  bundling documents generated elsewhere**, not a document with its own unique field
  schema. It would plausibly reference attachments by name and repeat only a subset of
  key fields (B/L number, ETA, container numbers) inline — a texture the current
  generator's single rigid "Field: value" format doesn't produce.

---

## 9. Dangerous Goods Declarations

### ShippingSolutions Software — "Creating the IATA Dangerous Goods Form: The Shipper's Declaration for Dangerous Goods"
`https://shippingsolutionssoftware.com/blog/creating-the-iata-dangerous-goods-form-the-shippers-declaration-for-dangerous-goods`
Field-by-field walkthrough of the IATA DGD (IATA's own fillable PDF failed to parse).
- **Header:** Shipper, Consignee, AWB Number, "Page __ of __," Shipper's Reference
  (optional), Transport Details (passenger+cargo vs. cargo-only aircraft), Airport of
  Departure/Destination, Shipment Type (Radioactive/Non-Radioactive).
- **"Nature and Quantity of Dangerous Goods" table, per line:** UN/ID number, Proper
  Shipping Name, Class/Division + subsidiary risk, Packing Group, # packages + type,
  net quantity/package, gross weight, "Overpack Used," Packing Instruction code,
  Special Provision number(s) (prefix "A").
- Plus: Handling Information, **Emergency response phone number** (required for
  US-touching shipments), signature block, and a fixed certification statement.
- **Realism note (high value):** the DG table has a **fixed column grammar** (UN No. /
  Proper Shipping Name / Class-Division / Packing Group, then Qty-Type-Instruction-
  Authorization) — a table, not a flat key:value list. Reproducing that grammar is what
  makes a synthetic DGD look real rather than a repurposed invoice template.

### DGM-US — "Shipper's Declaration for Dangerous Goods"
`https://www.dgm-us.com/dangerous-goods-declarations/`
- Corroborates the air-side field set. Ocean/IMO side described only at process level
  on this page (see MCA source below for the real structural detail).

### UK Maritime & Coastguard Agency (gov.uk) — MCA guidance on container packing certificates for DG notes
`https://www.gov.uk/guidance/mca-guidance-for-container-packing-certificated-on-dangerous-goods-notes`
Official UK regulator interpreting IMDG Code §5.4.1.6/§5.4.2.1 — the strongest ocean-DG
source found.
- **Key structural fact:** ocean DG shipments require **two distinct certifications** —
  the DG declaration itself, and a separate **container/vehicle packing certificate**
  (clean/dry/suitable container, segregation maintained, packages inspected, drums
  braced upright, bulk goods evenly distributed, marking/labeling/placarding correct,
  container ID stated) — which may be combined into one document or must be physically
  attached if separate. Signing responsibility falls to whoever physically packed the
  load (consignor, consolidator, carrier, or forwarder — not necessarily "the shipper").
  **This has no air-side analog.**

### IMO — IMDG Code overview page
`https://www.imo.org/en/ourwork/safety/pages/dangerousgoods-default.aspx`
- IMDG mandatory under SOLAS since 1 Jan 2004. Points to Chapter 3.2 (Dangerous Goods
  List), 7.2 (segregation), 5.4 (the Multimodal DG Form) — citable section numbers a
  synthetic ocean-DG document could plausibly reference.

### Cornell Law LII mirror of 49 CFR § 173.185 (US lithium battery regulation)
`https://www.law.cornell.edu/cfr/text/49/173.185`
The most precise regulatory source in the whole pass (PHMSA's own site 403'd).
- **UN numbers:** UN3090 (lithium metal), **UN3480** (lithium-ion standalone), UN3091
  (lithium metal in/with equipment), **UN3481** (lithium-ion in/with equipment).
  **Lithium battery mark:** hatched-border rectangle/square, min 100mm×100mm, red
  hatching + black text on white/contrasting background, showing the applicable UN
  number(s). Restricted-transport marking text: **"LITHIUM BATTERIES—FORBIDDEN FOR
  TRANSPORT ABOARD PASSENGER AIRCRAFT"** / "CARGO AIRCRAFT ONLY," depending on threshold.
  Documentation carve-outs exist (button cells in equipment, ≤2 packages of limited
  cells in equipment, certain small-cell exceptions, disposal/recycling shipments).
- **Realism note (directly maps to the `dg_undeclared` pathology):** shows "no DGD
  required" is a **real, narrowly-scoped exception**, not a blanket rule — a realistic
  pathology should have the sender's claim hinge on a plausible-but-wrong reading of one
  of these carve-outs, not an unqualified assertion.

### CMA CGM Multimodal Dangerous Goods Form (WebSearch, PDF not independently parsed)
`https://www.cma-cgm.com/assets/public/pdf/DG%20FORM%20BLANK%2028112017.pdf`
- Real carrier's combined DG declaration/packing-certificate form. Fields: shipper +
  24-hr emergency contact, container ID, transport document number, vessel/flight,
  goods description, packaging, container/vehicle ID, certifications; DG-specific:
  proper shipping name, hazard class, UN number, packing group, **marine pollutant
  designation** (ocean-only, no air equivalent — something a mode-agnostic
  `dangerous_goods: bool` can't represent).

### Lithium battery UN3480/UN3481 Section II rules (WebSearch synthesis: aeroclass.org, freightamigo.com, shipmercury.com, others)
- UN3480 = standalone lithium-ion; UN3481 = packed with/installed in equipment.
  "Section II" relaxed provision caps a consignment at **one package** (PI965/PI968);
  many carriers refuse Section II shipments outright regardless of regulatory
  allowance; industry is shifting toward requiring full Section IA/IB (UN-certified
  packaging) even where Section II technically applies. UN3480 cells: ≤30% state of
  charge cap for air; that cap **does not formally apply to UN3481** or lithium-metal,
  though some carriers apply it voluntarily anyway.
- **This is the single most useful DG finding for the `dg_undeclared` pathology**: a
  realistic "no DGD needed" claim for lithium batteries would plausibly say "shipped
  under Section II, no DGD required" or "reduced state of charge, exempt" — historically
  true-ish for narrow cases, increasingly rejected in practice, and easy to get subtly
  wrong (misapplying the one-package cap, or conflating UN3480's SOC exemption with
  UN3481, which doesn't get it). Far harder to catch than a generic, unqualified "no DG
  needed" sentence.

### 24-hour emergency response number requirement (WebSearch synthesis, citing 49 CFR 172.604)
- Must be a **monitored, live-answered** number (not voicemail/beeper), the responder
  must know the specific hazmat or have immediate access to someone who does; required
  for DG shipments to/from/within/transiting the US whenever a shipping paper is
  required at all. Third-party emergency-response contract services are common but must
  be formally registered before use.
- **Realism note:** a subtle non-compliance pathology — a declaration listing a normal
  office number (unmonitored after hours) as the "24-hour" contact.

---

## 10. VGM Declarations (SOLAS)

### IMO — "Verification of the gross mass of a packed container"
`https://www.imo.org/en/ourwork/safety/pages/verification-of-the-gross-mass.aspx`
- Shipper bears primary responsibility for providing verified weight, stating it in a
  shipping document, and submitting it to the master/master's rep and the terminal rep
  with enough lead time for the stowage plan. **Method 1** = weigh the packed container
  whole. **Method 2** = weigh all packages/cargo/dunnage individually + add container
  tare, via a competent-authority-certified method. Master retains discretion to refuse
  loading without VGM. Effective 1 July 2016.

### IncoDocs — "The SOLAS VGM regulations explained"
`https://incodocs.com/blog/vgm-solas-verified-gross-mass-declaration/`
The clearest VGM field checklist found.
- **Fields:** Exporter name/address/contact, shipper's reference number, verification
  method used (1 or 2), total VGM (kg), container ID number, vessel name + voyage,
  issue location + date, signatory organization + name/date/signature.
- **Formula:** Method 2 = Cargo Gross Weight + Container Tare Weight = VGM.
- **Note:** VGM is submitted **per container**, keyed to a specific container ID and
  vessel/voyage — not per shipment or booking. A multi-container shipment needs one VGM
  record per container.

### Maersk — "SOLAS VGM Requirement" article (WebSearch snippet — fetch timed out)
`https://www.maersk.com/news/articles/2020/04/22/solas-vgm-requirement`
- Corroborates IMO's page. Method 2's container tare is read from a **physical marking
  stenciled on the container door end** (the CSC plate) — Method 2 shippers reference a
  real physical data source, not an invented number. Method 2 flagged impractical for
  bulk commodities (scrap, grain), needing local-authority permission to use.

### MSC VGM submission requirements (msc.com, rosecontainerline.com — WebSearch synthesis)
- Before submission MSC requires confirmation of booking number, container number,
  **seal number**, vessel/voyage, shipper info, cut-off time. Channels: myMSC (free),
  EDI (INTTRA/GT Nexus/CargoSmart), manual entry, or email (**$25-per-container manual
  fee**). Seal number is a cross-reference field not mentioned by other VGM sources.

---

## 11. EDI Message Samples

*Segment tables sourced from Stedi's EDIFACT documentation (mirrors the UN/EDIFACT
spec text; the official UNECE host 403'd on direct fetch) and cross-checked against
WebSearch snippets of the official spec.*

### UN/EDIFACT IFTMIN (Instruction Message)
`https://www.stedi.com/edi/edifact/messages/IFTMIN` (Release D21A)
- **Purpose (spec text):** a message from the party issuing forwarding/transport
  instructions to the party arranging those services.
- **Segment structure:** header UNH/BGM/CTA/COM/DTM/TSR/CUX/MOA/FTX/CNT/DOC/GDS, then
  ~13 nested segment groups: Group 1 LOC+DTM (locations, repeat 99); Group 2 TOD+LOC
  (terms of delivery); Group 3 RFF+DTM (references, repeat 999); Group 4 GOR+DTM/LOC/
  SEL/FTX (governmental requirements) w/ nested DOC+DTM; Group 6 CPI+RFF/CUX/LOC/MOA
  (charge payment instructions); Group 7 TCC+... (charge/rate calc); Group 8 TDT+DTM
  (transport/main-leg) w/ nested TSR+SCC, LOC+DTM, RFF+DTM; Group 12 NAD+LOC/MOA (party)
  w/ 6 further nested subgroups; Group 19 EFI (external file ID); **Group 20 GID+...**
  (goods item, repeat up to 99999) with a large nested block including MEA+EQN
  (measurements), DIM+EQN (dimensions), PCI (package ID, repeat 999), and **Group 34
  DGS+FTX (dangerous goods, repeat 99)**; **Group 39 EQD** (equipment/container, repeat
  999) with its own nested TCC/NAD/EQA/DGS blocks. UNT trailer.
- **Realism note:** IFTMIN maps closely onto FreightBench's 35 fields — BGM=booking
  reference, NAD=shipper/consignee/notify, LOC=origin/destination, DTM=dates, TDT=
  vessel/flight/carrier, GID/MEA/DIM=cargo/weight/dimensions, EQD=container, DGS=
  dangerous goods, RFF=references — but the real spec has **~40 distinct segment types
  and 5+ levels of nesting** for one booking instruction. Good citable justification for
  why FreightBench deliberately flattens to 35 fields rather than modeling full EDI
  fidelity.

### UN/EDIFACT IFTMBF (Firm Booking Message)
`https://www.stedi.com/edi/edifact/messages/IFTMBF` (Release D21A)
- **Purpose:** a party *definitely* booking forwarding/transport services, with
  conditions specified by the sender — the closest real EDI analog to what FreightBench
  actually generates.
- **Structure:** near-identical to IFTMIN through most groups (same header shape minus
  CUX/DOC/the EFI group). Same deep GID (goods item, repeat 99999) and EQD (equipment,
  repeat 999) nesting, each still carrying a full DGS dangerous-goods sub-block.
- **Realism note:** even a "simple firm booking" in real EDI carries far more structural
  depth than a flat 35-field schema — same citable justification as above.

### UN/EDIFACT IFCSUM (Forwarding and Consolidation Summary List)
`https://www.stedi.com/edi/edifact/messages/IFCSUM` (Release D21A)
- **Purpose:** consolidation-purposes message from the forwarding/transport party to
  the party the consolidated cargo is destined for; supports a short reconciliation
  form and an extended form with full consignment detail inline.
- **Structure:** header UNH/BGM (carries Master B/L or Master AWB number)/DTM/MOA/FTX/
  **CNT** (control total — total equipment count, consignment count, gross weight of
  the whole consolidation) /PCD/GDS, then ~80 groups total including **Group 28 CNI**
  (consignment information, repeat 9999 — lists each consignment in the consolidation
  by transport-document number) and **Group 55 GID** (goods item, repeat 99999).
- **Real sample message (verbatim, from an open-source EDI parser's test fixtures):**
  `github.com/indice-co/EDI.Net` (a .NET EDI parsing library test fixture, not a spec
  example) — shows real compact segment text like `TDT+20++10:SEA` (mode=sea) and
  `CNT+7:25.784:KG` (weight control total), and the **CNI+GID pairing** that lists
  multiple house shipments under one control total — structurally the closest real EDI
  analog to FreightBench's `multi_shipment` pathology.

### CargoIMP FWB (Freight/Air Waybill) and FHL/FZB (House Waybill/Manifest)
Sources: `parse2.com/example-cargoimp-FWB16.shtml` (validator vendor, includes a real
sample message), `flaks.io/glossary/cargo-imp`, `xmlpipelineserver.com/.../iata-cargo-imp/`
- IATA's Cargo Interchange Message Procedures (introduced 1975; 34th edition, effective
  2015-01-01, is now frozen). Compact Type-B text messages (not EDIFACT), 3-letter
  segment tags.
- **Real sample FWB/16 message (verbatim):**
  `FWB/16 777-12345675BOMSUV/T1K3.5 RTG/SUVII SHP /T. ULSIDAS LTD. /105 VEER TAMAN ROAD
  /MUMBAI /IN CNE /J. JONES IMPORTERS /. /SUVA /FJ AGT//1430288 /SPEEDAIR SERVICES
  /MUMBAI CVD/INR//PP/NVD/1500.00/XXX RTD/1/P1/K3.5/CM/W3.5/R800.00/T800.00 /NG/CLOTH
  SAMPLES /2/ND//NDA PPD/WT800.00 /CT800.00 CER/T.ULSIDAS LTD. ISU/01OCT05/MUMBAI
  /SPEEDAIR SERVICES REF///AGT/SPEEDAIRSERVICES/BOM`
  — segments: FWB/16 (msg+version), 777-12345675 (AWB no: 3-digit prefix + 8-digit
  serial), BOMSUV (origin/dest airport pair), RTG (routing), SHP (shipper block), CNE
  (consignee block), AGT (agent code+name+location), CVD (currency/valuation/charges),
  RTD (rate description: pieces/weight/rate class/rate/total), NG (goods description),
  PPD (prepaid summary), CER (certification/signatory), ISU (issue date/place/agent),
  REF (reference).
- **A real naming trap worth reusing for FreightBench's own ambiguity pathologies:**
  FHL is commonly *misnamed* "house waybill data" but is actually the **consolidation
  summary/manifest** (houses listed under a master) — the real House AWB Data message
  is **FZB**. Practitioners and even some airline systems conflate the two. Full
  message-family list (flaks.io): **FWB** (Air Waybill/master), **FFM** (Flight
  Manifest), **FSU** (Status Update), **FHL** (Consolidation List), **FZB** (House
  Waybill Data — the real HAWB message), **FFR** (AWB Space Allocation Request, i.e. a
  booking request, itself often confused with a flight manifest).
- **Realism note:** `RTD/1/P1/K3.5/CM/W3.5/R800.00/T800.00` packs pieces, weight unit,
  commodity class, weight, rate, and total into one slash-delimited segment — a strong
  contrast point for FreightBench's plain-English bodies, and citable evidence for why
  FreightBench targets email-shaped extraction rather than simulating Cargo-IMP's wire
  format directly.

### Cargo-XML (IATA's XML successor to Cargo-IMP)
`https://github.com/riege/one-record-converter` (Riege Software's open-source
XFWB/XFZB→ONE Record converter), `flaks.io/glossary/cargo-imp`
- Introduced ~2010; re-expresses Cargo-IMP content in XML, removing the fixed
  character-set/message-size constraints. 1:1 mapping to Cargo-IMP ancestors with an
  "X" prefix: **XFWB**↔FWB, **XFHL**↔FHL, **XFZB**↔FZB, **XFSU**↔FSU, etc. Per Riege's
  README, XFWB3 is "a message from a forwarder to an airline"; XFZB3 (house waybill) has
  weaker mapping support in their converter, implying it's structurally simpler/less
  standardized in practice. IATA's Cargo-XML Manual and Toolkit (1st ed., Dec 2012)
  covers 14 messages; XFWB/XFNM were the first recommended for phased migration
  (WebSearch snippet only — IATA's own PDFs returned unreadable binary).
- **Realism note:** air cargo now has two live, non-interoperable wire formats (legacy
  Cargo-IMP text and modern Cargo-XML) carrying identical field semantics — good
  evidence that FreightBench's 35 fields are a deliberately-simplified superset of what
  several real formats already try to standardize.

### Other EDI context (not message-structure-specific, useful for the README's tone)
- `github.com/nerdocs/pydifact` — general-purpose Python EDIFACT parser; no freight
  sample messages shipped, but evidence open-source EDIFACT tooling exists.
- `github.com/parcelLab-archive/edi-iftmin` — archived IFTMIN/IFTSTA parser built by a
  parcel-tracking company, confirming real industry use of IFTMIN for carrier booking
  integration (shows parsed-JSON output only, not raw EDI samples).
- WebSearch snippet (transportmanagement.org, not independently verified): "most
  European road freight carriers won't accept bookings through a REST API — they want
  EDIFACT IFTMIN messages, with status updates sent back as IFTSTA" — background color
  on IFTMIN's continued real-world relevance.

---

## Gap Analysis: FreightBench Generator vs. Reality

Grounded directly in `freightbench/schema.py`, `generate.py`, `pathologies.py`,
`reference.py`, `naive.py`, `score.py`, `tests/test_freightbench.py`, and
`examples/naive-report.txt`, cross-referenced against the findings above.

### 1. One rigid template shape vs. enormous real structural variance
Every document today opens with a one-line greeting ("Hi,"/"Hello,"), one intro
sentence, a fixed-order `Field: value` block (`Mode: / Origin: / Destination: /
Shipper: / Consignee: / Commodity: / Pieces: / Gross weight: / Volume: / Incoterm: /
Cargo ready: / Freight terms: / Our reference:`), and a bare `Best regards,\n<name>\n
<company>` sign-off. Real correspondence spans a much wider register: formal,
ESL-influenced "Respected Sir/Madam... at your earliest convenience" (emailsinenglish.com)
next to casual "Dear Freight Team," (Freightamigo) next to terse, single-paragraph asks
("FCL sea freight from Ho Chi Minh... ready in early August," mg-spl.com) next to
checklists pasted straight into the body with uneven formatting (Freightos). Subject
lines follow real conventions the generator never uses, e.g. `"RFQ - Ocean LCL Quote:
[CBM] [origin] to [destination]..."`. None of this variance exists today; every document
in the corpus is instantly recognizable as the same template with different values
substituted in.

### 2. Reference-number formats are fictional and singular
`booking_reference` is always `BK-#####` and `customer_reference` is always `PO######`
— both invented formats with no real-world analog. Reality: AWB numbers are
`XXX-XXXXXXX-X` with a **verifiable check digit** (serial mod 7 — freightos.com,
cross-confirmed by Australian Border Force); container numbers are ISO 6346 (4 letters
ending in U + 6 digits + check digit, e.g. `MSCU1234567` — exportnesthub.com); B/L
numbers are SCAC-prefixed with carrier-specific patterns (`MAEU`+9 digits for Maersk-
style, `HLCU`+13 chars for Hapag-Lloyd-style — vizionapi.com); and a single real booking
carries up to **five separate reference numbers simultaneously** (shipper ref, forwarder
ref, invoice ref, and two SI-stage refs — ONE's own booking guide), not one flat "our
reference." This is concretely actionable: a `reference_formats.py` module with
carrier-specific generators and a real checksum validator would let the generator (a)
produce plausible real-shaped references, and (b) build a new "malformed reference
number" pathology (a trailing AWB check digit of 7-9 is mathematically impossible —
an easy, checkable trap).

### 3. Whole document types don't exist yet — and now have concrete field taxonomies ready to use
README already states plainly that "PDF and HAWB documents" don't exist yet
("currently email bodies only"). This research fills in exactly what's missing, with
sources strong enough to build from directly: the SLI (NTCBFFA's 40-box specimen), the
AWB (eAWBlink's 17-field-group form + IATA's Conditions of Contract), the House/Master
B/L (DCSA's standard, which is uniquely valuable because it gives **per-field
Mandatory/Conditional/Optional status by lifecycle stage** — booking request → confirm →
prepare B/L → issue B/L — meaning the generator could finally produce realistic
*omissions*, not just realistic values), the DG declaration (a tabular UN-No./Proper-
Shipping-Name/Class/Packing-Group grammar, not a flat list), the VGM (per-container, two
weighing methods), the arrival notice/pre-alert (fundamentally a cover-email bundling
other documents' data, not its own schema), and the commercial invoice/packing list
(distinct field sets — buyer ≠ consignee, and invoice/packing-list totals must match
exactly, a plantable pathology).

### 4. About a third of the schema is never actually expressed in generated text — a functional bug, not just a realism gap
Re-reading `generate.py`'s `_block()` method: only 13 of the schema's 35 fields ever
appear as text in a generated body (`mode, origin, destination, shipper, consignee,
commodity, pieces, packaging_type, gross_weight_kg, volume_cbm, incoterm,
cargo_ready_date, freight_terms, customer_reference` — 14 counting packaging_type
inline with pieces). `service_level`, `shipper_country`, `consignee_country`, `hs_code`,
`currency`, `pickup_required`, `delivery_required`, and `temperature_controlled` are
generated into ground truth by a coin flip (`self.rng.random() < p`) but **never printed
anywhere in the body**. This is independently confirmed by the bundled
`examples/naive-report.txt`: exactly these fields score **0.0%** for the naive
extractor — not because the extractor is bad at them, but because the text contains no
signal for them at all. A perfect extractor reading the email as generated still cannot
recover these fields. Real bookings *do* surface most of these in prose ("please arrange
pickup from our Rotterdam warehouse," "keep frozen at -18°C" — mg-spl.com's reefer
fields; DAKOSY's TMP segment) — the fix is either to actually write these into body text
non-templated ways, or to honestly exclude them from strict extraction scoring until
they are.

### 5. The `dg_undeclared` pathology is a strawman; a much harder, more realistic version is one sentence away
Today's pathology text is a flat, unqualified "No dangerous goods declaration needed for
this one" — catchable by keyword-matching "dangerous goods" near a known-DG commodity
name. Research (49 CFR 173.185, and the UN3480/UN3481 Section II sources) shows the real
failure mode is subtler: shippers genuinely invoke narrow, real exemptions incorrectly —
"shipped under Section II, no DGD required" (caps at one package per consignment; many
carriers reject it outright anyway) or "reduced state of charge, exempt" (a real
exemption for UN3480 standalone cells that does **not** formally extend to UN3481
cells-in-equipment, a distinction shippers routinely get wrong in practice). Swapping the
current sentence for a regulation-literate-but-wrong claim would make this pathology
test actual domain knowledge instead of keyword avoidance. Ocean DG adds a further wrinkle
with no air-side analog at all: a **second, separate container-packing certificate**
alongside the declaration (UK MCA guidance) — something `dangerous_goods: bool` +
`un_number` cannot represent regardless of phrasing.

### 6. Confirmation status is not binary, and "cargo ready" conflates several distinct real deadlines
The generator never produces a confirmation-side document at all — every document is a
request. MSC's own IFTMBC spec shows real confirmations carry a 3-valued status
(Pending/Accepted/Conditionally Accepted, not just "confirmed") plus multiple distinct
deadlines that collapse into the generator's single `cargo_ready_date` today: VGM
cut-off, SI-due date, port cut-off, and inland cut-off are all separately named,
separately dated fields in real carrier documentation.

### 7. Company-suffix normalization is Euro/US/SG/India-centric and will misfire on real global partners
`score.py`'s `_company_key()` strips `bv, gmbh, ltd, limited, inc, pte ltd, pte, pvt
ltd, pvt, co, nv, sa, ag` — a reasonable start, but it misses suffixes that are
extremely common among real freight-forwarding trading partners: **LLC** (US, Middle
East), **Pty Ltd** (Australia), **Sdn Bhd** (Malaysia), **KG**, **OY/OYJ** (Finland),
**AB** (Sweden), **ApS** (Denmark), **S.p.A.** (Italy), **S.L./S.A. de C.V.**
(Spain/Mexico), **SARL/SàRL** (France/Switzerland), **K.K.** (Japan), **Co. Ltd**
(very common across Asia, distinct from bare "Ltd"), **Ltda** (Brazil/Portugal),
**FZE/FZCO** (UAE free zone). This is a cheap, concrete, immediately testable fix once a
short reference table of real suffixes-by-country is assembled — none of the research
above required for it, just breadth.

### 8. HS codes are 4-digit headings; real commercial documents require 6-10 digits
`reference.py`'s `COMMODITIES` dict stores 4-digit HS headings only ("8517", "3208").
US CBP requires an 8-digit HTS subheading at release (19 CFR 142.6, Cornell LII); the EU
requires 8-digit Combined Nomenclature codes (EU Access2Markets). The schema's own field
description says "Harmonised System code" without specifying length, but the reference
data doesn't go past the 4-digit heading level that real invoices/customs filings never
stop at.

### 9. No lane-conditional field logic; Incoterms have no named place
ONE's own booking form makes AES ITN, CERS, Mexico TAX IDs, and China MOT No. all
**conditional on the specific origin/destination country pair** — the generator's flat
schema applies identical fields to every lane regardless of geography. Real Incoterms
also carry a named place ("FOB Shanghai," never bare "FOB") — the generator's
`incoterm` field is always bare.

### 10. No per-piece dimensions or repeatable multi-line cargo
Every cargo field is a single aggregate scalar (`pieces`, `gross_weight_kg`,
`volume_cbm`). NTCBFFA's SLI boxes 26-34 repeat per HTS line item; real air
chargeable-weight is derived from per-piece L×W×H via a volumetric divisor (a
calculation the generator can't represent since it has no dimension fields at all,
despite already having a separate `chargeable_weight_kg` field in the schema that's
never actually derived from anything).

### 11. Signature blocks and disclaimers are thin, and this research honestly could not fill that hole
Signatures today are name + company only — no title, phone, address, or
confidentiality footer. This research specifically looked for a verified
freight-industry-specific disclaimer example and did not find one (only generic
disclaimer-template sites, not a named forwarder's own footer) — flagged as an open gap
rather than invented. Real signatures very likely do carry phone/mobile/title given
every rate-request template found asks the requester to include contact details, but a
verified real *signature block* (not just "include your phone number" advice) wasn't
independently confirmed either. Treat both as directions worth testing empirically
against whatever real correspondence becomes available, not as facts this research
established.

### 12. Realistic negative space is missing: genuinely incomplete requests, and thread density
Multiple independent sources note real rate/booking requests are very often
underspecified ("Please quote Singapore to India" — mg-spl.com explicitly calls this
out as unusably vague but realistic) and that a single shipment "can generate 40+
messages across its lifecycle" (Tier2 Systems). The generator's `missing_critical`
pathology removes exactly one field from an otherwise-complete document — real-world
underspecification is messier, multi-field, and the generator produces exactly one
email per document (except `forwarded_thread`'s single quoted layer) with no sense of
an ongoing, amended, multi-message conversation.

### 13. Real EDI is a useful citation, not a target to implement
IFTMIN/IFTMBF have on the order of 40 distinct segment types and 5+ levels of nesting
for a single booking instruction (Stedi's documentation); real Cargo-IMP FWB messages
pack pieces/weight/rate/total into single slash-delimited codes
(`RTD/1/P1/K3.5/CM/W3.5/R800.00/T800.00`). This is not something FreightBench should
try to replicate — it's evidence the README can cite to justify the deliberate
35-field flattening as a considered simplification of genuinely more complex real
formats, not an oversight.

### 14. Access gaps that should stay visible, not get smoothed over
Reddit and LinkedIn — the two source classes the original brief specifically named for
"real quoted emails" — were completely unreachable this session (explicit tool blocks
and empty search results respectively). Nothing in this inventory should be read as
"real forum-quoted booking emails were found and analyzed"; they were not. Several
carrier PDFs (Hapag-Lloyd and MSC shipping-instruction guides, CMA CGM's SI format spec,
IATA's own DGD PDF) also could not be retrieved and are absent rather than
approximated from memory.

---

## Dataset & Benchmark Positioning List

For the README's positioning against prior art. All figures below are as retrieved this
session; flagged explicitly wherever a figure is WebSearch-snippet-sourced rather than
page-confirmed.

| Dataset/benchmark | Domain | Size | Task | Real/Synthetic | Freight-specific? |
|---|---|---|---|---|---|
| **CORD** ([clovaai/cord](https://github.com/clovaai/cord)) | Receipts | 11k+ collected, 1k publicly released (800/100/100 split) | Post-OCR key info parsing, 8 superclasses/54 subclasses | Real | No |
| **FUNSD** ([project page](https://guillaumejaume.github.io/FUNSD/)) | Scanned forms | 199 docs, 31,485 words, 9,707 entities | Entity labeling + relation linking | Real | No |
| **Kleister NDA / Charity** ([arXiv:2105.05796](https://arxiv.org/abs/2105.05796)) | Legal (NDAs) / financial (charity reports) | 540 docs / 3,229 pages; 2,788 docs / 61,643 pages | Long-document key info extraction | Real (mixed scanned/digital) | No |
| **DocVQA** ([arXiv:2007.00398](https://arxiv.org/abs/2007.00398)) | Mixed industry docs (UCSF Industry Documents Library) | 50k QA pairs / 12,767 page images | Visual question answering | Real | No |
| **DocILE** ([docile.rossum.ai](https://docile.rossum.ai/)) | Invoices/orders | 6,680 real + 100,000 synthetic + ~1M unlabeled | Key info localization + line-item recognition | Real+Synthetic mix | No |
| **RealDocBench** ([arXiv:2606.07401](https://arxiv.org/abs/2606.07401)) | Mortgage/finance/**logistics**/clinical | 1,356 field-level Qs / 581 docs (QA); 1,500 pages (layout) | Per-field typed-answer QA + layout localization | Real | Partial — B/L is one doc type in its logistics slice, not a dedicated focus |
| **RealKIE** ([arXiv:2403.20101](https://arxiv.org/pdf/2403.20101)) | Financial/govt/political disclosures (5 datasets) | Varies by sub-dataset | Enterprise key info extraction | Real | No — confirmed no logistics content |
| **Customs Import Declaration Datasets** ([arXiv:2208.02484](https://arxiv.org/abs/2208.02484), snippet-sourced) | Customs/trade | 54,000 GAN-synthesized records (base: 24.7M real declarations) | Fraud/critical-fraud classification (tabular) | Synthetic (conditional GAN) | Adjacent — tabular classification, not text extraction |
| **LLMStructBench** ([arXiv:2602.14743](https://arxiv.org/abs/2602.14743)) | Generic office **email** (support tickets, sick leave, project extension, conference reg, loan request) | 995 tests, 5 scenarios, 22 models tested | Structured JSON extraction from synthetic emails | Synthetic (LLM-generated) | No — but closest methodological match (schema→synthetic email text) |
| **ExtractBench** ([arXiv:2602.12247](https://arxiv.org/abs/2602.12247)) | General enterprise PDFs (financial reporting example) | 35 PDFs, 12,867 fields, up to 369 fields/schema | PDF-to-JSON structured extraction | Real | No |
| **Matrix / Kuehne+Nagel** ([arXiv:2412.15274](https://arxiv.org/abs/2412.15274)) | **Freight-forwarding invoices** (UBL format) | Not disclosed in abstract | Transport-reference-number extraction (narrow, single field family) | Real (anonymized), industry partner | Yes — closest on-domain prior art found |
| **FATURA** (mentioned in search results, not independently fetched) | Invoices | 50 unique layouts | Invoice extraction | Not confirmed | No |
| **Multilingual Intent Classification in Logistics Customer Service** ([arXiv:2603.23172](https://arxiv.org/abs/2603.23172)) | Logistics customer-service queries | ~30,000 de-identified real queries (from 600k), EN/ES/AR + zero-shot ID/ZH | Intent classification (13 parent / 17 leaf intents) | Real | Logistics-domain, but classification not extraction |
| **ExStrucTiny / VAREX** (search results only, not deep-dived) | General structured extraction | Unconfirmed | Schema-variable/multi-modal extraction | Unconfirmed | No indication of logistics specificity |

**Positioning summary:** No existing public benchmark combines FreightBench's specific
combination of (a) freight-forwarding booking-email domain, (b) synthetic + fully
deterministic/reproducible generation, (c) a named-pathology error taxonomy (11 distinct,
labeled failure modes rather than one blended accuracy number), and (d) a 5-category
outcome split that separates "wrong" from "missing" from "hallucinated." **RealDocBench**
is the closest in *scoring philosophy* (per-field typed-answer scoring against a gold
dict, explicit critique of "synthetic prose" benchmarks) but uses real, not-reproducible
documents across four broad regulated domains, with logistics/B-of-L as only one slice,
not a dedicated focus, and no confirmed wrong-vs-missing split. **LLMStructBench** is the
closest in *generation methodology* (schema → synthetic email text) but is generic
office/admin domain with no pathology taxonomy and token-level accuracy scoring instead
of the 5-outcome split. **Matrix/Kuehne+Nagel** is the closest in *domain* (a real global
forwarder's own documents) but narrow (single field family, invoices not booking emails,
real not synthetic, no pathology taxonomy). No source found combines all four properties
FreightBench claims — which is a legitimate, citable positioning claim, not just marketing
language, based on what this research pass could locate.
