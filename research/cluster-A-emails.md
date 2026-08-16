# FreightBench Cluster A Research — Booking Requests, Rate Requests, Booking Confirmations

Research method: WebSearch + WebFetch only. All content below was actually retrieved (via WebFetch page content, or via WebFetch on a PDF followed by the Read tool on the saved binary, or via specific/substantial WebSearch result snippets). No content was filled in from general parametric knowledge. Verbatim quoting kept under 15 words per source in a row; field/segment names are reproduced fully and exactly since they are short technical terms, not prose.

## Access limitations encountered (report transparently)

- **Reddit is not reachable at all.** WebFetch returned an explicit tool-level block ("Claude Code is unable to fetch from www.reddit.com" / "...old.reddit.com") for every reddit.com and old.reddit.com URL tried, including r/logistics and r/Freightforwarding search URLs. WebSearch queries targeting reddit.com (including `site:reddit.com/r/freightforwarding`, `site:reddit.com/r/logistics`, and quoted-phrase variants) never returned actual Reddit threads in the result set — only unrelated marketplace/tool listings. So **zero Reddit sources** could be included despite many attempts with varied phrasing. This is a real gap against the brief; the forum angle is not covered.
- **LinkedIn**: no searches surfaced fetchable LinkedIn posts with real quoted booking/quote emails; results were limited to company profile pages or generic glossary sites repeating the same LinkedIn-adjacent phrasing. No LinkedIn sources included.
- Several vendor help-center pages returned HTTP 403 to WebFetch (Flexport support.portal.flexport.com articles, TraceLink, getmage.io, CMA CGM's own SI Template PDF hosted at cma-cgm.com, LogixMindz — this last one via a TLS/certificate error rather than 403). Where a 403'd page's content could still be characterized from a substantial, specific WebSearch snippet, that is marked clearly as "WebSearch snippet only, page not fetched."
- Two PDFs (ONE/Ocean Network Express booking guide, MSC IFTMBC EDIFACT implementation guide) came back from WebFetch as unparsed binary; I recovered full readable content from both by re-reading the auto-saved local PDF copy with the Read tool (page images), not by downloading anything new myself.
- One source (DocShipper booking-number glossary) produced booking-number digit examples via WebFetch's summarizing step that look suspicious — pattern-matches ISO 6346 **container** number format rather than a **booking** number, and may be the fetch tool's own plausible-sounding invention rather than text actually on the page. Flagged inline; treat as low-confidence.

---

## 1. Booking Request Emails (shipper/customer → freight forwarder)

### Source 1.1 — ONE (Ocean Network Express) "Outbound eCommerce Guide" (Booking Request section)
- **URL:** https://ecomm.one-line.com/ecom/DocRoot/guide/How_to_booking_request.pdf
- **Type:** Booking request
- **What it is:** Official 20-page user guide from Ocean Network Express (ONE), a top-6 global container carrier, explaining every field on its online "Booking Request" form for shippers/forwarders/eBooking parties. Retrieved as PDF, read via the Read tool's PDF page-image support. Dated "as of April 2021."
- **Fields observed (full, exact):**
  - Header/meta: Manual Booking Number, Template (dropdown of saved templates), Copy Previous Booking
  - Customer Information: Name, e-Mail Address (supports multiple, for confirmation notification), Phone No., Fax No., Contract No. (dropdown: specific contract / "Others" / "No Contract"), Address, Named Account ("Unable to Find Named Account or Not Applicable" option), Person placing Request (Shipper / Forwarder / eBooking Party)
  - Parties: Shipper (Company, Address), Freight Forwarder (Company, Address, "Same as Shipper" checkbox), Consignee (Company, Address) — each validated against an address book with a green/yellow/black status indicator (Validated / needs validation / no data)
  - Location: Service Type (Origin/Destination each set to CY, CFS, or DR/Door), Origin (Place of Receipt), Loading Port ("Same as above" checkbox), Discharging Port, Destination (Place of Delivery), Booking Office
  - Country-conditional customs fields: **US** — House Manifest Filing (Yes/No), AMS for House B/L (By Carrier Non-Auto / By NVOCC Auto), AES ITN; **Canada** — House Manifest Filing (Yes/No), ACI for House B/L (By Carrier Non-Auto / By NVOCC Auto), CERS License, P.O.R.CERS; **Mexico** — Shipper TAX ID, Consignee TAX ID, Notify TAX ID; **China origin** — MOT No. (mandatory for NVOCC shipper bookings ex-China)
  - Schedule: Departure Date OR Vessel (radio choice), Return Date, Manage Schedule (bulk-duplicate a booking across multiple vessels/weeks — Booking1, Booking2... rows)
  - Vessel Schedule Inquiry (List/Calendar view): Inland Cut Off Time, Port Cut Off Time, Loading Port, Vessel, Lane, Departure Date
  - Pick Up: Pick Up Date (date + time)
  - Container: Type (dropdown, e.g. DRY), Size (e.g. 40', 40H), Quantity/Total, Quantity/S.O.C. (Shipper's Own Container); FLEX OK (Y/N — accept 40'/40'HC substitution at empty pick-up); SPLIT OK (Y/N — accept ONE splitting the booking across sailings)
  - Pick Up Information (appears only if Origin service type = Door): Type, Size, Total, Supplier's Name, Contact Person, Address, Postal/Zip, Phone No., Fax No. (or, for Europe/Africa: E-Mail instead of Fax), Drop-Off Date & Time, Pick-Up Date & Time, Remarks — with "Add/Remove/Copy Inland Pick Up" actions for multi-stop pickups
  - Cargo: Commodity (chosen from contract-filed list, or free-text spyglass search returning an HS-style Code + Commodity description list, e.g. searching "coffee" returns codes like 210111, 090111 etc.), Total Estimated Weight (+ unit, e.g. KGS)
  - Reefer Cargo (if equipment = Reefer): Unit (F/C), Degree, Ventilation Value + Type (e.g. "1 CMH"), Nature (Chilled / Frozen / Fresh), Humidity (%), Genset (Yes/No)
  - Dangerous Cargo (if commodity is hazardous): UN No., Class (IMDG class), Flash Point (°C, enabled only for Class 3), Package Group (None/I/II/III), Dangerous Cargo Certificate Upload — File Type dropdown values: **DGD-Final, DGD-Preliminary, MSDS, Pkg Certificate, Tank Certificate, Other-Class 1 Vanning Survey, Other-Competent Authority Letter 'CAA', Other-Specific Product Certificate 'fish meal', Other-Class1 Port Permits, Other-Import License, Other-Export License, Other-LOI 'Letter of Indemnity', Other-Plastic Repartition Letter**
  - Awkward Cargo (if equipment = Open Top or Flatrack): Package (count + type, e.g. BAG), Gross Weight (+unit), Net Weight (+unit), Commodity, Unit (e.g. CM), Length, Width, Height, Remark(s)
  - Special Instruction on Booking: free-text box explicitly described as "the box to make notes that you would make in an email booking or phone booking to a Customer Service Export Booking Agent"
  - Reference No.: Invoice Ref. No., BKG SH Ref. No. (Booking Shipper Reference), BKG FF Ref. No. (Booking Freight Forwarder Reference), S/I SH Ref No (Shipping Instruction Shipper Reference), S/I FF No (Shipping Instruction Forwarder Reference) — plus a "Multiple Reference Numbers" Yes/No toggle and "Manage Reference No." grid for bulk-duplicated bookings
  - e-Mail Notification: Event (Vessel Departure, Vessel Advance/Delay) x Subscribe/Unsubscribe
  - Post-submit: Booking Status screen columns — Request No., Booking No., Split (Y/N), Via (Web/EDI/Offline/Portal), Request Date, Booking Date, Vessel, Estimated Departure Date, Status (e.g. PROCESSING)
- **Notes on phrasing/layout conventions:** This is a structured web form, not prose email — but it's the single most complete real-world field taxonomy found in this research, and it explicitly maps its "Special Instruction" free-text field to what a human would type in an actual booking email. Two details a synthetic generator almost certainly misses: (1) there are up to **five separate reference-number fields** tracked independently (shipper's own ref, forwarder's own ref, invoice ref, plus separate SI-stage refs) rather than one "our reference" field — real bookings distinguish "your ref" (shipper) from "our ref" (forwarder) from invoice number; (2) customs/compliance fields are **conditional on trade lane** (AES ITN only if US origin, CERS only if Canada origin, TAX IDs only if Mexico is origin or destination, MOT No. only if China origin + NVOCC) rather than a flat field list that's the same regardless of country pair. Also notable: the system distinguishes "booking uploaded" (into the carrier's system) from the actual "Booking Receipt Notice" the customer later receives — these are two different confirmation events, not one.

### Source 1.2 — Tier2 Systems, "Freight Booking Management: An Ops Guide"
- **URL:** https://tier2systems.com/en/blog/freight-booking-management-guide/
- **Type:** Booking request (with downstream confirmation detail)
- **What it is:** Vendor (freight-tech ops platform) blog post aimed at forwarder operations staff on managing the booking lifecycle.
- **Fields observed:** Origin and destination ports, commodity description with HS code, gross weight, cargo dimensions, container type and count, cargo ready date, special requirements (reefer / hazmat / OOG — out of gauge), customer's preferred carrier; confirmation-side: vessel name, voyage number, ETD, ETA, documentation cutoff dates; post-confirmation: Shipping Instructions (SI) submission deadline, dangerous goods declarations, certificates of origin.
- **Notes on phrasing/layout conventions:** No literal email template shown, but a striking operational-realism data point worth encoding: it states a single shipment "can generate 40 or more messages across its lifecycle," with "10 to 20 emails per booking" phase alone. That implies real booking correspondence is rarely a single clean email — it's usually a thread with amendments, follow-ups, and confirmations, which the current single-shot generator doesn't model at all.

### Source 1.3 — freightcourse.com, "How to Book a Container in Shipping: A Quick Guide"
- **URL:** https://www.freightcourse.com/how-to-book-a-container-in-shipping/
- **Type:** Booking request
- **What it is:** Freight-training/education site article walking through the container booking process step by step.
- **Fields observed:** Shipper, Consignee, "Notify Party" (named explicitly), cargo type/dimensions/weight, special handling requirements, load type, "Cargo Ready Date" (named explicitly), origin and destination, permits/documentation needs, number of containers, vessel name, voyage number, ETD, ETA, sailing schedule selection, pickup details, "Booking Instructions," container type and quantity.
- **Notes on phrasing/layout conventions:** Refers to the resulting document as a "booking confirmation (also referred to as pro forma booking)" and says it "acts like a receipt" — useful vocabulary ("pro forma booking") the generator could use as an alternate document label. No literal sample email text.

### Source 1.4 — IncoDocs, "Create and Download a Shipper's Letters of Instruction Document"
- **URL:** https://incodocs.com/blog/shippers-letters-of-instruction-freight-export/
- **Type:** Booking request (companion document that typically travels with/soon after a booking request)
- **What it is:** Vendor (trade-documentation software) blog explaining the Shipper's Letter of Instruction (SLI), the document a shipper hands a forwarder alongside or right after booking.
- **Fields observed (full):** Shipper details (name, address, phone, email), Consignee details, Notify Party, Forwarding Agent details, Shipper's reference number, vessel name and voyage number, container number and seal number, shipping marks, commodity/nature of goods description, total number of packages, total gross weight (kg/lbs), total packing size (cbm/cuft), country and state of origin, value of goods and currency, port of loading and discharge, method of dispatch (sea/air/road/rail), shipment type (FCL/LCL/breakbulk), Incoterm agreement, pickup requirement confirmation, hazardous cargo declaration (UN#, class, packing group), letter of credit status, insurance status, ISPM packing details, freight payment terms (prepaid vs. collect), special instructions, authorized signatory company/name/date.
- **Notes on phrasing/layout conventions:** Confirms "seal number" and "shipping marks" as fields the current generator's flat field list omits entirely. Page didn't specify email transmission conventions.

### Source 1.5 — mg-spl.com (Matrix Global Singapore), "What Information Do You Need to Request a Freight Quote?"
- **URL:** https://mg-spl.com/what-information-do-you-need-to-request-a-freight-quote/
- **Type:** Straddles booking request / rate request (a Singapore-based forwarder's advice on what a customer must supply before either a quote or a booking can proceed) — logged fully under Rate Requests below (Source 2.1) since that's its primary framing, cross-referenced here because its "Example Template Provided" line doubles as realistic booking-request shorthand: *"FCL sea freight from Ho Chi Minh / Cat Lai Port, Vietnam to Nhava Sheva, India. 2 × 40'HC containers, general cargo, ready in early August."* Note the terse, non-templated, single-paragraph phrasing — real requests are often this compressed, not a labeled field block.

---

## 2. Rate Requests / Spot Quote Emails

### Source 2.1 — mg-spl.com (Matrix Global Singapore), "What Information Do You Need to Request a Freight Quote?"
- **URL:** https://mg-spl.com/what-information-do-you-need-to-request-a-freight-quote/
- **Type:** Rate request / spot quote
- **What it is:** Singapore freight forwarder's advisory blog post for shippers on how to ask for a workable quote.
- **Fields observed (full):** Company name, Contact person, Email address, Phone/WhatsApp, Company type (importer/exporter/forwarder/etc.), Operating location/country; Port of loading, Port of discharge, Place of receipt (if inland pickup needed), Final delivery location (if inland delivery needed); Transport mode (FCL sea freight / LCL / air freight / reefer / dangerous goods / other); Commodity name, HS code, Cargo value, Packaging type, fragile/sensitive/high-value/regulated flags; Number of containers + type (20'GP, 40'GP, 40'HC etc.), Gross weight per container, for LCL/air: number of packages + gross weight + dimensions + total CBM; Cargo ready date, Preferred shipment week, Required arrival period; Service scope (port-to-port only vs. including pickup/customs clearance/insurance/inland delivery); Reefer temperature settings, DG details (UN number, IMO class, MSDS), oversized/heavy cargo specs.
- **Notes on phrasing/layout conventions:** Explicitly warns that a bare "Please quote Singapore to India" is an unusably vague real-world request — i.e., real incoming rate-request emails vary enormously in completeness, and a realistic corpus should include some genuinely underspecified requests, not just complete field sets. Gives the compressed one-paragraph example quoted above under 1.5.

### Source 2.2 — Freightamigo, "Freight Quote Email Templates: Pro Tips 2026"
- **URL:** https://www.freightamigo.com/en/blog/logistics/how-to-craft-an-effective-freight-quote-request-email-samples-and-best-practices/
- **Type:** Rate request / spot quote
- **What it is:** Vendor (digital freight forwarder) blog post with worked sample RFQ emails for two shipment types.
- **Content observed:**
  - Sample 1 (Domestic LTL): Greeting **"Dear Freight Team,"**; body covers pickup/delivery addresses, cargo specs (weight, dimensions, value, HS code), services needed, Incoterms, ready date; sign-off **"Thanks, [Your Name/Company/Phone]"**; subject line pattern **"RFQ - LTL Freight Quote: [quantity] [origin] to [destination], Ready [date]"**
  - Sample 2 (International Ocean LCL): same greeting; body covers origin/destination addresses, cargo details (weight, CBM, HS code), mode preference, insurance needs, Incoterms, deadline; sign-off **"Regards, [Your Name/Company]"**; subject pattern **"RFQ - Ocean LCL Quote: [CBM] [origin] to [destination], Alt [mode] Option"**
  - Recommended call-to-action line: "Please confirm receipt and provide an itemized quote with transit times by EOD."
- **Notes on phrasing/layout conventions:** Confirms **"RFQ - "**-prefixed subject lines carrying compressed shipment parameters (quantity/CBM + lane + ready date) as a real convention — quite different from the current generator's plain-prose intro. Recommends **bullet points or short tables** in the body rather than a flat labeled block, and explicitly separates sign-off register by relationship warmth ("Thanks," vs. "Regards," vs. presumably more formal alternatives). Recommends itemized breakdowns (freight + THC + demurrage for ocean; chargeable-weight rates for air) and "all-in door-to-door" pricing asks — i.e., real rate requests often ask for a *cost breakdown structure* back, not just a single number.

### Source 2.3 — emailsinenglish.com, "Request for Freight Quotation Email"
- **URL:** https://www.emailsinenglish.com/request-for-freight-quotation-email/
- **Type:** Rate request / spot quote
- **What it is:** An ESL/business-English email-writing reference site with a full worked template for requesting a freight quote.
- **Content observed (full template structure):**
  - Header block shown explicitly: **To: / Bcc: / Cc: / From: / Subject:** — subject phrased as "Requesting Freight Quotation for [goods type]"
  - Greeting: **"Respected Sir/ Madam,"**
  - Opening line pattern: "We have learned about your company's courier and freight services, and I'm writing this email to request a quotation for [volume/weight/size] of goods for [transportation mode]."
  - Body continues with business type and destination requirements, then: "the quotation as per the details attached at your earliest convenience, including any applicable discounts."
  - Closing: **"Thank you," / "Sincerely,"** then name and contact details
- **Notes on phrasing/layout conventions:** This is a materially different register from the Freightamigo sample above — much more formal/deferential ("Respected Sir/Madam," "at your earliest convenience") and reads as influenced by South Asian/subcontinent business-English conventions, which are extremely common in real freight-forwarding correspondence given the demographics of the industry's operations staff. A separate general WebSearch (not a specific single page, so noted as pattern-level only) corroborated that "Dear Sir/Madam" and "Dear Sirs" greetings persist in shipping-industry email specifically even though general business-English style guides now call them outdated — i.e., the industry lags general email norms. This directly supports diversifying greeting style beyond the generator's flat "Hi," / "Hello,". Also notable: this template explicitly shows a **To/Bcc/Cc/From/Subject header block** as part of "the email," reinforcing that realistic samples should sometimes show real headers, not just a body.

### Source 2.4 — sfi.com (Straight Forwarding Inc.), "How to Ask For a Freight Quote"
- **URL:** https://sfi.com/blog/how-to-ask-for-a-freight-quote
- **Type:** Rate request / spot quote
- **What it is:** US freight forwarder/broker blog post on how shippers should approach requesting quotes.
- **Fields observed:** Origin location (city/ZIP/warehouse/port address), destination location (same detail level), shipment weight, dimensions, container size, hazardous-material designation, special licensing needs, required transit timeframe, shipment ready date.
- **Notes on phrasing/layout conventions:** No sample email shown. Notes that when a company has no online quote form, "you can still always reach out to them by sending them an email with all the necessary information" — i.e., positions email as the fallback channel behind self-serve forms, consistent with rate requests skewing toward less-standardized, more free-form phrasing than carrier-side booking systems.

### Source 2.5 — Freightos, "Request For Freight Quote"
- **URL:** https://www.freightos.com/freight-resources/request-for-freight-quote/
- **Type:** Rate request / spot quote
- **What it is:** Freight marketplace/rate-benchmarking company's resource page on preparing an RFQ.
- **Fields observed:** Your contact details; supplier/origin contact details; pickup address (zip/full detail); delivery address; weight (from packing list); volume in CBM; ready/pickup date; desired delivery date; mode (air vs ocean; LCL vs FCL); official product description (from commercial invoice); HS code; shipment value; certificate of origin / MSDS / fumigation certificate (if applicable); cargo insurance needed (Y/N); Incoterm; delivery deadline constraints; budget/service priorities.
- **Notes on phrasing/layout conventions:** Recommends preparing a checklist first, then either filling an online form or, "for email submissions... copy and paste your prep list straight onto the email" and asking the recipient to confirm receipt — i.e., real RFQ emails are frequently a checklist literally pasted into email body text (uneven formatting, no polish), not a clean generated paragraph.

### Source 2.6 — Flexport Help Center quoting articles (WebSearch snippets only — pages returned HTTP 403 to WebFetch)
- **URLs:** https://support.portal.flexport.com/hc/en-us/articles/18033346613015-International-Freight-only-Quoting-Guide ; https://www.flexport.com/help/386-when-do-i-submit-quote-request/ ; https://www.flexport.com/help/382-quote-request-lcl-fcl/
- **Type:** Rate request / spot quote
- **What it is:** Flexport's own customer help-center articles on submitting quote requests; content below is from WebSearch result snippets since WebFetch was blocked (403) on all three.
- **Fields/process observed:** Freight method, shipment type, container type; origin as full address (manufacturer pickup) vs. port (if manufacturer delivers to port); destination as Flexport fulfillment / FBA / own warehouse / third-party warehouse; delivery-timeline flexibility toggle ("I'm flexible"); LCL vs FCL selection tied to shipment type; recommendation to request quotes "weeks in advance" of cargo-ready date.
- **Notes:** Digital-forwarder quoting is structured-form-first rather than email-first at Flexport — reinforces that real "rate request" correspondence in the wild ranges from unstructured shipper emails (Sources 2.1–2.5) to structured web-form submissions that only become email once a human ops rep replies. Low confidence on exact wording since not directly fetched.

---

## 3. Booking Confirmations (Ocean and Air)

### Source 3.1 — MSC (Mediterranean Shipping Company), "IFTMBC Booking Confirmation Message" implementation guide
- **URL:** https://developerportal.msc.com/content/MSC_MIG_EDIFACT_IFTMBC_Booking_Confirmation.pdf
- **Type:** Booking confirmation (ocean) — EDI/EDIFACT technical spec, not an email, but the authoritative real-carrier definition of what data a booking confirmation legally carries
- **What it is:** MSC's own 101-page EDIFACT message implementation guide (Sensitivity: Public) for the IFTMBC "Booking confirmation message" — "a message from the party providing forwarding and/or transport services to the party booking those services giving confirmation information to the booking of the consignment." Retrieved as PDF; WebFetch couldn't parse the binary directly, so I re-read the auto-saved local copy with the Read tool.
- **Fields/segments observed (exact segment names + real coded values):**
  - Segment structure: UNB (Interchange Header), UNH (Message Header), BGM (Beginning of Message), CTA (Contact Information), COM (Communication Contact), DTM (Date/Time/Period), TSR (Transport Service Requirements), FTX (Free Text), CNT (Control Total), GDS (Nature of Cargo), LOC (Place/Location Identification), RFF (Reference), TCC (Transport Charge/Rate Calculations), TDT (Details of Transport), NAD (Name and Address), GID (Goods Item Details), HAN (Handling Instructions), TMP (Temperature), RNG (Range Details), TMD (Transport Movement Details), PCD (Percentage Details), MEA (Measurements), EQN (Number of Units), DIM (Dimensions), DOC (Document/Message Details), DGS (Dangerous Goods), EQD (Equipment Details), UNT (Message Trailer), UNZ (Interchange Trailer)
  - Concrete coded example given for BGM segment: **`BGM+770+7685967039:1.2019+6+AP`** — document code **770 = "Booking confirmation"** (defined exactly as "Document/message issued by a carrier to confirm that space has been reserved for a consignment in means of transport"); "7685967039" is the example booking/document reference number (10 numeric digits, no letter prefix in this example); message function code 6 = Confirmation (vs. 1 = Cancellation); response type code values: **AJ = Pending** ("the referenced offer or transaction ... is being dealt with"), **AP = Accepted**, **CA = Conditionally accepted** ("... accepted under conditions indicated in this message")
  - DTM date-qualifier examples relevant to booking confirmations: 137 = Document/message date/time, 265 = "Container(s) VGM cut-off date," 407 = Document requested date/time, annotated specifically as "Date by which SI for the booking should be received by the carrier"
  - TSR "Contract and carriage condition" coded values: 27 = Door-to-door, 28 = Door-to-pier, 29 = Pier-to-door, 30 = Pier-to-pier
  - CTA contact-function example: CW = "Confirmed with" (person who discussed/agreed contents by phone before the message was sent) — example given: `CTA+CW+:CHARLES BROWN`
  - COM communication-channel qualifiers: EM = Electronic mail, FX = Telefax, TE = Telephone
- **Notes on phrasing/layout conventions:** This is EDI, not prose email, so field *names/codes* should inform realism (the generator's field taxonomy and status vocabulary) rather than be copied into email body text verbatim. The most useful transferable ideas: (1) real booking confirmations aren't binary confirmed/not-confirmed — carriers formally distinguish **Pending / Accepted / Conditionally Accepted**, which is a much richer and more realistic state space than "confirmed" for a pathology generator; (2) a real confirmation explicitly states **"VGM cut-off"** and **"SI due date"** as two distinct deadlines separate from the vessel cut-off, both of which the current generator's flat "Cargo ready" field misses entirely; (3) service scope is coded as one of four door/pier combinations (door-to-door, door-to-pier, pier-to-door, pier-to-pier) rather than the generator's simple ORIGIN/DESTINATION shorthand — worth cross-checking against the CW1 hblDlvMode convention already in use.

### Source 3.2 — freightcourse.com, "What Is a Booking Confirmation in Shipping?"
- **URL:** https://www.freightcourse.com/booking-confirmation/
- **Type:** Booking confirmation (ocean)
- **What it is:** Freight-training/education article defining and illustrating a booking confirmation with a worked example.
- **Fields observed (full):** Booking Reference Number ("generated by the carrier at the time of booking"), Shipper Details (name/address/contact), Consignee Details (name/address/contact), Cargo & Commodity Type, Cargo Weight, Equipment Quantity & Type (example phrasing: "3 x 40' General Purpose Container"), Requested Sailing/ETD, ETA, CY Cutoff, Vessel Name & Voyage Number, Port of Loading (POL), Port of Discharge (POD), Transshipment Port, Special Remarks.
- **Concrete example given:** a shipment from Los Angeles to Melbourne, reference **BHK51332862**, sports equipment, vessel **OOCL California**, transshipping through Shanghai.
- **Notes on phrasing/layout conventions:** The example reference format — two letters + eight digits, no hyphen (BHK51332862) — is a real-feeling alternative to the current generator's fixed "BK-#####" pattern, and pairs a plausible real ocean-carrier vessel name (OOCL California) with an explicit transshipment leg, something the flat generator never models (it has no notion of a transshipment port distinct from origin/destination).

### Source 3.3 — Freightos, "Booking Confirmation Document" (glossary, two equivalent URLs found)
- **URLs:** https://www.freightos.com/glossary/booking-confirmation/ and https://www.freightos.com/freight-resources/what-is-a-booking-confirmation/
- **Type:** Booking confirmation (ocean and air, general)
- **What it is:** Freight-marketplace company's glossary/resource definition page.
- **Fields observed:** Booking number; equipment used (size and number of pallets, in the air/general phrasing); transport plan (origin, destination, ETAs); load itinerary.
- **Notes on phrasing/layout conventions:** Frames the booking confirmation explicitly as "a receipt for the main shipment leg (ocean or air)" and notes the booking number "is often used as the main shipment tracking code" and flows carrier → forwarder → shipper (i.e., the shipper-facing confirmation is usually a forwarder's re-statement of the carrier's own confirmation, not the carrier's raw document) — a real intermediation detail the generator could reflect (forwarder confirmations sometimes reference "carrier booking no." as a field distinct from the forwarder's own file/job number).

### Source 3.4 — Freightlink (UK), booking confirmation FAQ
- **URL:** https://www.freightlink.co.uk/knowledge/faq/how-do-i-get-confirmation-my-booking
- **Type:** Booking confirmation (road/general UK freight exchange context, generalizable)
- **What it is:** UK freight-exchange platform's customer FAQ page.
- **Content observed:** "All freight booking confirmations are sent to you by email and SMS (if mobile phone number provided)." States the on-screen "thank you" page after an online booking is explicitly **not** itself the confirmation ("is not confirmation of your booking being made with the operator") — the real confirmation is the follow-up email. Advises contacting support if no email confirmation arrives within 24 hours.
- **Notes on phrasing/layout conventions:** Useful negative-space detail: real workflows have a documented gap between "we received your request" and "your booking is confirmed," i.e., an intermediate acknowledgment email genuinely exists as its own object distinct from the final confirmation — mirrors the ONE guide's distinction (Source 1.1) between "booking uploaded" and "Booking Receipt Notice."

### Source 3.5 — IAG Cargo, "eBooking guide" (air cargo)
- **URL:** https://www.iagcargo.com/en/e-booking-guide/
- **Type:** Booking confirmation / booking request (air)
- **What it is:** IAG Cargo (British Airways/Iberia cargo group) official guide to its airline e-booking platform.
- **Fields observed:** Air Waybill (AWB) number (formats given: "125-0000000" or "075-0000000" — i.e., 3-digit carrier prefix + 7-digit serial, hyphenated); origin and destination; preferred shipping date; commodity code; load type (loose or unitised cargo); weight per piece; unit type (e.g., "PMC Lower Deck" for a standard pallet); booking type (Free sale, or Allotments — BSA/CPA/Permanent Booking); product selection (named tiers: Perform, Prioritise, Constant Fresh, Constant Climate Passive); rate type (Standard or Flex); flight number and departure date; special handling flags (non-stackable, non-turnable, dangerous goods, battery classifications ELM/ELI, handling codes, dry-ice indicator); primary contact (mandatory); shipper/consignee details (mandatory only for live animals, human remains, Constant Climate).
- **Process flow:** shipment info entry → rate selection/comparison → summary review → AWB assignment → contact confirmation → final submission → **booking confirmation notification via email**.
- **Notes on phrasing/layout conventions:** Confirms the AWB-number hyphenated format (e.g., 125-0000000) explicitly as it appears on real confirmations, and shows that airline product/service tiers (e.g., "Constant Fresh," "Constant Climate Passive," "Perform," "Prioritise") are named brand products that would realistically appear as a field value on a real air booking confirmation — something a generic "Mode: Air" field completely flattens.

### Source 3.6 — Freightos, "Air Waybill (AWB): Meaning, Number, Types, and Examples"
- **URL:** https://www.freightos.com/freight-resources/air-waybill-awb/
- **Type:** Booking confirmation (air) — supporting document format
- **What it is:** Freightos glossary/resource page on AWB structure.
- **Content observed:** Full worked AWB number example: **99953729071** — decomposed as 999 (carrier/airline prefix — "999" itself denotes a neutral, non-airline-specific prefix), 5372907 (7-digit serial), 1 (check digit = the 7-digit serial number modulo 7). Also lists AWB document fields: carrier details, consignor/shipper details, consignee/receiver details, origin/destination airport codes, quantity of items, description of goods (weight/dimensions/condition), HS code, value of goods for customs, special handling instructions, payment/shipping-charge info, insurance details, contract terms, date/time/place of contract execution. Notes AWBs are issued in eight colour-coded physical copies distributed to different parties.
- **Notes:** Confirms the check-digit construction (serial mod 7) as a verifiable, realistic detail a generator could actually implement correctly (unlike a purely random AWB-looking string) — directly useful since the task background says the current generator only uses BK-##### / PO######, with no airline-prefix/check-digit logic for air shipments at all.

### Source 3.7 — DocShipper, "Booking Number: Definition & Guide" (booking-number formats — flagged low confidence)
- **URL:** https://docshipper.com/glossary/booking-number-definition-logistics/
- **Type:** Booking confirmation (ocean/air, format reference)
- **What it is:** Freight-forwarder (DocShipper) glossary page on booking-number conventions.
- **Content observed, with caveat:** WebFetch's summary returned specific carrier-prefixed examples — "MAEU123456789" (Maersk), "CMDU987654321" (CMA CGM), "MSCU2024987654" (MSC) — described as booking-number formats. **These look suspect**: 4-letter-prefix + 7-digit patterns like "MAEU1234567" are the well-known ISO 6346 **container** number format (4 letters, last one always U for freight containers, 7 digits with a check digit), not typically how ocean carriers format *booking* numbers, and "MSCU2024987654" has 11 digits after the prefix, which doesn't match the standard either. This may be the fetch tool's own generated illustration rather than text actually on the page. Also states booking confirmation "typically occurs within 15 minutes to 48 hours" and that the booking number recurs across commercial invoice, packing list, VGM declaration, SLI, and customs pre-clearance filings. Given the uncertainty on the digit patterns specifically, **do not use the three quoted example strings as ground truth for a generator's format logic** — cross-check against a primary carrier source before encoding a format rule from this.

### Source 3.8 — mailing-list/general web evidence on booking confirmation delivery footers and greetings (pattern-level, not single-page)
- **Type:** Cross-cutting structural notes gathered from multiple booking-confirmation-adjacent pages above (freightlink.co.uk, freightcourse.com, Freightos), plus a general confidentiality-notice search
- **Notes:** A generic but real confidentiality-footer pattern recurs across business-email disclaimer references: *"This email and any attachments are intended only for the use of the individual or entity to which they are addressed and may contain confidential information."* No source specifically confirmed this exact wording on a named freight forwarder's own confirmation email (general disclaimer-template sites only), so treat as a plausible generic register to sample from, not a verified freight-industry-specific quote. This is the closest evidence found for the task's flagged gap ("no legal disclaimers/confidentiality footers") — genuinely thin evidence, worth flagging as an area where I could not find a real freight-forwarder-specific example despite several search attempts.

---

## Summary of what the current generator is missing, cross-referenced to sources above

- **Multiple, distinct reference numbers per booking** (shipper ref, forwarder ref, invoice ref, SI-stage refs) instead of one "Our reference" — Source 1.1
- **Country/lane-conditional fields** (AES ITN, CERS, Mexico TAX IDs, MOT No.) rather than a fixed field list — Source 1.1
- **Non-binary confirmation status** (Pending / Accepted / Conditionally Accepted) instead of just "confirmed" — Source 3.1
- **Distinct deadlines** — VGM cut-off, SI-due date, port cut-off, inland cut-off — all separate from a single "cargo ready" date — Sources 1.1, 3.1, 3.2
- **Realistic reference-number formats**: two-letter+8-digit booking refs (BHK51332862), 3-digit-prefix+7-digit+check-digit AWB numbers (999-5372907-1), MSC's plain 10-digit booking/document numbers — Sources 3.2, 3.6, 3.1 (contrast against Source 3.7's low-confidence figures)
- **Transshipment legs** and named real vessels — Source 3.2
- **Named airline product tiers / service levels** on air confirmations, not just "Mode: Air" — Source 3.5
- **Varied greeting register**, including formal/ESL-influenced "Dear Sir/Madam," "Respected Sir/Madam," vs. casual "Dear Freight Team," — Sources 2.2, 2.3
- **Varied subject-line conventions** ("RFQ - ..." prefix with compressed shipment parameters) — Source 2.2
- **Real header block shown** (To/Cc/Bcc/From/Subject) as part of a "sample email" — Source 2.3
- **Thread density**: a real booking can span 10-20+ emails, i.e., amendments/re-confirmations are normal, not a single clean message — Source 1.2
- **Uneven/incomplete real requests** — genuinely underspecified one-line rate requests are realistic, not just fully-populated ones — Source 2.1
- **Checklist-pasted-into-email-body texture** rather than polished prose — Source 2.5
- **Intermediate acknowledgment vs. final confirmation** as two separate emails — Sources 1.1, 3.4
- **Gap not filled by this research**: no verified freight-industry-specific confidentiality/disclaimer footer text, and zero Reddit/LinkedIn real-world quoted-email examples (both blocked/unavailable to these tools) — flagged as an open gap, not fabricated.
