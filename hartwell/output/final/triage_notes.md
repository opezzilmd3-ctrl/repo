# Triage notes – Hartwell & Osei LLP mailbox (first filing pass)

Inputs confirmed before triage: `sha256sum -c MANIFEST.sha256` gave 72/72 OK. The folder matches the manifest and INPUTS.md (71 inputs + INPUTS.md + MANIFEST). All 64 .eml files parse with no MIME defects. All 24 PDF attachments open in pdfinfo; 15 have no text layer (image-only scans).

Method: the emails are read in Date order, in batches of 8. Every header and body was read in full. Text-layer PDFs were read with pdftotext. Each scanned page was rendered alone with pdftoppm at 110 dpi and viewed as a single image (no montages). The rules applied are filing_rules.md §1–8. Matter data comes from matters.csv.

Standing interpretations (applied throughout):
- **Privilege log scope.** privilege_log.csv lists every email filed in 1001-001 with AC or WP privilege. The parenthetical "(under litigation hold)" describes the matter; it does not limit the dates. So pre-hold privileged items are logged too. Hold start is 2026-08-10.
- **Hold flag.** The `hold` flag is set only when the email date is on or after 2026-08-10 (§5).
- **Privilege for forwards.** Privilege follows who takes part in the email itself (§7).

## Batch 1 (emails 1–8, 2026-08-03 → 2026-08-05)

### 1. AAMkdd73cf256d.eml
- From: Dana Whitcomb <dwhitcomb@brightwaterfoods.test> · To: Mira Osei · Cc: – · Date: Mon, 03 Aug 2026 09:12 -0400 · Message-ID: <179101024147.431.7208689589448930797@mail.test>
- Body: the client sends the March–May delivery logs Mira asked for, with Kestrel short shipments highlighted, and offers the invoices too.
- Attachment: delivery_logs_mar-may.pdf (text layer). "Brightwater Foods Inc. – Inbound delivery log; Supplier: Kestrel Packaging Ltd; Mar–May 2026; short shipments flagged: 14 of 61 deliveries."
- Decision: **matter 1001-001** (Kestrel Supply Dispute). The client domain is brightwaterfoods.test, the subject is Kestrel supply evidence and it goes to the responsible attorney. Privilege **AC** (client ↔ firm). Dated 08-03, before the 08-10 hold start, so **no hold flag**. It still goes on the privilege log (see the standing interpretation).

### 2. AAMkdb8f4d3e27.eml
- From: Leah Park (firm) · To: Dana Whitcomb (Brightwater) · Date: Mon, 03 Aug 2026 14:40 -0400 · Message-ID: <179101024148.431.5595503585959105414@mail.test>
- Body: USPTO examiner issued an office action on the SunHarvest application citing a prior registration; options to follow by Friday.
- Attachments: none.
- Decision: **matter 1001-002** (SunHarvest Trademark; Leah Park is the responsible attorney). Privilege **AC**. No flags.

### 3. AAMkc7ec99108d.eml
- From: Greg Tolland <gtolland@tolland-law.test> (Tolland Law, counsel for Kestrel) · To: Mira Osei · Date: Tue, 04 Aug 2026 10:05 -0400 · Message-ID: <179101024149.431.1713291243171398086@mail.test>
- Body: opposing counsel sends a proposed stipulated protective order and wants edits by the 7th.
- Attachment: proposed_protective_order.pdf (text layer). "United States District Court – Brightwater Foods Inc. v. Kestrel Packaging Ltd – [Proposed] Stipulated Protective Order."
- Decision: **matter 1001-001**. Privilege **none** (opposing counsel takes part). Dated before the hold start, so no flags.

### 4. AAMk737734d7c1.eml
- From: Maria Delgado <mdelgado.home@mailbox.test> · To: Ravi Iyer · Date: Tue, 04 Aug 2026 11:30 -0400 · Message-ID: <179101024149.431.7654711019877552585@mail.test>
- Body: "Dad's house". The appraiser visited yesterday and his scanned report is attached.
- Attachment: scan_0812.pdf, an image-only scan **viewed as an image**. The page is landscape and the text runs rotated 90°. It reads: "APPRAISAL REPORT – Property: 88 Alder Street – Prepared for: Estate of Ricardo Delgado – Purpose: date-of-death valuation – Opinion of value: $412,000".
- Decision: **matter 1002-001** (Estate of Ricardo Delgado). matters.csv lists the estate property as 88 Alder Street. The body alone ("Dad's house") could also suggest 1002-002 (Purchase 14 Fenwick Lane, closed). The scan settles it as the estate. Privilege **AC**. No flags (the matter is open).

### 5. AAMkda8201e2bd.eml
- From: Ravi Iyer · To: Paul Ostrander <paul.ostrander@mailbox.test> · Date: Tue, 04 Aug 2026 16:20 -0400 · Message-ID: <179101024192.431.10755287519557781898@mail.test>
- Body: reminder that the financial disclosure is due to the court by Aug 28, with a request for three bank statements.
- Attachments: none.
- Decision: **matter 1005-001** (Ostrander Divorce). Privilege **AC**. No flags.
- *Corrected after batch 5 (email 38):* a non-delivery report dated 2026-08-20 shows this subject "Financial disclosure deadline" failed to reach paul.ostrander@mailbox.test. Filing is unchanged. Ravi must confirm by another channel that Paul received the Aug 28 disclosure deadline.

### 6. AAMk30965eda32.eml
- From: Hank Moreau <hmoreau@northpointlogistics.test> · To: Jonah Hartwell · Date: Wed, 05 Aug 2026 08:55 -0400 · Message-ID: <179101024192.431.8186450037367379820@mail.test>
- Body: the landlord's counter-proposal is attached; they want a 4% annual escalator.
- Attachment: landlord_letter.pdf, an image-only scan **viewed as an image**. The page is upside down (180°). It reads: "HARBORVIEW PROPERTIES – Re: Dock 7 – lease renewal – Counter-proposal: 5-year term, 4% annual escalator – Tenant: Northpoint Logistics LLC".
- Decision: **matter 1003-002** (Dock 7 Lease Renewal; Jonah is the responsible attorney). Privilege **AC** (client ↔ firm; the landlord letter is only an attachment). No flags. This is Northpoint's lease matter, not the Tran claim, so the wall does not apply.

### 7. AAMkcd2f45e678.eml
- From: **Anika Brandt** (firm associate) · To: Mira Osei · Cc: Tom Weller · Date: Wed, 05 Aug 2026 09:40 -0400 · Message-ID: <179101024203.431.8433474836880937074@mail.test>
- Body: Anika offers to help with the Tran deposition outline. She says she worked on Ms. Tran's side at her old firm and knows their theory.
- Attachments: none.
- Decision: **matter 1003-001** (Tran Employment Claim). Privilege **WP** (internal only). **ETHICAL WALL.** matters.csv says Anika Brandt has been screened from 1003-001 since 2026-07-01. She *sent* an email about that matter on 08-05. Flag `ethical-wall`, and one wall incident (Anika Brandt, role sender, 1003-001). Her statement confirms the reason for the screen (prior work for the adverse party). Jonah Hartwell (ethics partner) must be told. Mira must not accept her help or reply to her on this matter. Tom Weller, who is not screened, was copied. This is not a `potential-conflict` under §5: no client is adverse to another current client here, and no adverse party is asking to hire the firm. Anika's prior work is what the existing wall already covers.

