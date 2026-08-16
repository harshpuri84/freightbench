# Cluster B Research: Transport Documents (SLI, HAWB/MAWB, House/Master B/L)

Research method: WebSearch + WebFetch only. Several PDFs that WebFetch's summarizer
couldn't parse as binary were re-read directly with the Read tool (which does real PDF
text/image extraction) from WebFetch's own local cache copy of the same fetched URL —
no separate download tool was used. Field/box labels below are reproduced fully and
exactly as short technical labels (not copyrighted prose). Narrative/legal prose from
sources is paraphrased, not quoted at length. No fetched page contained text addressing
me as an AI/agent; nothing to flag on prompt injection.

---

## 1. Shipping Instructions / SLI (Shipper's Letter of Instruction)

### Source 1 — NTCBFFA "Shipper's Letter of Instructions (SLI) Template"
- **URL:** https://ntcbffa.org/ftp/webdocs/DCB_SLI_NTCBFFA.pdf
- **What it is:** A filled-in specimen SLI form published by the National Customs Brokers/Forwarders trade association network (NTCBFFA — a regional NCBFAA-affiliated body). This is the actual widely-circulated U.S. export-compliance SLI layout (the model descended from the old NITL/NCBFAA form). Retrieved via WebFetch; binary PDF was re-read with the Read tool for full text since WebFetch's summarizer couldn't parse it directly — full form text and all 40 numbered boxes came through cleanly.
- **Fields, exactly as numbered/labeled on the form, in order:**
  1. USPPI Name
  2. USPPI Contact Name
  3. USPPI Contact Phone #
  4. USPPI EIN (IRS) #
  5. USPPI Address (Including Zip Code)
  6. Freight Location Address (If not Box #5)
  7. State of Origin
  8. Shipment Reference Number
  9. Mode of Transportation (checkboxes: Air / Vessel / Rail / Truck / Other)
  10. Carrier Code (per-mode columns: IATA code / SCAC / SCAC / SCAC / SCAC)
  11. Carrier/Vessel Name (per-mode)
  12. Containerized? (Yes/No checkboxes per mode, N/A for air)
  13. Transportation Reference # (Air Waybill number in ###-######## format / Booking # / optional / optional)
  14. Port of Unlading
  15. Port of Export
  16. Shipment contain Hazardous Materials? (Yes/No)
  17. USPPI and Ultimate Consignee related? (Yes/No)
  18. Routed Export Transaction? (Yes/No)
  19. Ultimate Consignee Name & Address
  20. Ultimate Consignee Type (Direct Consumer / Reseller / Government Entity / Other-Unknown)
  21. Country of Ultimate Destination
  22. Date of Export
  23. In-Bond Code
  24. In-bond Entry Number
  25. FTZ Identifier
  26. Domestic or Foreign (D/F) — per commodity line
  27. Schedule B / HTS Number and Commodity Description (vehicles require VIN/Year/Make/Model/Title Number)
  28. Quantity in Schedule B / HTS units
  29. Shipping Weight (kg)
  30. ECCN, EAR99 or USML Category No.
  31. Export Information Code
  32. Export License No., License Exception Symbol, DDTC Exemption No., DDTC ACM No. or NLR
  33. Value in Whole US Dollars (including inland freight and insurance)
  34. License Value by item (if applicable) (US Dollars)
  35. Does this shipment require additional PGA information? (checkboxes: AMS / ATF / DEA / EPA / FWS / NMFS / TTB)
  36. Certification statement checkbox ("statements made... true and correct")
  37. Printed Name
  38. Title
  39. Signature
  40. Date (MM/DD/YYYY)
  - Plus a free-text **Notes** box at the end.
- **Layout/format notes:** This is a dense single-page grid form, not prose — numbered boxes 1-40 arranged in a table with shaded header cells, very close to a customs/AES filing form. Boxes 9-13 form a multi-column "Transportation" sub-grid where each transport mode (Air/Vessel/Rail/Truck/Other) gets its own column of carrier code, carrier name, containerized flag, and reference number — meaning a single SLI can carry data for multiple legs/modes side by side. Commodity lines (26-34) are a repeatable table, one row per HTS line item, so a shipment with multiple commodities needs multiple rows with per-line HTS code, weight, ECCN and value — the current FreightBench generator's flat single-commodity model doesn't capture this. Structured codes present: EIN (USPPI tax ID), SCAC (per carrier), Schedule B/HTS number, ECCN/EAR99/USML category, DDTC exemption codes, "NLR" (No License Required) as a specific Export Information Code value. The Air Waybill reference field explicitly shows the ###-######## mask (3-digit prefix, dash, then serial), confirming the SLI is where the AWB/booking number gets cross-referenced back to the export filing.

### Source 2 — IncoDocs "Create a Shipper's Letter of Instruction (SLI) [Free Template]"
- **URL:** https://incodocs.com/template/shippers_letter_of_instruction
- **What it is:** A freight-tech vendor's product page describing/offering a downloadable SLI template, aimed at exporters.
- **Fields/sections described:** Shipper details, Consignee details, Notify Party (optional third party), Forwarding Agent (freight company + terms), product descriptions/specifications, number and type of packages, gross weight (kg), measurement (m³), shipping marks and numbers, hazardous goods declaration, Letter of Credit status, port of loading/discharge, method of dispatch (sea/air/road/rail), shipment type (FCL/LCL/breakbulk), pickup requirements, freight payment terms (prepaid/collect), authorized signatory name, signature, company seal/stamp.
- **Notes:** This is the more "commercial/logistics" flavored SLI (closer to what a freight forwarder wants for booking + B/L prep) versus NTCBFFA's version which is entirely U.S. export-compliance/AES flavored. Confirms the SLI genuinely has two overlapping-but-distinct flavors in practice: a customs/export-filing form (EIN, ECCN, Schedule B) and a shipment-instruction form (Incoterm, FCL/LCL, marks and numbers). A realistic generator should probably pick one flavor deliberately rather than blend fields incoherently.

### Source 3 — NCBFAA "Shipper's Letter of Instruction Model"
- **URL:** https://www.ncbfaa.org/membership-benefits/shipper's-letter-of-instruction-model
- **What it is:** The National Customs Brokers & Forwarders Association of America's own page hosting its model SLI (downloadable as a password-protected .xlsx; page itself doesn't render the form as text).
- **Findings:** Confirms NCBFAA is the current custodian/publisher of "the" model SLI referenced industry-wide (the file is literally password-protected against accidental overwriting of field headings, password "SLI"). The page explicitly states the model is a *recommended* format only — member companies customize wording, add supplementary fields, change field numbering, and choose fillable-PDF vs. web-based vs. spreadsheet delivery. Also confirms the SLI's core legal function: it conveys the shipper's authorization for the forwarder to file Electronic Export Information (EEI) in AES (the Automated Export System) on the shipper's behalf. **Important for a generator:** there is no single rigid universal SLI layout — field numbering and exact wording vary company to company, but the underlying data elements (USPPI identity/EIN, ultimate consignee, HTS/Schedule B, ECCN, routed-transaction flag, hazmat flag) are stable across versions because they map to mandatory AES/EEI data elements.

