# Cluster C — Compliance & Attachment Document Research
Research pass for grounding the FreightBench synthetic-data generator in real field structures for: commercial invoice/packing list, arrival notices/pre-alerts, dangerous goods declarations, and VGM declarations. All entries below reflect content actually retrieved this session via WebFetch or substantial WebSearch snippet detail — nothing here is backfilled from unverified parametric memory unless explicitly labeled "background knowledge."

---

## 1. Commercial Invoice & Packing List

### Source 1.1 — Cornell Law School Legal Information Institute, mirror of 19 CFR § 142.6
**URL:** https://www.law.cornell.edu/cfr/text/19/142.6
**What it is:** Codified US federal regulation text (CBP entry requirements), served via Cornell's LII mirror of the CFR (used because ecfr.gov itself redirected through a bot-check wall this session).
**Fields / structure observed:**
- Adequate description of the merchandise
- Quantities of the merchandise
- Values or approximate values of the merchandise
- HTS classification — the applicable 8-digit subheading (conditional: may be waived at time of release if not yet available, filed later at entry summary)
- Name and full address of the foreign party responsible for invoicing the merchandise — ordinarily the manufacturer or seller
- Cross-reference: the fuller invoice data set required under 19 CFR §§ 141.86–141.89 can be supplied at entry summary rather than at release
**Notes on phrasing/layout/gaps:** This is the *minimal release-stage* invoice standard, not the full enumerated list (that lives in §141.86's ~11 categories, referenced but not restated here). The regulation's own vocabulary — "adequate description," "values or approximate values" — is looser than a rigid schema; a generator modeling a commercial invoice should allow for this two-stage structure (fields required now vs. fields that can trail behind) rather than treating "commercial invoice" as one flat always-complete document.

### Source 1.2 — US Dept. of Commerce / International Trade Administration, trade.gov
**URL:** https://www.trade.gov/commercial-invoice
**What it is:** Official US government exporter-guidance page.
**Fields / structure observed:** Carries forward pro forma invoice data; HS code (explicitly flagged optional-but-recommended, to speed clearance); destination control statement (recommended boilerplate clause protecting the exporter against diversion to restricted destinations/end-uses).
**Notes:** Confirms there is no single universal invoice template — a seller/exporter-format invoice is accepted almost everywhere as long as the substantive content is present. The "destination control statement" is a distinct standing clause (not a data field, but fixed boilerplate text) that a realistic commercial-invoice generator currently likely omits entirely.

### Source 1.3 — UK Government, business.gov.uk (official exporter support service)
**URL:** https://www.business.gov.uk/export-from-uk/learn/categories/funding-financing-and-getting-paid/get-paid/how-create-export-invoice/
**What it is:** Official UK government guidance on export/commercial invoice content.
**Fields / structure observed (15 items):**
1. Invoice number + date of issue
2. Seller details (name, address, contact)
3. Buyer details (name, address, contact)
4. Consignee details, when different from the buyer
5. Related paperwork references (proforma invoice / purchase order / sales contract number and date)
6. Unit price, payment method, currency, discounts
7. Weight and quantity (gross/net weights, package details)
8. HS/commodity/tariff code + plain-English description
9. Incoterms (agreed with buyer)
10. Packaging marks and numbers, e.g. "1 of 6 boxes"
11. Country of origin
12. Transport details (means and route)
13. Total value
14. Additional charges (freight, insurance, certification costs)
15. Language version(s) + certification, if the destination market requires it
**Notes:** The most complete single checklist found. Two things worth encoding: (a) **buyer and consignee are explicitly separate roles** — many synthetic generators collapse these into one field, which is unrealistic for door shipments to a different receiving address than the paying party; (b) package-mark notation follows a "N of M" convention ("1 of 6 boxes"), a concrete formatting pattern to reproduce rather than a free-text field.

### Source 1.4 — IncoDocs, "How to Create and Download a Packing List for Export Shipments"
**URL:** https://incodocs.com/blog/packing-list-document-template-export-import-shipping/
**What it is:** Trade-documentation software vendor's practitioner guide (IncoDocs sells packing-list/invoice generation tooling).
**Fields / structure observed, by group:**
- *Exporter:* company name, logo, address, phone, contact, registration numbers
- *Consignee & buyer:* name, address, phone, contact for each (if different)
- *Shipping details:* method of dispatch (Road/Rail/Air/Sea), shipment type (FCL/LCL/Breakbulk), country of origin, country of final destination, vessel/aircraft name, voyage number, port of loading (POL), date of departure, port of discharge (POD)
- *References:* export invoice number + date, bill of lading number, buyer's PO number, additional references, packing information, delivery notes/special instructions
- *Product/packaging:* product code, description of goods, unit quantity, "kind & number of packages" (e.g. "Pallet x 12"), net weight (kg), gross weight (kg), measurements (m³)
- *Signature:* signatory company, authorized signatory name, digital signature, digital company stamp/seal
**Notes:** This is a genuinely distinct field taxonomy from the commercial invoice — a generator currently treating "packing list" as a subset of invoice fields is missing volumetric measurement (m³), the FCL/LCL/Breakbulk shipment-type flag, and the net-vs-gross weight split that packing lists (not invoices) are the canonical source for.

### Source 1.5 — WebSearch synthesis: EU customs commercial invoice/packing list requirements
**URL (primary official reference in results):** https://trade.ec.europa.eu/access-to-markets/en/content/additional-customs-clearance-documents (European Commission Access2Markets portal), corroborated by multiple forwarder guides in the same result set
**What it is:** Search-derived synthesis anchored on the EU's official trade portal.
**Fields observed:** EU importer's EORI number; 8-digit HS code per line; unit + total value in convertible currency; Incoterms 2020 reference with named place; place and date of issue; invoice number; payment terms. Packing list: package-by-package gross/net weight, dimensions, identification marks, contents.
**Notes:** EORI is an EU/UK-specific registered-trader identifier distinct from a generic buyer/seller ID — worth modeling as its own field format for EU-bound synthetic shipments. The more interesting structural fact: EU guidance stresses that **package count and gross weight on the invoice must match the packing list exactly**, and consignee name/address must be identical across invoice, packing list, and transport document. That cross-document consistency requirement is itself a realistic extraction/validation target — a generator could plant a deliberate mismatch as its own pathology (invoice says 12 cartons, packing list says 11).

---

## 2. Arrival Notices & Pre-Alerts

### Source 2.1 — Maersk Insights, "Your cargo has arrived: Understanding arrival notice in ocean freight shipping"
**URL:** https://www.maersk.com/insights/digitalisation/2024/11/15/arrival-notice
**What it is:** Carrier-published (Maersk) customer-education article.
**Fields / content observed:** Arrival notice carries customs-relevant info echoed from the bill of lading and commercial invoice; per-container free time and last free day; a demurrage estimate running through the expected gate-out date, broken into itemized charges.
**Notes:** Confirms the arrival notice is not just a "your cargo is here" message — it doubles as a financial-deadline document (last free day, itemized demurrage estimate). A generator modeling only ETA/container fields misses the charges-and-deadline block entirely.

### Source 2.2 — Freightos Glossary, "What is an Arrival Notice?"
**URL:** https://www.freightos.com/glossary/what-is-an-arrival-notice/
**What it is:** Freight-marketplace glossary page aimed at shippers/importers.
**Fields observed:** Vessel name, bill of lading number, container number, cargo description, total number of packages, weight, arrival date, location of goods, instructions/requirements for cargo release, details on charges due before release.
**Sender → recipient:** Carrier or handling freight forwarder → consignee, notify party, importer of record.
**Notes:** Cleanest single field list found for this document type. Two details worth reproducing exactly: "vessel name" is called out separately from voyage number (both should appear, not just a combined string), and "location of goods" is its own field (which terminal/CFS/warehouse the cargo physically sits in) — distinct from port of discharge.

### Source 2.3 — Extensiv Glossary, "Arrival Notice"
**URL:** https://www.extensiv.com/glossary/arrival-notice
**What it is:** Warehouse/3PL software vendor's glossary page.
**Fields observed:** Contact information, description of goods received, number of units arrived, charges to be settled at pickup, incoterms/arrival port/tariff details, customs clearance documentation needed, ETA.
**Notes:** States arrival notices commonly go out **3–5 days before ETA**, not strictly after arrival — which blurs the line with a pre-alert. In practice, "arrival notice" and "pre-alert" are not always cleanly separated by timing; some carriers send an advance arrival notice that functions like a pre-alert. A generator could legitimately use overlapping vocabulary/timing for both document types rather than enforcing a hard boundary.

### Source 2.4 — WebSearch synthesis: "what is a pre-alert in freight forwarding"
**URLs referenced in results:** terminal49.com/glossary/pre-alert--arrival-notice, freightcourse.com/pre-alert, luwjistik.com
**What it is:** Search-derived synthesis of freight-forwarding glossary/training content (direct WebFetch of the Terminal49 page itself failed to return body content both times attempted, so this entry is search-snippet-derived only).
**Content observed:** A pre-alert is sent by the **origin** forwarder to the **destination** forwarder/customs broker (sometimes copied to the consignee), issued at or shortly after departure — i.e., *before* arrival, which is the opposite end of the timeline from an arrival notice (destination carrier/agent, issued at/near arrival). Typical bundle: Bill of Lading, commercial invoice, packing list, required certificates, plus ETA, container details, terminal information. Three stated purposes: gives the destination ops team lead time to verify documents/file customs entries/arrange clearance; lets the customs broker pre-declare in countries that allow it; gives the consignee advance planning visibility.
**Notes:** The structural distinction that matters for a generator: a pre-alert is fundamentally a **cover email bundling documents generated elsewhere** (BL, invoice, packing list) rather than a document with its own unique field schema — sender (origin forwarder) and timing (pre-departure/pre-arrival) are what define it, not a distinct field set. The current generator's single rigid "Field: value" booking-request format doesn't model this handoff/bundling structure — a pre-alert email would plausibly reference attachments by name and repeat only a subset of key fields (BL number, ETA, container numbers) inline.

---

## 3. Dangerous Goods Declarations

### Source 3.1 — ShippingSolutions Software, "Creating the IATA Dangerous Goods Form: The Shipper's Declaration for Dangerous Goods"
**URL:** https://shippingsolutionssoftware.com/blog/creating-the-iata-dangerous-goods-form-the-shippers-declaration-for-dangerous-goods
**What it is:** Export-documentation software vendor's field-by-field walkthrough of the IATA Shipper's Declaration for Dangerous Goods (DGD) form. (Direct WebFetch of IATA's own fillable PDF failed — binary/compressed content the fetch tool couldn't parse — so this HTML walkthrough is the verified substitute.)
**Fields / structure observed:**
- *Header:* Shipper (name/address), Consignee (name/address), Air Waybill Number, "Page __ of __ Pages," Shipper's Reference Number (optional), Transport Details (passenger-and-cargo vs. cargo-only aircraft), Airport of Departure, Airport of Destination, Shipment Type (Radioactive / Non-Radioactive)
- *"Nature and Quantity of Dangerous Goods" table*, per line item: UN or ID number (e.g. "UN1993"); Proper Shipping Name; Class or Division + subsidiary risk; Packing Group (I/II/III where applicable); Number of packages + packaging type; Net quantity per package; Gross weight (when applicable); "Overpack Used" notation (when relevant); Packing Instruction code; Special Provision number(s), prefixed "A"
- Additional Handling Information field; Emergency response telephone number (called out as required specifically for shipments touching the US)
- Signature block: signatory printed name (mandatory) and date
- A fixed certification block (paraphrased, not quoted): the shipper affirms the consignment is correctly identified by proper shipping name and has been properly classified, packaged, marked, and labeled for transport under the applicable regulations.
**Notes:** The richest structural source found across all four document types. The key layout fact for a generator: the "Nature and Quantity of Dangerous Goods" section is a **table with a fixed column grammar** (UN No. / Proper Shipping Name / Class-Division / Packing Group, then a second block of Qty-Type-Instruction-Authorization), not a flat key:value list — reproducing that tabular grammar is what makes a synthetic DGD look real rather than like a repurposed invoice template. The 24-hour emergency contact being conditionally required (US-touching shipments) is a good axis to vary.

### Source 3.2 — DGM-US, "Shipper's Declaration for Dangerous Goods"
**URL:** https://www.dgm-us.com/dangerous-goods-declarations/
**What it is:** Dangerous-goods packaging/compliance vendor's service page, contrasting air (IATA) vs. ocean (IMO) declarations.
**Fields observed:** Proper shipping name, UN number, class and packing group, quantity and type of packaging, emergency contact information, shipper certification/signature — presented as the air-side (IATA) field set. Ocean/IMO declarations are described only at the process level ("classification, packaging, labeling, and documentation") without a distinct field enumeration on this page.
**Notes:** Corroborates Source 3.1's field set for air; the real ocean-specific structural detail came from the UK MCA source below (3.3), which this page doesn't provide.

### Source 3.3 — UK Maritime & Coastguard Agency (gov.uk), "MCA guidance for container packing certificate on dangerous goods notes"
**URL:** https://www.gov.uk/guidance/mca-guidance-for-container-packing-certificated-on-dangerous-goods-notes
**What it is:** Official UK government regulatory guidance interpreting IMDG Code documentation requirements. The strongest single ocean-DG source found — official national competent authority, directly on-topic.
**Fields / structure observed:**
- The DG transport document (declaration) and the container/vehicle packing certificate **may be combined into one document, or must be physically attached to each other if kept separate** — citing IMDG Code §5.4.1.6 (declaration) and §5.4.2.1 (packing certificate) by section number.
- DG declaration content: confirmation that goods are properly packaged, marked, and labeled, and in proper condition for transport.
- Packing certificate content (additional, beyond the declaration): container/vehicle is clean, dry, and suitable; proper segregation maintained between incompatible goods; all packages inspected and found sound; drums stowed upright with goods properly braced; bulk goods evenly distributed; marking/labeling/placarding correctly applied; container/vehicle identification number(s) stated.
- When combined into one document: requires an additional signed statement that packing was carried out per applicable provisions, with the signatory identified and the statement dated.
- Signing responsibility falls to whoever physically packed/secured the load — could be the consignor, a consolidator, a carrier, or a forwarder, not necessarily the shipper of record.
**Notes:** This reveals a structural fact a generator almost certainly doesn't model: ocean DG shipments require **two distinct certifications** (the DG declaration itself, and a separate container/vehicle packing certificate attesting to *how* it was loaded) — which can appear as one combined document or two attached ones. The container/vehicle ID number belongs on this document as a cross-check field against the booking's container number. This is genuinely different from the air-side DGD, which has no packing-certificate analog.

### Source 3.4 — International Maritime Organization (IMO), IMDG Code overview page
**URL:** https://www.imo.org/en/ourwork/safety/pages/dangerousgoods-default.aspx
**What it is:** Official IMO overview of the IMDG Code.
**Content observed:** IMDG Code became mandatory under SOLAS from 1 January 2004 (though some parts, e.g. training/security provisions, remain recommendatory). Sets out substance-specific requirements covering packing, container traffic and stowage, with particular attention to segregating incompatible substances. Points to specific sections: Chapter 3.2 (Dangerous Goods List), Chapter 7.2 (segregation requirements), Chapter 5.4 (the Multimodal Dangerous Goods Form).
**Notes:** High-authority but overview-level — doesn't itself enumerate form fields (that detail came from Source 3.3 and 3.6). Useful mainly to confirm the section numbers (5.4, 3.2, 7.2) a synthetic ocean-DG document could plausibly cite.

### Source 3.5 — Cornell Law School LII, mirror of 49 CFR § 173.185 (US lithium battery shipping regulation)
**URL:** https://www.law.cornell.edu/cfr/text/49/173.185
**What it is:** Codified US federal regulation text (PHMSA's own site returned a 403 this session, so this LII mirror is the verified official-text source used instead).
**Fields / structure observed:**
- Classification by UN number: UN3090 (lithium metal cells/batteries), UN3480 (lithium ion cells/batteries), UN3091 (lithium metal packed with/in equipment), UN3481 (lithium ion packed with/in equipment)
- Lithium battery mark specification: rectangle or square with hatched border, minimum 100mm × 100mm, red hatching with black text on a white/contrasting background, displaying the applicable UN number(s)
- Restricted-transport marking for smaller cells/batteries exceeding standard limits: package text such as "LITHIUM BATTERIES—FORBIDDEN FOR TRANSPORT ABOARD PASSENGER AIRCRAFT" or a "CARGO AIRCRAFT ONLY" designation, depending on which capacity threshold applies
- State of charge is **not** addressed in this specific section (that's an IATA/operator-level air rule, not this US ground/multimodal regulation) — this section instead cross-references Special Provision A100 for medical-device battery exceptions
- Documentation: full hazmat shipping papers are required **except** for specific carve-outs — button-cell batteries in equipment; consignments of two or fewer packages of limited cells/batteries in equipment; certain small-cell exceptions; batteries shipped for disposal/recycling. Low-production-run/prototype shipments require a specific notation referencing §173.185(e).
**Notes:** This is the most precise regulatory source in the whole research pass — exact mark dimensions and colors, exact exemption conditions for when a shipping paper is/isn't required. Directly useful for the `dg_undeclared` pathology: it shows that "no DGD required" is a **real, narrowly-scoped exception** (specific package counts, specific battery-in-equipment configurations) rather than a blanket rule — so a realistic pathology sample should have the sender's claim of "no DG paperwork needed" hinge on a plausible-but-wrong reading of one of these carve-outs, not an unqualified assertion.

### Source 3.6 — WebSearch synthesis: CMA CGM Multimodal Dangerous Goods Form
**URL referenced:** https://www.cma-cgm.com/assets/public/pdf/DG%20FORM%20BLANK%2028112017.pdf (found via search; not directly WebFetched — PDF binary content, same limitation as the IATA form)
**What it is:** A real ocean carrier's actual combined DG declaration / container packing certificate form.
**Fields observed:** Shipper full name/address with 24-hour emergency contact; container identification number; transport document number; delivery address; vessel/flight details; description of goods; packaging; container/vehicle identification; certifications block. DG-specific: proper shipping name, hazard class, UN number, packing group (where assigned), **marine pollutant designation**. When used purely as a packing certificate (not combined), a separately-signed DG declaration must still exist covering each DG consignment inside the container.
**Notes:** Corroborates Source 3.3's "combined or attached" structure with a real carrier's implementation. "Marine pollutant" is an ocean-only flag (IMDG-specific environmental hazard designation) with no air-side equivalent — a field an air/ocean-agnostic `dangerous_goods: bool` currently can't represent.

### Source 3.7 — WebSearch synthesis: lithium battery UN3480/UN3481 Section II air rules
**URLs referenced:** aeroclass.org/un-3481, freightamigo.com, shipmercury.com, battery-energy-storage-system.com, directprologistics.com, dginspector.com
**Content observed:** UN3480 = standalone lithium-ion batteries; UN3481 = lithium-ion batteries packed with or installed in equipment. The relaxed "Section II" provision caps a consignment at one Section II package (under Packing Instructions PI965/PI968); many carriers refuse Section II shipments outright regardless of the regulatory allowance; the industry is actively shifting toward requiring full Section IA/IB compliance (UN-certified packaging) even where Section II would technically still apply. UN3480 (standalone) cells may only fly at ≤30% state of charge; that cap does not formally apply to UN3481 (in/with equipment) or lithium-metal entries, though some carriers apply the 30% limit voluntarily across the board anyway.
**Notes — directly relevant to the `dg_undeclared` pathology:** This is the single most useful finding for that pathology. A realistic "sender claims no DG paperwork is needed" email for a lithium-battery shipment would plausibly invoke language like "shipped under Section II, no DGD required" or "batteries at reduced state of charge, exempt from declaration" — a claim that was historically true-ish for narrow cases but is (a) increasingly rejected by carriers in practice and (b) easy to get wrong (e.g., misapplying the one-package-per-consignment cap, or conflating UN3480's 30%-SOC allowance with UN3481, which doesn't get that exemption). That's a much more realistic and harder-to-catch pathology phrasing than a generic "no DG needed" claim with no regulatory hook at all.

### Source 3.8 — WebSearch synthesis: 24-hour emergency response number requirement
**URLs referenced:** thecompliancecenter.com, dgm-usa-ny.com, hazmatuniversity.com (citing 49 CFR 172.604)
**Content observed:** A monitored, live-answered (not an answering machine/beeper/general service), 24-hour emergency response phone number — numeric, with area code — is required on the shipping paper for dangerous goods shipments to/from/within/transiting the US, across all transport modes, whenever a shipping paper is required at all (limited-quantity and consumer-commodity shipments are among the listed exceptions). The person answering must either know the specific hazmat being shipped or have immediate access to someone who does. Third-party emergency-response contract services are common industry practice but must be formally registered/contracted before their number can be used on a declaration.
**Notes:** Confirms the "24-hour emergency contact" field called out in the brief is not just a phone number — it's a company name + monitored number pairing with specific live-response requirements behind it. A subtle, realistic non-compliance pathology: a declaration listing a normal office number (unmonitored after hours) as the "24-hour" contact.

---

## 4. VGM Declarations (SOLAS)

### Source 4.1 — International Maritime Organization (IMO), "Verification of the gross mass of a packed container"
**URL:** https://www.imo.org/en/ourwork/safety/pages/verification-of-the-gross-mass.aspx
**What it is:** Official IMO page on the SOLAS VGM amendment (the primary regulatory source for this requirement worldwide).
**Content observed:** The shipper bears primary responsibility for providing the verified weight, stating it in a shipping document, and submitting it to the master (or the master's representative) and to the terminal representative, with enough lead time to be used in the vessel's stowage plan. Two permitted methods: Method 1 — weigh the packed container as a whole; Method 2 — weigh all packages and cargo items (including pallets and dunnage) individually and add the container's tare mass, using a method certified/approved by the competent authority. The master retains ultimate discretion to refuse loading a container without a VGM. Requirement effective 1 July 2016.
**Notes:** Authoritative on responsibility and methodology but doesn't itself enumerate a document field list — this establishes the *business rules* (who signs, which of two methods, what happens if VGM is missing/late) that a generator should encode as logic, not just a static field.

### Source 4.2 — IncoDocs, "The SOLAS VGM regulations explained"
**URL:** https://incodocs.com/blog/vgm-solas-verified-gross-mass-declaration/
**What it is:** Trade-documentation software vendor's VGM explainer.
**Fields observed:** Exporter company name/address/contact; shipper's reference number; verification method used (Method 1 or Method 2); total verified gross mass (kg); container ID number; vessel name + voyage details; issue location + date; signatory organization name; signatory name, date, and signature.
**Formula stated:** Method 2 = Cargo Gross Weight + Container Tare Weight = Verified Gross Mass.
**Notes:** The clearest VGM field checklist found. Key structural point: VGM is submitted **per container**, keyed to a specific container ID and vessel/voyage — not per shipment or per booking. A multi-container shipment needs one VGM record per container number, which a generator should model explicitly rather than attaching a single VGM value to the whole booking.

### Source 4.3 — WebSearch synthesis: Maersk "SOLAS VGM Requirement" article
**URL:** https://www.maersk.com/news/articles/2020/04/22/solas-vgm-requirement (direct WebFetch timed out twice this session; entry is search-snippet-derived)
**Content observed:** VGM = cargo weight (including dunnage and bracing) plus the container's tare weight; must be communicated in a shipping document — either folded into the shipping instruction or sent as a separate communication — before the container is loaded on the vessel. Method 1 = weigh the packed container. Method 2 = weigh all cargo/contents and add the container's tare weight as marked on the container's door end; flagged as impractical for bulk commodities (e.g. scrap, grain), where use of Method 2 needs local-authority permission.
**Notes:** Corroborates Source 4.1. The concrete detail worth keeping: container tare weight is read from a **physical marking stenciled on the container door end** (the CSC plate) — i.e., Method 2 shippers reference a real physical data source, not an arbitrary number they invent. A synthetic Method-2 VGM document could plausibly cite "per CSC plate" or "container tare per door marking" as its tare-weight source.

### Source 4.4 — WebSearch synthesis: MSC VGM submission requirements
**URLs referenced:** msc.com, rosecontainerline.com (hosting an MSC USA VGM PDF)
**Content observed:** Before VGM submission, MSC requires confirmation of booking number, container number, seal number, vessel/voyage reference, shipper information, and cut-off time. Submission channels: myMSC (free), EDI (via INTTRA, GT Nexus, or CargoSmart), manual entry via those same platforms, or email (carries a $25-per-container manual-submission fee).
**Notes:** Confirms container number + seal number + booking number as the minimum linking keys tying a VGM record back to its underlying booking — seal number in particular is a field not mentioned by the other VGM sources but is a real cross-reference field. The manual-submission fee is carrier-operational color (adjacent to, not part of, the VGM document itself) but is a realistic charges-line detail if a generator ever models late/manual VGM handling fees in an invoice or arrival-notice charges block.

---

## Sources attempted but excluded (no usable content retrieved)
For transparency — these were fetched but yielded nothing substantive, so they are not counted above and nothing was inferred from them:
- IATA's own fillable Shipper's Declaration PDF and IATA's Lithium Battery Guidance Document PDF — both returned as binary/compressed content the fetch tool couldn't parse as text.
- gwp.co.uk (UN3480/3481 guide) — HTTP 403.
- MSC "VGM & Tare Weight Guide" blog — HTTP 403.
- PHMSA's own lithiumbatteries page — HTTP 403 (used the Cornell Law LII mirror of 49 CFR 173.185 instead, Source 3.5).
- Terminal49's pre-alert/arrival-notice glossary page — fetched twice, both times returned no extractable body content (only search-snippet-level detail was usable, captured in Source 2.4).
- Hapag-Lloyd, DHL Global Forwarding, Kuehne+Nagel, C.H. Robinson arrival-notice pages — searched specifically but returned no field-level detail, only generic marketing/navigation content.