### 8. AAMk79830c71c2.eml
- From: LegalCLE Events <webinar@legalcle-events.test> · To: Front Desk info@ · Date: Wed, 05 Aug 2026 13:15 -0400 · Message-ID: <179101024203.431.13510552400517953194@mail.test>
- Body: marketing push to register for an ethics CLE webinar.
- Attachments: none.
- Decision: **non_matter** (unsolicited marketing). Privilege n/a.

## Batch 2 (emails 9–16, 2026-08-05 → 2026-08-07)

### 9. AAMk9da13ffe79.eml
- From: Elena Varga <evarga@callowaymed.test> · To: Leah Park · Date: Wed, 05 Aug 2026 15:02 -0400 · Message-ID: <179101024203.431.11778248285446685871@mail.test>
- Body: the client sends its IT vendor's timeline of the July access incident and asks to keep circulation tight.
- Attachment: incident_timeline_draft.pdf (text layer). "Calloway Medical Group PC – Access incident timeline (DRAFT) – Jul 14 unusual login detected – Jul 15 account disabled."
- Decision: **matter 1004-001** (Privacy Investigation; Leah Park). The matter is **RESTRICTED**, so the email goes under `box/Restricted/…` with flag `restricted`. Privilege **AC**. Judgment call: Elena Varga is the Calloway contact on both 1004 matters. This email is about the data-access incident, not Heron.

### 10. AAMk2fcb008853.eml
- From: Elena Varga (Calloway) · To: Jonah Hartwell · Date: Thu, 06 Aug 2026 09:10 -0400 · Message-ID: <179101024204.431.17076831110516396069@mail.test>
- Body: "Heron – diligence responses". Riverside's response to the diligence request list is attached.
- Attachment: diligence_responses.pdf (text layer). "Riverside Imaging LLC – Responses to Due Diligence Request List – Prepared for Calloway Medical Group PC."
- Decision: **matter 1004-002** (Project Heron Acquisition = acquisition of Riverside Imaging; Jonah). Privilege **AC**. **Name overlap:** "Heron" is also in Blue Heron Marina (1007). The Calloway sender and the Riverside Imaging attachment decide it for Project Heron. Not restricted (only 1004-001 is).

### 11. AAMk7218187993.eml
- From: Sam Pryce <sam@blueheronmarina.test> · To: Jonah Hartwell · Date: Thu, 06 Aug 2026 10:45 -0400 · Message-ID: <179101024204.431.10475402619713769054@mail.test>
- Body: "Heron slip agreement – signature page". The signed page is attached.
- Attachment: sigpage.pdf, an image-only scan **viewed as an image**, upright. It reads: "BLUE HERON MARINA LLC – Slip C Lease Agreement – signature page – Signed: S. Pryce, Manager".
- Decision: **matter 1007-001** (Blue Heron Marina, Slip C Lease; Jonah). Privilege **AC**. **Name overlap:** "Heron" here is the marina, not Project Heron (Calloway). Both the sender domain and the scan confirm it. Jonah is the responsible attorney on both "Heron" matters, so the recipient does not help tell them apart.

### 12. AAMk244dabb481.eml
- From: Kenji Sato <ksato@satoarch.test> · To: Mira Osei · Date: Thu, 06 Aug 2026 12:00 -0400 · Message-ID: <179101024212.431.10390633232226026914@mail.test>
- Body: Rivera & Sons are billing for roof work at 210 Mill Street that was never completed. How should the client respond?
- Attachments: none.
- Decision: **matter 1008-001** (Rivera Roofing Dispute, 210 Mill Street; Mira). Privilege **AC**.

### 13. AAMk8917362f25.eml
- From: Fenwick Lane HOA Board <board@fenwicklanehoa.test> · To: Leah Park · Date: Thu, 06 Aug 2026 17:30 -0400 · Message-ID: <179101024212.431.4625812910636666749@mail.test>
- Body: the Unit 22 owner is four months behind on dues; the ledger is attached.
- Attachment: ledger.pdf, an image-only scan **viewed as an image**, upright (slight skew). It reads: "FENWICK LANE HOMEOWNERS ASSOCIATION – Owner ledger – Unit 22 (owner: K. Albright) – Balance due: $1,860.00".
- Decision: **matter 1006-001** (Assessment Collections; Leah). Privilege **AC**. **Name overlap:** "Fenwick" is also in Delgado's 1002-002 (14 Fenwick Lane). The debtor here is K. Albright, not a firm client, so there is no conflict.

### 14. AAMke3cf44dd3f.eml
- From: Maria Delgado <mdelgado.home@mailbox.test> · To: Ravi Iyer · Date: Fri, 07 Aug 2026 08:20 -0400 · Message-ID: <179101024222.431.6055211168486285328@mail.test>
- Body: Maria got a letter from the Fenwick Lane HOA saying she owes a transfer fee from the June purchase, and asks whether that is right. The letter is attached.
- Attachment: hoa_letter.pdf, an image-only scan **viewed as an image**, upright (slight skew). It reads: "FENWICK LANE HOMEOWNERS ASSOCIATION – To: Maria Delgado, 14 Fenwick Lane – Transfer fee due on June 2026 conveyance: $750.00".
- Decision: **matter 1002-002** (Purchase 14 Fenwick Lane; Ravi). The fee arises from that purchase. The matter **closed 2026-06-30** and this email is 08-07, so flag `post-closing`. **Potential conflict:** the Fenwick Lane HOA is a current client (1006-001, open, Leah Park). It is asserting a $750 claim against Maria Delgado, who is also a current client (1002-001 is open). Advising Maria on whether she owes the HOA is adverse to the HOA, so flag `potential-conflict`. Flags in §5 order: `post-closing;potential-conflict`. Privilege **AC**. No stub goes in the HOA's folders (§2: never cross clients). Action: Ravi (post-closing request plus conflict) and Leah Park (HOA's attorney). Conflict clearance goes to the ethics partner.
- *Updated after batch 6 (email 42):* on 08-21 the HOA Board asked Leah to send a demand letter to Maria Delgado over this same fee. That confirms the adversity: the firm is being asked to act against one current client for another. The flags are unchanged. The conflict is now live on both sides.