### Source 4 — Carrier-side "Shipping Instructions" (distinct from the shipper's SLI) — WebSearch snippets only, fetches blocked
- **URLs (fetch attempts failed — 403/502/timeout, so these are WebSearch-snippet sourced, not full fetches):**
  - Hapag-Lloyd — https://www.hapag-lloyd.com/en/online-business/documentation/shipping-instructions/shipping-instructions.html and the "Shipping_Instructions_User_Guide.pdf"
  - MSC — https://mscmkt3.com/MSCAssets/MyMSC/MyMSC_ShippingInstruction.pdf
  - CMA CGM — https://www.cma-cgm.com/static/CR/attachments/Shipping%20instructions%20format%20-%20CMA-CGM.pdf (this one is explicitly titled a "Shipping instructions format" spec — a strong lead for a future fetch attempt with a different tool/approach, but I could not retrieve its content this session)
- **What the snippets show:** These are carrier web-portal forms submitted directly to the ocean carrier (not to a forwarder) that feed B/L preparation. Per search snippets: Hapag-Lloyd's SI requires mandatory Shipper/Consignee/Notify Party details, specification of where the B/L draft should be sent, a general comments/instructions field, and a Container Number + Seal Number entry per container. MSC's myMSC SI covers booking reference, vessel details, payment terms, B/L information, shipper/consignee/notify addresses, and per-container details (number, seal, packages, cargo description, weight, reefer/OOG flags); MSC's amendment workflow names specific reason codes such as "Split B/L," "Seal Change due to physical inspection," "Typing Error," "Seal Damage during vessel operation."
- **Important distinction for the generator:** "Shipping Instructions" (carrier portal term, DCSA's usage, this section) and "Shipper's Letter of Instruction / SLI" (Sources 1-3, a forwarder-facing export-compliance document) are two different documents that share a confusingly similar name. The SLI authorizes AES filing and tells the *forwarder* what to do; the carrier SI is submitted (often via web portal) directly to the *carrier* or the carrier via the forwarder to populate the B/L. A realistic corpus should treat these as two distinct document types with different field sets, not one.

---

## 2. HAWB / MAWB (House / Master Air Waybill)

### Source 1 — eAWBlink "5 Create Air Waybill" user guide
- **URL:** https://www.eawblink.org/UserGuide/5_Create_Air_Waybill.htm
- **What it is:** A user guide for an electronic AWB creation platform (eAWBlink), walking through every data-entry field on a standard IATA-layout AWB.
- **Fields, in order of appearance on the form:**
  1. Air Waybill Number
  2. Template (dropdown to load a saved template)
  3. Shipper's Name and Address (mandatory)
  4. Issuing Carrier's Name and Address (mandatory)
  5. Consignee's Name and Address (mandatory)
  6. Accounting Information (Code + Description)
  7. Issuing Carrier's Agent Name and City
  8. Shipping Information (Reference Number, Optional Shipping Information)
  9. Requested Routing (Airport of Departure, Airport of Destination, Carrier Code, Flight Number, Departure/Arrival dates)
  10. Charges Information (Currency, Charges Codes, Weight & Valuation Charge, Other Charges, Declared Value for Carriage, Declared Value for Customs, Amount of Insurance)
  11. Also Notify (Name and Address)
  12. Handling Information (SPH codes [Special Handling], SCI, SSR, OSI, OCI — with Country Code, Information Identifier, Customs Information Identifier, Supplementary Customs Information)
  13. Consignment Rating Details (Pieces, RCP, Gross Weight, Rate Class Code, Commodity Item Number, Harmonized Commodity Code, Chargeable Weight, Rate/Charge, Goods Description, Dimensions, Volume, ULD information, SLAC [Shipper's Load and Count])
  14. Charge Summary (auto-computed totals)
  15. Other Charges (Code, due Agent/Carrier, Amount)
  16. Shipper Certification (checkbox + Agent Name, Execution Date, Execution Place, Issuing Carrier Name)
  17. Charges Collect Summary (Destination Currency, Conversion Rates, CC Charges, Total Collect Charges)
- **Layout notes:** Sequential top-to-bottom flow grouped into party info → routing → financial/charges → certification, matching the classic 3-box-wide IATA AWB grid described in the assignment brief. Each party section splits further into Name/Address/Contact sub-fields. This is the single richest field-level source found for AWB structure — the current FreightBench generator's flat "Shipper / Consignee / Commodity / Pieces / Gross weight / Volume" fields correspond to only a small slice of boxes 3, 5, and 13 here; it has nothing for Accounting Information, Handling Information codes (SPH/SCI/SSR/OSI/OCI), Rate Class Code, ULD info, or the two-tier Charges/Charges-Collect summary structure.

### Source 2 — DAKOSY "Cargo-IMP Amendments for ZAPP-Air / Message FWB" (v1.6.1e, Nov 2023)
- **URL:** https://www.dakosy.de/fileadmin/Redakteur/Support/Dokumentation/Entwicklerdokumentation/EDI/ZAPP-Air/FWB_v161_en.pdf
- **What it is:** A German air-cargo community-system operator's technical EDI implementation spec for the IATA Cargo-IMP **FWB** message — the electronic equivalent of a (Master) Air Waybill, built on Cargo-IMP FWB version 15 / Release 26 as defined by IATA/ATA. Retrieved via WebFetch, then re-read with the Read tool from the cached PDF for full text (WebFetch's own summarizer couldn't parse the binary).
- **Message segment structure, in order (Tag — Name — Occurrence — purpose), for the FWB message:**
  1. FWB — Standard Message Identifier (1) — identifies the message as FWB
  2. *(unlabeled)* — AWB Consignment Details (1) — AWB number, number of packages, volume
  3. ZEV — ZAPP-Air Envelope (1) — which ZAPP-Air participants are involved (community-system-specific, not core IATA)
  4. ZPI — ZAPP-Air Processing Information (1) — e.g. carrier's Tax ID (community-specific)
  5. FLT — Flight Bookings (1) — which flight(s) the AWB is booked on
  6. TRK — Trucking Information (0-1) — pre-carriage truck details to the airport
  7. SEC — Security information (0-1) — AWB security status
  8. RTG — Routing (1) — which carrier flies which leg
  9. SHP — Shipper (1) — shipper's address
  10. CNE — Consignee (1) — consignee's address
  11. AGT — Agent (0-1) — agent's address (for commission-entitled agents)
  12. ZFC — ZAPP-Air Forwarder Contact (1) — forwarder contact person (community-specific)
  13. SSR — Special Service Request (0-1) — handling particulars, e.g. max storage temperature
  14. NFY — Also Notify (0-1) — extra notify address
  15. ACC — Accounting Information (0-1)
  16. CVD — Charge Declarations (1)
  *(table continues beyond the 15 pages retrieved this session)*
- **Format conventions:** Cargo-IMP messages are subdivided into "Segments" tagged by a 3-letter code (e.g. **SHP** = shipper address, confirmed directly), each segment holding "Fields" separated by fixed length or delimiter characters (slash, dash, carriage return). Character set is restricted to capital A-Z (no diacritics/umlauts), digits 0-9, period (used as decimal point), dash, and space; format codes are defined as `a` = letters only, `n` = digits only, `m` = alphanumeric, `t` = alphanumeric + point/dash/space. Max line length is 70 characters; longer segment content wraps to a continuation line starting with `/`. The whole Cargo-IMP FWB message is wrapped in a UN/EDIFACT envelope (UNB/UNH segments, then the message body, then UNT/UNZ), addressed using structured "PIMA" addresses (7-field structure: CCS System Identifier[3] + CCS Group Code[3] + CCS Code Type[2] + CCS Participant Identifier[19] + optional Slash + optional Airport Code[3] + optional CCS Participant Office[2]). **This is the clearest evidence that a "real" e-AWB/FWB is a structured EDI record with mandatory/optional segment occurrence rules (M/O/D/X status codes), not free text** — useful if FreightBench ever wants a machine-message variant alongside the human-readable AWB grid.

### Source 3 — IATA Resolution 600b, "Air Waybill — Conditions of Contract" (CSC(32)600b)
- **URL:** https://www.iata.org/contentassets/783ac75f30d74e32a8eaef26af5696b6/csc-600b-en-28dec2019.pdf
- **What it is:** The official IATA Cargo Services Conference resolution defining the exact legal notice printed on the face of every AWB and the 12 numbered "Conditions of Contract" clauses printed on the reverse. Retrieved via WebFetch, re-read with the Read tool from cache for full text.
- **Structure found:** Part I is a single short paragraph-length "Notice" printed on the *face* of the AWB — it references acceptance of goods "subject to conditions of contract on the reverse," the carrier's right to route via any means/intermediate stops absent contrary shipper instructions, and points the shipper toward the liability-limitation notice (with the option to raise the liability cap by declaring a higher value and paying a supplemental charge). Part II is the "Conditions of Contract" proper, printed on the *reverse*, structured as 12 numbered clauses (several with sub-numbered parts, e.g. 2.1/2.2/2.2.1...): definitions (Carrier, SDR, Warsaw/Montreal Convention references); applicability of Warsaw/Montreal liability rules; incorporation of the carrier's own conditions of carriage/tariffs by reference; agreed stopping places; the default liability cap of **22 SDRs per kilogram** absent a higher declared value; shipper's payment guarantee; the shipper's right to declare a higher value for a supplemental charge; how partial-shipment loss/damage weight is apportioned; claim time limits (14 days for damage, 21 days for delay, 120 days for non-delivery, and a 2-year limit to bring suit); and shipper's regulatory-compliance obligations.
- **Notes for a generator:** This confirms the AWB, like an ocean B/L, has a hard front/back split — a compact data grid on the front, and a fixed block of dense liability/legal boilerplate on the back that virtually never varies shipment-to-shipment (only the carrier's own additional tariff-referenced conditions vary). A synthetic generator that wants to "quote" an AWB realistically should treat this Conditions-of-Contract block as a static template, not something to regenerate per shipment.

### Source 4 — LegalClarity, "Air Waybill (AWB): Definition, Legal Requirements, and Data"
- **URL:** https://legalclarity.org/air-waybill-awb-definition-legal-requirements-and-data/
- **What it is:** A legal-reference site's explainer on AWB requirements.
- **Findings:** Confirms the physical AWB is issued in a minimum of 8 copies/colors (green = issuing carrier's retained copy, pink = consignee's copy, blue = shipper's copy, remainder for customs/delivery/administrative use). Lists minimum mandatory data elements: 3-letter IATA origin/destination airport codes, shipper name/address, consignee name/address, nature-of-goods description, piece count, gross weight, dimensions, freight charges + payment method (prepaid/collect), currency, HS commodity codes. Confirms the functional MAWB/HAWB split (MAWB = contract between airline and forwarder covering the consolidation; each underlying shipper gets a HAWB from the forwarder) but does not give box-level layout detail or the check-digit formula — this page is weaker on layout precision than Source 1.

### Source 5 — AltexSoft, "Air Waybill (AWB) and e-AWB Explained"
- **URL:** https://www.altexsoft.com/blog/awb-air-waybill/
- **What it is:** A software-consultancy blog explainer on AWB/e-AWB.
- **Findings:** Confirms the 11-digit AWB number format (3-digit airline prefix + 7-digit serial + 1-digit check digit) and that the check digit equals the serial number modulo 7. States MAWBs are issued on the carrier's own pre-printed form while HAWBs use a neutral form carrying no carrier branding. Does not give a box-by-box layout.

### Source 6 — AWB number / check-digit algorithm confirmation (WebSearch snippets, cross-confirmed across multiple sources)
- **Sources:** Australian Border Force official check-digit-algorithm page (https://www.abf.gov.au/sdg-subsite/Pages/Check-Digit-Algorithms/Air-Waybill-Number-Validation.aspx), https://www.freight.domains/air-way-bill-check-digit-calculator/, https://airwaybilltracker.com/awb-number-format.html
- **Findings:** AWB number = 11 digits total, format `XXX-XXXXXXX-X`: first 3 digits = IATA airline prefix (e.g. 020 = Lufthansa Cargo, per a Beacon reference page surfaced in search), next 7 digits = serial number, final digit = check digit computed as **serial number mod 7** (unweighted modulus-7 — no weighting factors, unlike many other check-digit schemes). Worked example found: AWB 999-5372907-1 → 5372907 ÷ 7 leaves remainder 1, matching the check digit. A trailing check digit of 7, 8, or 9 is definitionally impossible/invalid since a mod-7 remainder can only be 0-6 — a good validity-rule a generator could enforce or deliberately violate for a "malformed AWB number" pathology.

### Source 7 — MAWB vs HAWB distinctions (WebSearch snippets)
- **Sources:** Ship4wd (https://ship4wd.com/import-guides/mawb-vs-hawb), gocargonet, howtoexportimport, tlstechno
- **Findings:** MAWB is issued by the airline (or its agent) to the freight forwarder and covers the whole consolidated shipment — shows total consolidated weight/volume and is the core document for airline billing, customs, and transport ops. HAWB is issued by the forwarder to each individual shipper within the consolidation, giving each shipper their own unique reference number essential for that shipper's customs clearance and final delivery; a HAWB typically carries more granular shipper/consignee/goods detail than the MAWB entry it rolls up into. Confirms the same "one MAWB : many HAWBs" nesting relationship that DCSA's ocean B/L standard describes for master/house B/Ls (see Section 3).

---

## 3. House / Master Bill of Lading

### Source 1 — DCSA "Standard for the Bill of Lading: A roadmap towards eDocumentation" (Dec 2020)
- **URL:** https://www.digitalizetrade.org/files/projects/documents/20201208-DCSA-P4-DCSA-Standard-for-Bill-of-Lading-v1.0-FINAL.pdf
- **What it is:** The Digital Container Shipping Association's (carrier-consortium-backed: Maersk, MSC, Hapag-Lloyd, ONE, CMA CGM, COSCO, Evergreen, HMM, Yang Ming, ZIM are DCSA members/backers) official published data standard for the ocean Bill of Lading, covering both the physical B/L and its electronic form (eBL), and explicitly also covering the Sea Waybill (eSWB). WebFetch's own summarizer couldn't parse the binary PDF; re-read in full with the Read tool from the cached copy — got complete text and the standardized field table image.
- **Standardized B/L data field categories and fields (Figure 2 in the source, exactly as labeled), grouped by Category:**
  - **Party:** Shipper, Consignee, Notify party, Also notify, Shipper forwarding agent, Consignee forwarding agent, Forwarding agent reference number, Freight payer, SCAC code, Tax ID / LEI, Address, Phone, Email/Fax, Consignee reference number
  - **Transport document:** Date of issue, Place of issue, Transport document number, Number of original B/Ls, Transport document issuer, Signature, Onboard date, Terms & conditions, Received for shipment date, Disclaimer, Transport document type, Number of copies
  - **Shipment:** Place of Receipt, Port of Loading, Port of Discharge, Place of Delivery, Declared value, Service Type, Shipment terms, Onward inland routing, Precarried by, Export reference number, Point and country of origin of goods, Carrier booking number
  - **Vessel:** Vessel, Voyage number
  - **Cargo item:** Marks & numbers, Description of goods, Measurement, Total number of containers or packages received by the Carrier, HS code, Cargo Gross Weight, Reefer Humidity, Unit, Part load indicator, Reefer Temperature setting, Reefer ventilation
  - **Shipment equipment:** VGM, Total container weight, Container tare weight, Container type, Container number
  - **Seal:** Seal number, Seal source
  - **Charges:** Prepaid amount, Collect amount, Freight & charges, Prepaid/collect, Freight payable at, Currency
  - **Carrier clauses:** Carrier clauses
  - **Booking:** Service contract, Commodity
  - Each field carries a Mandatory / Conditional / Optional stipulation **per process step** (Booking request → Booking confirmation → Prepare B/L → Issue B/L). Example given directly in the source: "Shipper" is mandatory at every step; "Onward inland routing" is conditional (only when the customer arranges onward transport); "Also notify" is optional throughout.
  - Appendix table (partially retrieved) has this exact column structure for every field: **# | Field | UN Assigned ID | Current definition of field | Data input format | 1.1 Booking request | 1.2 Booking confirmation | 1.3 Prepare B/L | Conditions (if applicable) | 1.4 Issue B/L**. Sample rows retrieved: field #1 Transport document Issuer (UN Assigned ID UN00001809, format = Entity Name/Address/Phone/Fax/Website/Issuer ID e.g. SCAC Code, Mandatory at every step); field #2 Shipper (UN00001807, format = company name + structured or L/C-matching unstructured address + contact + LEI/Tax ID, Conditional→Mandatory across steps, can be left blank until SI submission if a forwarding agent was given at booking); field #3 Consignee (UN00001808, similar format plus "to order" identifier, Optional→Conditional, explicitly blank for "to order" B/Ls).
- **Process notes:** The end-to-end documentation flow DCSA models is Booking Request → Confirm Booking → **Prepare B/L** (shipper submits Shipping Instructions/SI, carrier validates, drafts B/L, shipper approves) → **Issue B/L** → Arrival Notice → Release Shipment. This confirms "Shipping Instructions" in carrier/DCSA usage is the data submission step that produces the B/L draft — reinforcing the SLI-vs-SI distinction flagged in Section 1.
- **This is the single most useful find for a corpus generator in this whole cluster**: it gives an exact, industry-consensus, machine-usable field taxonomy for the B/L with per-field mandatory/conditional/optional status tied to shipment lifecycle stage — exactly the kind of ground truth a generator needs to build a B/L field set that's neither over- nor under-specified, and to model realistic *omissions* (e.g. blank Consignee for a "to order" B/L, blank Notify Party, conditional Onward Inland Routing) rather than guessing which fields are "usually" blank.

### Source 2 — FIATA Standards presentation (CAREC Federation of Carrier & Forwarder Associations, "Module 06 — FIATA Standards")
- **URL:** https://www.carecprogram.org/uploads/Module-06-FIATA-Standards.pdf
- **What it is:** A training slide deck (2013, CAREC Program / CFCFA) explaining FIATA's standard forwarding documents, including an embedded full-page image of an actual specimen **FBL** (FIATA Multimodal Transport Bill of Lading) form. WebFetch's summarizer couldn't parse the binary; re-read with the Read tool from cache, which rendered the slide images directly (including the specimen FBL form) for visual inspection.
- **The 8 FIATA standard documents/forms, exactly as listed:** Negotiable FIATA Multimodal Transport Bill of Lading (FIATA FBL), Non-negotiable FIATA Multimodal Transport Waybill (FIATA FWB — note: FIATA's own "FWB" abbreviation is unrelated to and a naming collision with IATA/Cargo-IMP's air-cargo FWB message in Section 2), Forwarders Certificate of Receipt (FIATA FCR), Forwarders Certificate of Transport (FIATA FCT), FIATA Warehouse Receipt (FIATA FWR), Shippers Declaration for the Transport of Dangerous Goods (FIATA SDT), Forwarding Instructions (FIATA FFI), Shippers Intermodal Weight Certificate (FIATA SIC).
- **Specimen FBL form fields, read directly off the embedded form image, top to bottom:** Consignor; document header showing "FBL No. ___" and a "CN" (copy/negotiable?) marker plus the CIFA/ICC branding line ("negotiable FIATA multimodal transport bill of lading, issued subject to UNCTAD/ICC rules for multimodal transport documents"); Consigned to order of; Notify address; Place of receipt; Ocean vessel; Port of loading; Port of discharge; Place of delivery; Marks and numbers; Number and kind of packages; Description of goods; Gross weight; Measurement; Declaration of Interest of the consignor in timely delivery (Clause 6.2); Declared value for ad valorem rate according to the declaration of the consignor (Clauses 7 and 8); a boilerplate liability/negotiability paragraph (goods accepted "in apparent good order and condition," negotiability requires surrender of one original, duly endorsed); Freight amount; Freight payable at; Place and date of issue; Cargo insurance through the undersigned (checkboxes: not covered / covered per attached policy); Number of Original FBL's; Stamp and signatures; a printed serial number at the bottom (specimen showed "1070000004").
- **Issuance/format rules, exactly as stated:** Only FIATA member national freight-forwarder associations' qualifying members may issue FBLs (multi-year forwarding experience, membership fee current, at least one senior staffer with multiple years of forwarding experience required). Documents must carry **continuous serial numbers**; the issuing national association must stamp its seal on the FBL before dispatch to the forwarder; the issuer must carry freight-forwarder liability insurance. Print samples must be FIATA-approved before printing. FBL text is officially in English (translations permitted but the issuer bears translation cost/accuracy risk, and English is the legally controlling version). FBL numbering identifies both the issuing national forwarder association and its country. Territory-of-use restrictions apply; document validity is **5 years**, auto-renewing for another 5 unless a party gives 6 months' notice to terminate. A long list of ~45 countries where FBL is in active use was given (Australia, Austria, Belgium, Canada, China, France, Germany, Japan, UK, US, and many more).
- **Notes for a generator:** The FBL is explicitly a *carrier-type* document (the forwarder takes on carrier-like liability under FIATA's own model terms/UNCTAD-ICC rules) even though it's issued by a forwarder, not an asset carrier — conceptually this is the direct FIATA-standard analog of a "House B/L," and its field set (Consignor/Consigned-to-order-of/Notify address/ocean vessel/ports/marks-numbers/packages/goods description/weight/measurement/freight amount/freight payable at) is nearly identical to the carrier B/L layout found in Source 3, confirming House and Master B/Ls share the same front-page field grid and differ mainly in issuer identity, applicable terms/liability regime, and the specific numbering series.

### Source 3 — Maersk sample Bill of Lading (specimen PDF, third-party-hosted copy)
- **URL:** https://africactn.com/staging/wp-content/uploads/2023/02/Example-Maersk-BIll-of-Lading.pdf
- **What it is:** A blank specimen "Bill of Lading for Ocean Transport or Multimodal Transport" issued in Maersk's name (found via WebSearch, hosted on a third-party freight-training site). WebFetch's summarizer couldn't parse the binary; re-read with the Read tool from the cached copy, which returned the complete, exact form text.
- **Fields, exactly as printed on the form, by region:**
  - Top-right block: **SCAC**, **B/L No.**
  - **Booking No.**
  - **Export references** | **Svc Contract**
  - **Onward inland routing** (explicitly captioned: "Not part of Carriage as defined in clause 1. For account and risk of Merchant")
  - **Vessel** (see clause 1+19) | **Voyage No.** | **Place of Receipt** (captioned "Applicable only when document used as Multimodal Transport B/L (see clause 1)")
  - **Port of Discharge** | **Place of Delivery** (same Multimodal-B/L-only caption)
  - Section header **"PARTICULARS FURNISHED BY SHIPPER"** over a single wide grid box captioned: **Kind of Packages; Description of goods; Marks and Numbers; Container No./Seal No.** | **Weight** | **Measurement** — i.e. on this real specimen, package type + goods description + marks/numbers + container/seal number are all one combined free-text cell, not four separate boxes; only Weight and Measurement get their own columns. Caption beneath: goods particulars are "as declared by Shipper, but without responsibility of or representation by Carrier (see clause 14)."
  - **Freight & Charges** | **Rate** | **Unit** | **Currency** | **Prepaid** | **Collect**
  - **Carrier's Receipt** (captioned "Total number of containers or packages received by Carrier", see clause 1 and 14) | **Place of Issue of B/L**
  - **Number & Sequence of Original B(s)/L** | **Date of Issue of B/L**
  - **Declared Value** (see clause 7.3) | **Shipped on Board Date (Local Time)**
  - **Forwarder** (signature block) ... **Signed for the Carrier Maersk A/S** ... **As Agent(s)**
  - A dense boilerplate legal paragraph beginning "SHIPPED, as far as ascertained by reasonable means of checking..." — references "all those terms and conditions on the reverse hereof numbered 1-26" plus the carrier's applicable tariff, and spells out negotiable-vs-non-negotiable delivery mechanics (surrender of an endorsed original required only for a negotiable B/L).
- **Notable absence:** the specimen's Shipper / Consignee / Notify Party fields are large **unlabeled blank boxes** at the top of the form (positionally understood, not printed as literal "Shipper:"/"Consignee:"/"Notify Party:" captions) — the printed field labels only start appearing at the Vessel/Voyage/Port row. This is a real-world layout wrinkle a synthetic generator would otherwise never guess: not every field on a real B/L is textually labeled on the document image itself; some are conveyed purely by position/convention.
- **Layout/format notes:** Confirms the B/L, like the AWB, has a hard split between a front-page data grid and a fixed-numbering (here, 26-clause) legal boilerplate block on the reverse that's carrier-standard, not shipment-specific. Confirms the SCAC+B/L-number pairing sits together in a small box at top right, distinct from Booking No. (a separate field/number series). Multimodal-only fields (Place of Receipt, Place of Delivery) are explicitly captioned as conditional on document type, mirroring DCSA's own conditional-field logic in Source 1.

### Source 4 — exportnesthub, "How to Read a Bill of Lading: Field-by-Field Guide"
- **URL:** https://exportnesthub.com/how-to-read-bill-of-lading/
- **What it is:** A trade-education site's field-by-field B/L walkthrough.
- **Fields, in the order presented:** Shipper or Exporter, Consignee, Notify Party, Bill of Lading Number, Booking Number, Carrier and Freight Forwarder Details, Vessel Name, Voyage Number, Place of Receipt, Port of Loading (POL), Port of Discharge (POD), Place of Delivery or Final Destination, Container Number, Seal Number, Shipping Marks and Numbers, Number and Type of Packages, Description of Goods, HS Code, Gross Weight, Measurement or CBM, Freight Terms, Number of Original Bills Issued, Place and Date of Issue, Carrier Signature or Authentication.
- **Container number format given:** ISO 6346 structure — 3-letter owner code + 1-letter equipment-category identifier + 6 serial digits + 1 check digit (worked example given: "MSCU 123456 7"). This is a precise, checkable format a generator could validate/deliberately corrupt for a "bad container number" pathology, distinct from and complementary to the B/L-number-itself format in Source 6 below.

### Source 5 — iContainers, "House and Master Bill of Lading: A Complete Guide"
- **URL:** https://www.icontainers.com/help/differences-between-house-master-bill-of-lading/
- **What it is:** A digital freight forwarder's explainer comparing House and Master B/Ls.
- **Findings:** Master B/L is issued by the shipping carrier to the NVOCC/forwarder on the carrier's own pre-printed form; House B/L is issued by the NVOCC/forwarder to its own customer on the NVOCC's pre-printed form. Party-naming differs by document: on the Master B/L, Shipper = the NVOCC or its agent and Consignee = the destination agent or NVOCC itself; on the House B/L, Shipper = the actual exporter and Consignee = the actual importer/receiver. Critically: **all other fields — vessel info, cargo description, container/seal numbers, weight, container count, sail date — must be identical between the Master and House B/L for the same physical cargo**; only shipper, consignee, notify party, and pickup-location fields are allowed to differ. This is a directly implementable consistency rule for a generator that wants to emit a matched House+Master B/L pair for the same shipment (a realistic pathology would be to break this consistency rule deliberately, e.g. mismatched container numbers between the two).

### Source 6 — B/L number format (WebSearch snippets + one direct fetch)
- **Sources:** https://docs.vizionapi.com/docs/formatting-bl (fetched directly), plus WebSearch snippets citing Standard Carrier Alpha Code (SCAC) conventions and a CBP Ocean House Bill of Lading FAQ
- **Findings:** No single universal numeric format exists across carriers (unlike the AWB's strict 11-digit/mod-7 rule) — each ocean carrier has its own house format. Master B/L numbers are generally **SCAC (carrier's 2-4 letter Standard Carrier Alpha Code) + a carrier-specific alphanumeric/numeric sequence**, e.g. patterns cited include pure 9-12 digit numeric (Maersk, OOCL-style), 3 letters + 7-9 digits (APL/CMA-CGM-style), or explicit SCAC-prefixed strings like "HLCU" + 13 characters for Hapag-Lloyd; some carriers (COSCO cited) accept the number with or without the SCAC prefix and normalize it. A separate WebSearch snippet on US customs manifest rules states the B/L identifier is capped at 16 characters total, built from the 4-character SCAC plus up to 12 more characters, and that Ocean House B/Ls specifically are always required to carry a SCAC as part of their identifier. **Practical implication for a generator:** unlike the AWB, there's no single checkable B/L-number algorithm to validate against — realism here comes from mimicking a specific carrier's known SCAC + format pattern (e.g. "MAEU" + 9 digits for Maersk) rather than inventing an arbitrary alphanumeric string.

### Source 7 — Cross-confirmation snippets (WebSearch only)
- Independent WebSearch hits located two more live specimen FBL PDFs with near-identical field lists to Source 2's embedded image — https://ioc.xtec.cat/materials/FP/Recursos/fp_cin_m05_/web/fp_cin_m05_htmlindex/WebContent/u1/media/fbl.pdf and https://www.benship.hu/benship_uploads/files/fuvarokmanyok/fbl-minta.pdf — both snippet-confirmed as opening with Consignor / Consigned to order of / Notify address / Place of receipt / Port of loading (first) or /Ocean vessel / Port of discharge (second), cross-validating the field order read off Source 2's embedded image (attempted direct WebFetch of both failed — binary PDFs the summarizer couldn't parse, and I did not spend further budget re-reading them via the Read tool since Source 2 already gave equivalent, fuller data).
- Maersk's own FAQ pages (https://www.maersk.com/support/faqs/details-in-bill-of-lading, https://www.maersk.com/support/faqs/what-is-bill-of-lading) confirm in prose, without a full fetch succeeding, that Maersk considers shipper/consignee name+address, goods description, quantity, transport method, and shipment date to be the required core B/L contents — consistent with, but far less detailed than, Source 3's actual specimen form.

---

## Summary of fetch failures (for transparency)

Several promising URLs could not be retrieved this session and are *not* used as sourced findings above beyond what a WebSearch snippet independently supported: Expeditors SLI PDF (403), UPS SLI PDF (timeout), Hapag-Lloyd Shipping Instructions User Guide PDF and details page (403 twice), MSC MyMSC Shipping Instruction PDF (502), CMA CGM Shipping Instructions format PDF (403), Grokipedia's Air Waybill page (403), Magaya's AWB fields help page (TLS certificate error). Where these appeared only as WebSearch snippets, that's flagged explicitly in the relevant source entry above rather than presented as a full fetch.