### 15. AAMk980ab8ab67.eml
- From: Greg Tolland (Tolland Law, Kestrel's counsel) · To: Mira Osei · Date: Fri, 07 Aug 2026 11:00 -0400 · Message-ID: <179101024231.431.3195436931889555367@mail.test>
- Body: "RE: … proposed protective order". Kestrel accepts our edits to paragraphs 4 and 9; a clean version will follow.
- Attachments: none.
- Decision: **matter 1001-001**. Privilege **none** (opposing counsel). Dated 08-07, before the hold start, so no hold flag. This reply follows email 3 (same thread).

### 16. AAMka2b1852f27.eml
- From/To/Date/Subject/body identical to email 15 · Message-ID: <179101024231.431.3195436931889555367@mail.test>, the **same Message-ID as email 15**.
- Decision: **duplicate**. The two have the same Date to the second. I treat AAMk980ab8ab67 as the original: it comes first in Date order, and the tie is broken by mailbox file name, a mechanical rule. Its content is identical, so the choice makes no substantive difference. The original sits in 1001-001, which is under hold. But this duplicate is dated **08-07, before the 2026-08-10 hold start**, so the §6 exception does **not** apply. It goes to `box/_Duplicates/`. Privilege n/a.
- Back-reference: email 15's entry is unchanged; it stays the primary copy.

## Batch 3 (emails 17–24, 2026-08-10 → 2026-08-12)

### 17. AAMk65fb710734.eml
- From: Mira Osei · To: Dana Whitcomb (Brightwater) · Cc: Tom Weller · Date: Mon, 10 Aug 2026 09:00 -0400 · Message-ID: <179101024232.431.6629853116782086111@mail.test>
- Body: Mira sends the litigation hold notice: from today nothing related to Kestrel may be deleted.
- Attachment: litigation_hold_notice.pdf (text layer). "LITIGATION HOLD NOTICE – Matter: Brightwater v. Kestrel Packaging – Effective: 2026-08-10."
- Decision: **matter 1001-001**. Dated 08-10, the hold start day ("on or after"), so flag `hold`. Privilege **AC** (firm + client; Tom is staff). Goes on the privilege log. The notice confirms the hold date in matters.csv.

### 18. AAMk73f6fa5db8.eml
- From: Dana Whitcomb (Brightwater) · To: Mira Osei, Leah Park · Date: Mon, 10 Aug 2026 14:30 -0400 · Message-ID: <179101024232.431.18401162672358962926@mail.test>
- Body: "Two things". (1) To Mira: more Kestrel emails from April were found and will be uploaded tonight. (2) To Leah: the SunHarvest packaging launch moved to November. Does that affect trademark timing?
- Attachments: none.
- Decision: **two matters, same client** (Brightwater, 1001). Kestrel is addressed first, so the **primary is 1001-001**, with a **cross-reference stub in 1001-002** (SunHarvest) Correspondence (§2). Both parts are substantive (an evidence update and a legal question). Dated 08-10, so flag `hold`. Privilege **AC**. Privilege log: yes.

### 19. AAMkbda7677796.eml
- From: Tom Weller (paralegal) · To: Mira Osei · Date: Tue, 11 Aug 2026 10:10 -0400 · Message-ID: <179101024232.431.4728479494511230323@mail.test>
- Body: proposed Bates ranges for the first Kestrel production (BWF000001–BWF002400); draft privilege calls are flagged in the review sheet.
- Attachments: none.
- Decision: **matter 1001-001**, flag `hold`, privilege **WP** (internal only). Privilege log: yes.

### 20. AAMka69d95847e.eml
- From: Nina Cole <ncole@colelaborlaw.test> (Cole Labor Law, counsel for Jessica Tran) · To: Mira Osei · **Cc: Anika Brandt** · Date: Tue, 11 Aug 2026 13:45 -0400 · Message-ID: <179101024232.431.14556695436794007147@mail.test>
- Body: Ms. Tran is available for mediation on Sept 15 or 22; please confirm.
- Attachments: none.
- Decision: **matter 1003-001** (Tran). Privilege **none** (opposing counsel). **ETHICAL WALL:** Anika Brandt (screened since 2026-07-01) was **copied** on 08-11. Flag `ethical-wall`, and a wall incident (Anika Brandt, cc, 1003-001). Opposing counsel copying Anika suggests they know of her prior involvement. Jonah (ethics partner) must be told, and Mira should not reply-all to Anika.

### 21. AAMk9f28518867.eml
- From: Hank Moreau (Northpoint) · To: Mira Osei · Date: Tue, 11 Aug 2026 16:00 -0400 · Message-ID: <179101024232.431.9292703932913623197@mail.test>
- Body: "Tran – personnel file". The excerpt Mira asked for is attached.
- Attachment: personnel_excerpt.pdf, an image-only scan **viewed as an image**, upright. It reads: "NORTHPOINT LOGISTICS LLC – PERSONNEL FILE – Employee: Jessica Tran – Performance reviews 2024–2026 (excerpt)".
- Decision: **matter 1003-001** (Tran). Privilege **AC**. No screened person takes part, so there is no wall flag. Judgment call: Hank Moreau is Northpoint's contact on both 1003 matters. The scan (Tran personnel file) puts this one in the employment claim, not Dock 7.

### 22. AAMkd403d71684.eml
- From: Rivera & Sons Accounts <accounts@rivera-sons-roofing.test> · To: Front Desk info@ · Date: Wed, 12 Aug 2026 09:30 -0400 · Message-ID: <179101024244.431.7224610814304506253@mail.test>
- Body: "To counsel": as instructed by our client Sato Architecture, Rivera sends invoice copies. Invoice 4471 (roofing, 210 Mill Street) is 60 days overdue.
- Attachments: none.
- Decision: **matter 1008-001** (Rivera Roofing Dispute; Mira). The counterparty in the dispute writes to the firm as Sato's counsel. It is correctly addressed, so not misdirected. Privilege **none** (third party/adverse). Mira should note the overdue-invoice position.

### 23. AAMk108743feb6.eml
- From: noreply@boxsync.test · To: Front Desk info@ · Date: Wed, 12 Aug 2026 12:20 -0400 · Message-ID: <179101024245.431.14371766634565979647@mail.test>
- Body: "Your organization's storage is 91% full. Contact your administrator."
- Attachments: none.
- Decision: **firm_admin** (firm storage/IT notice). Not phishing: there is no link, no credential request and no impersonation of the firm. It is passed to IT/office manager as an IT item (storage is relevant to the Box migration).

### 24. AAMk090f3ebdd3.eml
- From: Paul Ostrander <paul.ostrander@mailbox.test> · To: Ravi Iyer · Date: Wed, 12 Aug 2026 15:40 -0400 · Message-ID: <179101024245.431.13610295619821862519@mail.test>
- Body: the kids' holiday schedule looks fine (divorce). Separately, his brother wants help with a slip contract at Blue Heron Marina and asks if he can call Ravi.
- Attachments: none.
- Decision: **matter 1005-001** (Ostrander Divorce). The email mainly concerns the existing matter and also asks for services on something new, so flag `new-matter-request` (§2). **Potential conflict:** Blue Heron Marina LLC is a current client (1007-001, Slip C lease, Jonah). The brother would be the marina's counterparty in a slip contract, so acting for him is adverse to a current client. Flag `potential-conflict`. Flags in §5 order: `potential-conflict;new-matter-request`. Privilege **AC**. No stub in 1007 (different client, §2). **Name overlap:** "Blue Heron" here is the marina, not Project Heron. Action: Ravi (intake/conflict check before any call), Jonah (marina's attorney), ethics partner for clearance.

## Batch 4 (emails 25–32, 2026-08-13 → 2026-08-17)

### 25. AAMke130b17d0b.eml
- From: Leah Park · To: Elena Varga (Calloway) · Date: Thu, 13 Aug 2026 08:45 -0400 · Message-ID: <179101024245.431.14579555550856765585@mail.test>
- Body: draft v2 of the regulator notification letter for review, marked privileged and confidential.
- Attachments: none.
- Decision: **matter 1004-001** (Privacy Investigation). A regulator notification arises from the access incident. **RESTRICTED**, so it is filed under `box/Restricted/` with flag `restricted`. Privilege **AC**.

### 26. AAMk993deffa38.eml
- From: "IT Support" <it-support@**hartwe11-osei.test**> · To: Mira Osei, Leah Park, Ravi Iyer · Date: Thu, 13 Aug 2026 10:00 -0400 · Message-ID: <179101024245.431.6239472754380089849@mail.test>
- Body: "Your mailbox password expires today. Verify your account at the link below…"
- Attachments: none.
- Decision: **non_matter**, flag `phishing`. The sender domain is a look-alike of the firm's (digits "11" in place of "ll" in hartwell), it impersonates firm IT, and it asks staff to verify credentials. Privilege n/a. Action: IT (block domain, check whether anyone clicked) and the three recipients (do not click; report).

### 27. AAMkc707b37e14.eml
- From: Robert Baines, CEO <rbaines@kestrelpack.test> (Kestrel Packaging) · To: Jonah Hartwell · Date: Thu, 13 Aug 2026 14:15 -0400 · Message-ID: <179101024245.431.10668196910374413000@mail.test>
- Body: Kestrel Packaging wants to engage the firm for a new distribution agreement and asks for a call.
- Attachments: none.
- Decision: **needs_review**, flags `potential-conflict;new-matter-request`. Kestrel Packaging Ltd is the **adverse party** in Brightwater v. Kestrel (1001-001, under hold). An adverse party asking to hire the firm is a conflict-check item (§1, §5), and it asks for new services. It is not filed in any Brightwater folder and gets no stub there (§2). Privilege n/a. Decision owner: Jonah Hartwell as ethics partner (conflict clearance; he is also the recipient), with Mira Osei (responsible for 1001-001) informed. Jonah should not schedule the call until conflicts are cleared.

### 28. AAMk5376c468ae.eml
- From: Dana Whitcomb (Brightwater) · To: Jonah Hartwell · Date: Fri, 14 Aug 2026 09:05 -0400 · Message-ID: <179101024245.431.7245120410654812910@mail.test>
- Body: the Q2 board minutes are attached for the minute book.
- Attachment: q2_minutes.pdf (text layer). "BRIGHTWATER FOODS INC. – Minutes of the Board of Directors – Q2 2026."
- Decision: **matter 1001-003** (General Corporate; Jonah). Privilege **AC**. This is not the Kestrel matter, so the hold does not apply even though the client is the same.

### 29. AAMk32d7a94ded.eml
- From: Greg Tolland (Kestrel's counsel) · To: Mira Osei · Date: Fri, 14 Aug 2026 11:25 -0400 · Message-ID: <179101024246.431.16904624335560488330@mail.test>
- Body: Kestrel intends to depose Dana Whitcomb in late September and asks for dates.
- Attachments: none.
- Decision: **matter 1001-001**, flag `hold` (08-14). Privilege **none**.

### 30. AAMk9770c6a5b8.eml
- Identical to email 29: same From/To/Date/Subject/body and the **same Message-ID** <179101024246.431.16904624335560488330@mail.test>.
- Decision: category **duplicate**. Tie on Date is broken by mailbox file name, so AAMk32d7a94ded is the original. The original is filed in 1001-001 (under hold), and this copy is dated 08-14, on or after the 08-10 hold start. The **§6 exception applies**: it is kept in the matter's Correspondence with `_dup` before `.eml`, flags `hold;duplicate-retained`, primary_matter 1001-001. Privilege: I record the original's value **none** (opposing counsel), not n/a, because the copy is filed in a matter folder under hold and must be reviewable like the original. It is not privileged either way, so the privilege log is unaffected.
- Back-reference: email 29 stays the primary original.

### 31. AAMk3b84e55160.eml
- From: Elena Varga (Calloway) · To: Leah Park, Jonah Hartwell · Date: Mon, 17 Aug 2026 10:40 -0400 · Message-ID: <179101024246.431.8366011476272693042@mail.test>
- Body: "Board update". (1) To Leah: the notification letter went out Friday (privacy matter). (2) To Jonah: the Heron board vote is set for Sept 2 (acquisition).
- Attachments: none.
- Decision: **two matters, same client** (Calloway, 1004). The notification letter is addressed first, so the **primary is 1004-001**, RESTRICTED, under `box/Restricted/…`, flag `restricted`. A **stub goes in 1004-002** (Project Heron) Correspondence; it holds only the "Filed at:" path, no content. Privilege **AC**. Judgment calls: (a) "Heron" here is Project Heron (Calloway sender, board vote on the acquisition), not the marina. (b) The stub in a non-restricted matter points into Restricted. §2/§3 require it because both matters are the same client, and the email copy itself stays only under Restricted.

### 32. AAMk4ba3ea284d.eml
- From: Lucy Carter <lcarter@carter-whitfield.test> (Carter Whitfield LLP) · To: Mira Osei · Date: Mon, 17 Aug 2026 15:00 -0400 · Message-ID: <179101024246.431.15814092934953722453@mail.test>
- Body (read only far enough to identify it): it refers to closing documents for "the Martinez closing next week, per our call". There is no Martinez client or matter in matters.csv. The email says documents are attached but the message has **no attachment**.
- Decision: **needs_review**, flag `misdirected`. It is clearly meant for another firm or person; it was not read further (§1). Privilege n/a. Action: Mira tells the sender it was misdirected and does not use the content.

## Batch 5 (emails 33–40, 2026-08-18 → 2026-08-20)

### 33. AAMk017ff12229.eml
- From: Mira Osei · To: Tom Weller · Date: Tue, 18 Aug 2026 09:30 -0400 · Message-ID: <179101024246.431.15009454818362858616@mail.test>
- Body: "Sato – draft demand letter". Prepare a first draft of the demand letter to Rivera & Sons; the position is no payment for work not performed.
- Attachments: none.
- Decision: **matter 1008-001** (Rivera Roofing Dispute). Privilege **WP** (internal).

### 34. AAMk15a9964aef.eml
- From: Sam Pryce (Blue Heron Marina) · To: Jonah Hartwell · Date: Tue, 18 Aug 2026 12:00 -0400 · Message-ID: <179101024246.431.2987419846011419478@mail.test>
- Body: the insurance certificate is attached as requested.
- Attachment: coi.pdf, an image-only scan **viewed as an image**. The page is landscape and the text runs rotated 90°. It reads: "CERTIFICATE OF LIABILITY INSURANCE – Certificate holder: Blue Heron Marina LLC – Re: Slip C lease".
- Decision: **matter 1007-001** (Slip C Lease). Privilege **AC**. "Heron" is the marina; the sender and the scan both say so.

### 35. AAMka775139237.eml
- From: Hank Moreau (Northpoint) · To: Jonah Hartwell · **Cc: Anika Brandt** · Date: Tue, 18 Aug 2026 16:45 -0400 · Message-ID: <179101024256.431.6594584699842797984@mail.test>
- Body: (1) the landlord accepted our counter on Dock 7. (2) Separately, Ms. Tran's lawyer called Hank directly **again**. Is that allowed?
- Attachments: none.
- Decision: **two matters, same client** (Northpoint, 1003). Dock 7 is addressed first, so the **primary is 1003-002** with a **stub in 1003-001** (Tran). The Tran part is a substantive question (opposing counsel contacting a represented party). Privilege **AC**. **ETHICAL WALL:** Anika Brandt (screened from 1003-001 since 07-01) was **copied** on an email about 1003-001 (the cross-referenced matter). §5 covers "primary or cross-referenced", so flag `ethical-wall` and a wall incident (Anika Brandt, cc, 1003-001). Actions: Jonah (Dock 7 acceptance), Mira (responsible for Tran) to advise Hank and raise the direct contact with Cole Labor Law, and the ethics partner on the wall incident. Anika was copied by the client, so Northpoint should be asked to leave her off Tran topics.

### 36. AAMk684735af1c.eml
- From: Maria Delgado · To: Ravi Iyer · Date: Wed, 19 Aug 2026 10:00 -0400 · Message-ID: <179101024256.431.9085454592554248722@mail.test>
- Body: the court set the estate inventory hearing for October 6.
- Attachments: none.
- Decision: **matter 1002-001** (Estate of Ricardo Delgado). Privilege **AC**.

### 37. AAMk8dff666589.eml
- From: Maria Delgado · To: Ravi Iyer · Date: Wed, 19 Aug 2026 13:30 -0400 · Message-ID: <179101024256.431.3243291915451065141@mail.test>
- Body: "Unrelated to Dad's estate": her daughter is starting a bakery and wants to form an LLC. Can Ravi help?
- Attachments: none.
- Decision: **needs_review**, flag `new-matter-request`. The email is only a request for new services for a new person (the daughter), and it says it is unrelated to the existing matter, so it is not filed in 1002-001 (§1). There is no adversity to any current client, so no conflict flag. Privilege n/a. Decision owner: Ravi Iyer (intake and conflict check for the daughter; engagement decision).
- *Updated after batch 8 (email 63):* on 09-21 Maria follows up with a proposed name, "Delgado Bakery LLC". It is the same pending new-matter request. The category is unchanged.

### 38. AAMkeefee5a5b2.eml
- From: Mail Delivery Subsystem <mailer-daemon@mx.hartwell-osei.test> · To: Ravi Iyer · Date: Thu, 20 Aug 2026 08:10 -0400 · Message-ID: <179101024256.431.15733610626560736354@mail.test>
- Body: delivery failed to paul.ostrander@mailbox.test. Original subject: "Financial disclosure deadline".
- Attachments: none.
- Decision: **bounce**, flag `delivery-failure`. Under §5 it is filed in the matter of the original email. The original subject matches email 5 (Ravi → Paul Ostrander, 08-04), so it goes to **1005-001**. Privilege **none** (automated sender). **Back-reference:** email 5's entry is now annotated. Observation: Paul wrote to Ravi from this same address on 08-12, so the failure may be temporary. Either way the court deadline of Aug 28 makes it urgent for Ravi to confirm receipt. IT should check the mail route.

### 39. AAMk15d7185dda.eml
- From: Dana Whitcomb (Brightwater) · To: Mira Osei · Date: Thu, 20 Aug 2026 11:45 -0400 · Message-ID: <179101024256.431.17012990539435476124@mail.test>
- Body: the April Kestrel emails are attached as one PDF. This follows up the promise in email 18.
- Attachment: april_emails.pdf (text layer). "Export: Brightwater purchasing mailbox – Correspondence with Kestrel Packaging Ltd, April 2026."
- Decision: **matter 1001-001**, flag `hold`. Privilege **AC**. Privilege log: yes. The attachment is evidence under hold and is extracted to Documents/.
- *Updated after batch 8 (email 64):* on 09-25 the client asks to purge the April purchasing mailbox. That is the source of this April Kestrel export, so the hold forbids the purge. Email 64 carries the attorney-action flag. This entry is unchanged.

### 40. AAMk41b53302fc.eml
- From: Leah Park · To: Dana Whitcomb · Date: Thu, 20 Aug 2026 15:20 -0400 · Message-ID: <179101024256.431.17876049419447495860@mail.test>
- Body: the response to the SunHarvest office action was filed today (follows emails 2 and 18).
- Attachments: none.
- Decision: **matter 1001-002**. Privilege **AC**.

## Batch 6 (emails 41–48, 2026-08-21 → 2026-08-25)

### 41. AAMkc250b601fc.eml
- From: Joan Kline <jkline@klinefamilylaw.test> (Kline Family Law; opposing counsel) · To: Ravi Iyer · Date: Fri, 21 Aug 2026 09:00 -0400 · Message-ID: <179101024256.431.13961663413545217704@mail.test>
- Body: "Counsel, attached is our proposed parenting plan."
- Attachment: parenting_plan.pdf, an image-only scan **viewed as an image**, upright. It reads: "PROPOSED PARENTING PLAN – In re the Marriage of Ostrander – Submitted by Respondent".
- Decision: **matter 1005-001** (Ostrander Divorce). The email alone does not name the matter; the scan identifies it. Privilege **none** (opposing counsel).

### 42. AAMk833acb6266.eml
- From: Fenwick Lane HOA Board · To: Leah Park · Date: Fri, 21 Aug 2026 14:00 -0400 · Message-ID: <179101024265.431.2638742175316285014@mail.test>
- Body: the new owner at 14 Fenwick Lane, **Maria Delgado**, disputes the transfer fee. Can we send a demand letter?
- Attachments: none.
- Decision: **matter 1006-001** (Assessment Collections: the HOA's collection work for amounts owed by owners; Leah). Flag `potential-conflict`: the HOA asks the firm to send a demand to **Maria Delgado, a current client** (1002-001 open; she is asking Ravi about this fee in email 14). Privilege **AC**. No stub or reference in any Delgado folder (§2). Action: Leah must not send the demand until the ethics partner clears the conflict; Ravi to be told. **Name overlap:** Fenwick Lane HOA (1006) and 14 Fenwick Lane purchase (1002-002) are different clients. Here they really are adverse.

### 43. AAMk0749fe85b0.eml
- From: Kenji Sato (Sato Architecture) · To: Mira Osei · Date: Mon, 24 Aug 2026 10:30 -0400 · Message-ID: <179101024265.431.5881789796094399942@mail.test>
- Body: would mediation make sense before going further with Rivera?
- Attachments: none.
- Decision: **matter 1008-001**. Privilege **AC**.

### 44. AAMk9011fa2ac0.eml
- From: Carla Ruiz (office manager) · To: Jonah, Mira, Leah, Ravi, Anika · Date: Mon, 24 Aug 2026 13:00 -0400 · Message-ID: <179101024265.431.12901282147393620540@mail.test>
- Body: submit Q3 time entries by September 5.
- Attachments: none.
- Decision: **firm_admin** (billing). Anika Brandt is a recipient, but the email is not about any matter, so there is no wall issue. Privilege n/a.

### 45. AAMk1bc42b7170.eml
- From: Elena Varga (Calloway) · To: Jonah Hartwell · Date: Mon, 24 Aug 2026 16:10 -0400 · Message-ID: <179101024265.431.9646920121914149221@mail.test>
- Body: draft escrow instructions for Heron are attached.
- Attachment: escrow_instructions.pdf (text layer). "ESCROW INSTRUCTIONS – DRAFT – Buyer: Calloway Medical Group PC – Seller: Riverside Imaging LLC."
- Decision: **matter 1004-002** (Project Heron = Riverside Imaging acquisition). Privilege **AC**. "Heron" is resolved by the sender and the attachment (Riverside Imaging), not the marina.

### 46. AAMk1b66809a11.eml
- From: Sam Pryce (Blue Heron Marina) · To: Jonah Hartwell · Date: Tue, 25 Aug 2026 09:20 -0400 · Message-ID: <179101024266.431.5285193962685057207@mail.test>
- Body: "Heron fuel dock incident". A visiting boat struck the marina's fuel dock and the boat owner's insurer has contacted them. Can Jonah advise on the damage claim?
- Attachments: none.
- Decision: **needs_review**, flag `new-matter-request`. The marina's only matter is 1007-001 (Slip C lease). A fuel-dock damage claim is a new request for legal services outside every existing matter. Nothing in it belongs to the Slip C matter, so it is not filed there (§1). Privilege n/a. **Name overlap:** "Heron" is the marina, not Project Heron. Decision owner: Jonah Hartwell (open a new matter for Blue Heron Marina; conflict check on the boat owner and insurer).

### 47. AAMk4ad8b9b45c.eml
- From: Greg Tolland (Kestrel's counsel) · To: Mira Osei · Date: Tue, 25 Aug 2026 11:00 -0400 · Message-ID: <179101024266.431.8197494633909484586@mail.test>
- Body: an FRE 408 settlement feeler: would the client consider a structured credit on future orders?
- Attachments: none.
- Decision: **matter 1001-001**, flag `hold`. Privilege **none** (opposing counsel; FRE 408 is not attorney-client privilege).

### 48. AAMk1162f28d1a.eml
- From: Mira Osei · To: Dana Whitcomb (Brightwater), Jonah Hartwell · Date: Tue, 25 Aug 2026 15:30 -0400 · Message-ID: <179101024266.431.15697951602826855898@mail.test>
- Body: Mira's recommendation on Kestrel's settlement feeler, marked privileged and confidential.
- Attachments: none.
- Decision: **matter 1001-001**, flag `hold`. Privilege **AC** (firm + client). Privilege log: yes. The log description must not reveal the recommendation.

## Batch 7 (emails 49–56, 2026-08-26 → 2026-09-01)

### 49. AAMk04f542441d.eml
- From: Hank Moreau (Northpoint) · To: Mira Osei · Cc: Tom Weller · Date: Wed, 26 Aug 2026 09:45 -0400 · Message-ID: <179101024266.431.9365392607623500091@mail.test>
- Body: "Tran mediation – authority". Management approved settlement authority up to the amount discussed.
- Attachments: none.
- Decision: **matter 1003-001** (Tran). Privilege **AC**. Anika is not on it, so there is no wall incident.

### 50. AAMkafd8e94b15.eml
- From: Law Weekly <newsletter@lawweekly.test> · To: Front Desk · Date: Wed, 26 Aug 2026 12:30 -0400 · Message-ID: <179101024266.431.6356067927297677731@mail.test>
- Body: newsletter ("This week in employment law": arbitration clauses, remote-work policies).
- Decision: **non_matter** (newsletter). It mentions employment law only generically; it does not concern the Tran matter. Privilege n/a.

### 51. AAMk360023b682.eml
- From: Maria Delgado · To: Ravi Iyer · Date: Thu, 27 Aug 2026 10:15 -0400 · Message-ID: <179101024266.431.7971340252889979952@mail.test>
- Subject "scan0047", **empty body**. It can only be identified from the attachment.
- Attachment: scan0047.pdf, an image-only scan **viewed as an image**, upright. It reads: "LETTERS TESTAMENTARY – Estate of Ricardo Delgado, deceased – Executor: Maria Delgado".
- Decision: **matter 1002-001** (Estate of Ricardo Delgado), not the closed Fenwick purchase. Privilege **AC**.

### 52. AAMked35b00a54.eml
- From: Hank Moreau (Northpoint) · To: Jonah Hartwell · Date: Thu, 27 Aug 2026 14:00 -0400 · Message-ID: <179101024275.431.16626428120426834772@mail.test>
- Subject "fwd", **empty body**. It can only be identified from the attachment.
- Attachment: scan0103.pdf, an image-only scan **viewed as an image**. The page is landscape and the text runs rotated 90°. It reads: "LEASE AMENDMENT NO. 3 – Premises: Dock 7 – Landlord: Harborview Properties – Tenant: Northpoint Logistics LLC – EXECUTED".
- Decision: **matter 1003-002** (Dock 7 Lease Renewal; Jonah). Privilege **AC**. Hank also writes on the Tran matter, but the scan decides this one: it is the lease. It is not 1003-001, so the wall does not apply.

### 53. AAMk0de90794df.eml
- From: Dana Whitcomb (Brightwater) · To: Leah Park · Date: Fri, 28 Aug 2026 09:00 -0400 · Message-ID: <179101024283.431.4653810507848225079@mail.test>
- Subject "photos", body "As discussed." It can only be identified from the attachment.
- Attachment: IMG_2211.pdf, an image-only scan **viewed as an image**, upright. It reads: "Specimen of use – Mark: SUNHARVEST – Retail packaging label – front panel".
- Decision: **matter 1001-002** (SunHarvest Trademark; Leah). Privilege **AC**. Judgment call: the sender is Brightwater, whose Kestrel matter is under hold. This is trademark specimen material, not Kestrel, so it is **not** filed in 1001-001 and gets no hold flag.

### 54. AAMk6078511608.eml
- From: Elena Varga (Calloway) · To: Leah Park · Date: Fri, 28 Aug 2026 11:30 -0400 · Message-ID: <179101024292.431.338879967079889645@mail.test>
- Subject "doc", **empty body**. It can only be identified from the attachment.
- Attachment: doc_0828.pdf, an image-only scan **viewed as an image**. The page is **upside down** (180°). It reads: "CONFIDENTIAL – Calloway Medical Group PC – Risk assessment – July access incident".
- Decision: **matter 1004-001** (Privacy Investigation), **RESTRICTED**, so it goes under `box/Restricted/`, flag `restricted`. Privilege **AC**. Elena handles both Calloway matters; the scan (July access incident) puts this in the restricted matter, not Heron.

### 55. AAMkb5faf8cda9.eml
- From: Kenji Sato (Sato Architecture) · To: Mira Osei · Date: Mon, 31 Aug 2026 10:00 -0400 · Message-ID: <179101024303.431.2213708215508532429@mail.test>
- Subject "Scan", **empty body**. It can only be identified from the attachment.
- Attachment: scan_lien.pdf, an image-only scan **viewed as an image**, upright. It reads: "NOTICE OF MECHANIC'S LIEN – Claimant: Rivera & Sons Roofing – Property: 210 Mill Street".
- Decision: **matter 1008-001** (Rivera Roofing Dispute). Privilege **AC**. Mira should note the escalation: Rivera has filed a lien.

### 56. AAMk6b65bd9acb.eml
- From: Paul Ostrander · To: Ravi Iyer · Date: Tue, 01 Sep 2026 13:00 -0400 · Message-ID: <179101024312.431.13342070296646936724@mail.test>
- Subject "scan", **empty body**. It can only be identified from the attachment.
- Attachment: statement_jul.pdf, an image-only scan **viewed as an image**, upright. It reads: "FIRST HARBOR BANK – Account holder: Paul Ostrander – Statement period: July 2026".
- Decision: **matter 1005-001** (Ostrander Divorce). It answers email 5's request for bank statements. Privilege **AC**. Note: it arrives after the Aug 28 disclosure deadline, and email 38 showed the reminder bounced. Ravi should check whether the disclosure was filed on time.

## Batch 8 (emails 57–64, 2026-09-02 → 2026-09-25)

### 57. AAMk9012b2a414.eml
- From: Sam Pryce (Blue Heron Marina) · To: Jonah Hartwell · Date: Wed, 02 Sep 2026 16:00 -0400 · Message-ID: <179101024322.431.10284820618428862053@mail.test>
- Subject "Re: Heron", body "Receipt attached." There is no In-Reply-To header.
- Attachment: receipt.pdf, an image-only scan **viewed as an image**, upright. It reads: "BLUE HERON MARINA LLC – Slip C – first month's rent received – Receipt no. 0091".
- Decision: **matter 1007-001** (Slip C Lease). Privilege **AC**. **Name overlap trap:** the subject "Re: Heron" and the recipient (Jonah, who also runs Project Heron) would point to 1004-002 on keywords alone. The sender (blueheronmarina.test) and the scanned receipt show it is the marina.

### 58. AAMk32a123f501.eml
- From: Jonah Hartwell · To: Elena Varga (Calloway) · Date: Thu, 03 Sep 2026 09:30 -0400 · Message-ID: <179101024331.431.8017880052074019903@mail.test>
- Body: congratulations on the board approval; the closing checklist is below (follows email 31's Sept 2 Heron vote).
- Attachments: none.
- Decision: **matter 1004-002** (Project Heron). Privilege **AC**.

### 59. AAMkacc74c7ccf.eml
- From: Northstar Insurance Claims <claims@northstar-insurance.test> · To: Front Desk · Date: Fri, 04 Sep 2026 10:00 -0400 · Message-ID: <179101024331.431.17404662151369631467@mail.test>
- Body: "Certificate required – Northpoint Logistics, Dock 7". Under the Dock 7 lease renewal the landlord needs an updated certificate naming it as additional insured. Please confirm the tenant's broker.
- Attachments: none.
- Decision: **matter 1003-002** (Dock 7 Lease Renewal). Privilege **none** (third-party insurer). It is addressed to counsel about our client's matter, so not misdirected. **Name overlap:** Northstar (insurer) and Northpoint (client) are different entities. Action: Jonah to confirm the broker with Hank.

### 60. AAMk5645100358.eml
- From: **Anika Brandt** · To: Hank Moreau (Northpoint) · Date: Tue, 08 Sep 2026 15:00 -0400 · Message-ID: <179101024331.431.2352544904900230228@mail.test>
- Body: please confirm the signatory for the Dock 7 renewal signature blocks.
- Attachments: none.
- Decision: **matter 1003-002** (Dock 7). Privilege **AC**. **Wall check:** Anika is screened only from **1003-001** (Tran). This email is purely about Dock 7 and contains nothing about Tran, so **no ethical-wall flag and no incident**. Working for the same client on a different matter is not barred by the wall in matters.csv.

### 61. AAMk4f164f1513.eml
- From: Priya Iyer <priya.iyer@mailbox.test> · To: Ravi Iyer · Date: Thu, 10 Sep 2026 09:00 -0400 · Message-ID: <179101024332.431.17588211232258734017@mail.test>
- Body: "Are we still on for dinner Friday? x"
- Decision: **non_matter** (personal message). Privilege n/a.

### 62. AAMk03552454f1.eml
- From: Greg Tolland (Kestrel's counsel) · To: Mira Osei · Date: Mon, 14 Sep 2026 11:00 -0400 · Message-ID: <179101024332.431.17937871436100237347@mail.test>
- Body: Kestrel's second production volume is attached.
- Attachment: production_vol2_index.pdf (text layer). "Kestrel Packaging Ltd – Document Production Volume 2 – Index: KPL004001–KPL006250."
- Decision: **matter 1001-001**, flag `hold`. Privilege **none**.

### 63. AAMk68f6cdb2f8.eml
- From: Maria Delgado · To: Ravi Iyer · Date: Mon, 21 Sep 2026 10:30 -0400 · Message-ID: <179101024332.431.3193745265520547928@mail.test>
- Body: "Bakery LLC – name ideas". Her daughter likes "Delgado Bakery LLC". Is the name available?
- Attachments: none.
- Decision: **needs_review**, flag `new-matter-request`. This is a follow-up to email 37 (the daughter's LLC formation). No matter exists for it and it is unrelated to the estate. Privilege n/a. Decision owner: Ravi Iyer. **Back-reference:** email 37's entry is annotated.

### 64. AAMkecc20ef164.eml
- From: Dana Whitcomb (Brightwater) · To: Mira Osei · Date: Fri, 25 Sep 2026 16:00 -0400 · Message-ID: <179101024332.431.16965563983247473530@mail.test>
- Body: Brightwater IT wants to purge the April purchasing mailbox to save space. Is that OK?
- Attachments: none.
- Decision: **matter 1001-001**, flags `hold;attorney-action`. The April purchasing mailbox holds the April Kestrel correspondence (email 39's attachment is an export of exactly that mailbox). The litigation hold since 08-10 forbids deleting anything related to Kestrel, so the client is asking for something the hold forbids (§5). Privilege **AC**. Privilege log: yes. Action: **Mira must tell Brightwater promptly not to purge** and should confirm preservation in writing. **Back-reference:** email 39's entry is annotated.


# Memo updates (Part 3)

The memos were read one at a time, in date order. For each memo I re-read the affected emails in full, updated the decisions and rebuilt box/ in a working folder, and ran tools/check_filing.py before reading the next memo.

## memo_01 (2026-09-28, Carla Ruiz) – new matter 1002-003 "Formation of Delgado Bakery LLC" (Ravi Iyer, open)
Re-read all five emails then in `_Needs_Review/`:
- **AAMk8dff666589.eml** (email 37). Maria asks for help with her daughter's bakery LLC. This is the request the new matter answers. **Changed:** needs_review → **matter 1002-003**, privilege **AC** (client contact Maria Delgado ↔ Ravi). Flag `new-matter-request` **removed** (the memo says these are no longer new-matter requests). It moved to `box/Clients/1002 Delgado Maria/1002-003 Delgado Bakery LLC Formation/Correspondence/`.
- **AAMk68f6cdb2f8.eml** (email 63). "Delgado Bakery LLC" name availability. Same change: **matter 1002-003**, AC, no flags.
- Not affected: AAMkc707b37e14 (Kestrel engagement request), AAMk4ba3ea284d (misdirected Martinez), and AAMk1b66809a11 (Blue Heron fuel dock). None of them concerns the bakery.
- Also checked the Delgado emails already filed (emails 4, 14, 36, 51). They concern the estate and the Fenwick purchase, not the bakery, so they are unchanged.

## memo_02 (2026-09-29, Carla Ruiz) – intake decisions
Re-read in full: AAMkc707b37e14 (Kestrel), AAMk1b66809a11 (fuel dock), and every other Blue Heron Marina email (AAMk7218187993 sig page, AAMk15a9964aef COI, AAMk9012b2a414 receipt). The COI and receipt scans were **re-opened as images**: the COI reads "Re: Slip C lease" and the receipt reads "Slip C – first month's rent received". I also re-read AAMk090f3ebdd3 (the Ostrander brother's slip contract at the marina).
- **AAMkc707b37e14.eml** (email 27). The Kestrel engagement was **declined**. **Changed:** needs_review → **firm_admin**, path `box/Firm_Admin/Declined_Intake/`, privilege n/a. Flags `potential-conflict;new-matter-request` → **`declined-intake;new-matter-request`**: declined-intake takes potential-conflict's place, as the memo directs. I kept new-matter-request because rule 5 lists every flag that applies, and the email still asks for services outside every matter. The memo replaces only potential-conflict.
- **AAMk1b66809a11.eml** (email 46). The fuel-dock damage claim is now **matter 1007-002** (Jonah). **Changed:** needs_review → matter 1007-002, privilege **AC**. Flag `new-matter-request` **removed**: a matter now exists for the request, the same treatment memo_01 set for opened matters.
- Not affected: AAMk7218187993, AAMk15a9964aef and AAMk9012b2a414 are all Slip C lease material and stay in 1007-001. AAMk090f3ebdd3 is the brother's slip contract, not the fuel-dock claim. It stays in 1005-001 with potential-conflict;new-matter-request (the memo does not decide that request).

## memo_03 (2026-09-30, Jonah Hartwell, ethics partner) – Tom Weller also screened from 1003-001, effective 2026-08-15
Re-read in full every email filed in or cross-referenced to 1003-001 (AAMkcd2f45e678, AAMka69d95847e, AAMk9f28518867, AAMka775139237, AAMk04f542441d), and every email on which Tom Weller appears (AAMkcd2f45e678, AAMk65fb710734, AAMkbda7677796, AAMk017ff12229, AAMk04f542441d).
- **AAMk04f542441d.eml** (email 49, 2026-08-26, Hank Moreau → Mira, **cc Tom Weller**, "Tran mediation – authority"). This is about 1003-001 and falls on or after 2026-08-15. **Changed:** flag `ethical-wall` added, and a **new wall incident** (Tom Weller, cc, 1003-001). Privilege AC and path are unchanged.
- **AAMkcd2f45e678.eml** (email 7, 2026-08-05). Tom is copied on a Tran email, but the date is before 2026-08-15. The memo says "nothing before 2026-08-15 counts for Tom", so there is **no incident for Tom**. The Anika incident and flag are unchanged.
- Not affected: AAMk65fb710734 and AAMkbda7677796 (Kestrel/1001-001) and AAMk017ff12229 (Sato/1008-001). Tom is on them, but they are not about Tran. AAMka69d95847e, AAMk9f28518867 and AAMka775139237 do not include Tom.

## memo_04 (2026-10-01, Carla Ruiz) – client renamed: Brightwater Foods Inc. → Brightwater Brands Inc.; client folder "1001 Brightwater Brands"
Re-read in full all 17 emails filed under client 1001 and every email from the brightwaterfoods.test domain (the same set). Each one still belongs to Brightwater, in the same matter:
- 1001-001 Kestrel Supply Dispute (13): AAMkdd73cf256d, AAMkc7ec99108d, AAMk980ab8ab67, AAMk65fb710734, AAMk73f6fa5db8, AAMkbda7677796, AAMk32d7a94ded, AAMk9770c6a5b8 (retained _dup), AAMk15d7185dda, AAMk4ad8b9b45c, AAMk1162f28d1a, AAMk03552454f1, AAMkecc20ef164.
- 1001-002 SunHarvest Trademark (3): AAMkdb8f4d3e27, AAMk41b53302fc, AAMk0de90794df. Plus the cross-reference stub for AAMk73f6fa5db8.
- 1001-003 General Corporate (1): AAMk5376c468ae.
- **Changed:** only the box_path (and attachments_saved) of these 17 emails, from `box/Clients/1001 Brightwater Foods/…` to `box/Clients/1001 Brightwater Brands/…`. The 7 extracted attachments moved with them. The stub's "Filed at:" line now points to the new path. Category, matter, flags and privilege are unchanged. Matter numbers and matter folders are unchanged.
- Not affected: AAMka2b1852f27 (pre-hold duplicate, `_Duplicates`, no client path). AAMkc707b37e14 (Kestrel declined intake, Firm_Admin). Privilege-log rows carry no paths, so they are unchanged. The case caption "Brightwater v. Kestrel" in matter names and subjects is the email's own text and was not altered.
