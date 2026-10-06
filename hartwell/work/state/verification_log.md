# Verification log

All checks below were run in this session after the four memo rounds. Raw outputs are pasted, not summarised.

## V1. Inputs (before any work)
- `sha256sum -c MANIFEST.sha256`: **72/72 OK** (71 inputs + INPUTS.md).
- The folder listing equals the manifest list (diff empty), matching INPUTS.md: 64 .eml, matters.csv, staff.csv, filing_rules.md, 4 memos.
- All 64 emails parse with Python `email` and show no MIME defects. All **24 PDF attachments** open in `pdfinfo`. **15** have no text layer (image-only), matching INPUTS.md.

## V2. Every scanned attachment re-opened as an image (from the filed copies in output/final/box)
All 15 image-only PDFs were re-rendered **from the extracted files in output/final/box/…/Documents/** with `pdftoppm -r 110`. Each page was viewed alone as its own image, with no montage. The content was compared with the matter folder it sits in.

| # | filed at (client/matter/Documents/…) | what the image shows | result |
|---|---|---|---|
| v01 | `1001 Brightwater Brands/1001-002 SunHarvest Trademark/Documents/2026-08-28_IMG_2211.pdf` | Specimen of use – Mark: SUNHARVEST – retail packaging label, front panel (upright) | ✔ matches folder |
| v02 | `1002 Delgado Maria/1002-001 Estate of Ricardo Delgado/Documents/2026-08-04_scan_0812.pdf` | APPRAISAL REPORT – 88 Alder Street – Estate of Ricardo Delgado – date-of-death valuation $412,000 (landscape, text rotated 90°) | ✔ matches folder |
| v03 | `1002 Delgado Maria/1002-001 Estate of Ricardo Delgado/Documents/2026-08-27_scan0047.pdf` | LETTERS TESTAMENTARY – Estate of Ricardo Delgado – Executor Maria Delgado (upright) | ✔ matches folder |
| v04 | `1002 Delgado Maria/1002-002 Purchase 14 Fenwick Lane/Documents/2026-08-07_hoa_letter.pdf` | Fenwick Lane HOA – To: Maria Delgado, 14 Fenwick Lane – transfer fee on June 2026 conveyance $750 (upright, skewed) | ✔ matches folder |
| v05 | `1003 Northpoint Logistics/1003-001 Tran Employment Claim/Documents/2026-08-11_personnel_excerpt.pdf` | Northpoint Logistics personnel file – Employee Jessica Tran – performance reviews 2024–2026 (upright) | ✔ matches folder |
| v06 | `1003 Northpoint Logistics/1003-002 Dock 7 Lease Renewal/Documents/2026-08-05_landlord_letter.pdf` | HARBORVIEW PROPERTIES – Re: Dock 7 lease renewal – 5-year term, 4% escalator – Tenant Northpoint (upside down, 180°) | ✔ matches folder |
| v07 | `1003 Northpoint Logistics/1003-002 Dock 7 Lease Renewal/Documents/2026-08-27_scan0103.pdf` | LEASE AMENDMENT NO. 3 – Premises Dock 7 – Harborview / Northpoint – EXECUTED (landscape, rotated 90°) | ✔ matches folder |
| v08 | `1005 Ostrander Paul/1005-001 Ostrander Divorce/Documents/2026-08-21_parenting_plan.pdf` | PROPOSED PARENTING PLAN – In re the Marriage of Ostrander – submitted by Respondent (upright) | ✔ matches folder |
| v09 | `1005 Ostrander Paul/1005-001 Ostrander Divorce/Documents/2026-09-01_statement_jul.pdf` | FIRST HARBOR BANK – Account holder Paul Ostrander – July 2026 statement (upright, skewed) | ✔ matches folder |
| v10 | `1006 Fenwick Lane HOA/1006-001 Assessment Collections/Documents/2026-08-06_ledger.pdf` | Fenwick Lane HOA – owner ledger Unit 22 (K. Albright) – balance $1,860 (upright) | ✔ matches folder |
| v11 | `1007 Blue Heron Marina/1007-001 Slip C Lease/Documents/2026-08-06_sigpage.pdf` | BLUE HERON MARINA LLC – Slip C Lease Agreement signature page – S. Pryce (upright) | ✔ matches folder |
| v12 | `1007 Blue Heron Marina/1007-001 Slip C Lease/Documents/2026-08-18_coi.pdf` | CERTIFICATE OF LIABILITY INSURANCE – holder Blue Heron Marina LLC – Re: Slip C lease (landscape, rotated 90°) | ✔ matches folder |
| v13 | `1007 Blue Heron Marina/1007-001 Slip C Lease/Documents/2026-09-02_receipt.pdf` | BLUE HERON MARINA LLC – Slip C first month's rent received – Receipt 0091 (upright) | ✔ matches folder |
| v14 | `1008 Sato Architecture/1008-001 Rivera Roofing Dispute/Documents/2026-08-31_scan_lien.pdf` | NOTICE OF MECHANIC'S LIEN – Rivera & Sons Roofing – 210 Mill Street (upright) | ✔ matches folder |
| v15 | `1004 Calloway Medical Group/1004-001 Privacy Investigation/Documents/2026-08-28_doc_0828.pdf` | CONFIDENTIAL – Calloway Medical Group – risk assessment, July access incident (upside down, 180°) | ✔ matches folder |

Result: **15/15 confirmed, no mistake.** v15 sits under `box/Restricted/` (the index trims the `Restricted/` prefix). Observation: the brief mentions one rotated scan. I found five pages that are not upright: three turned 90° on a landscape page (v02, v07, v12) and two upside down (v06, v15). None of them has a PDF /Rotate flag, so the rotation is in the image itself. All were read correctly.

## V3. Re-read of flagged, needs_review, Heron, Fenwick, Kestrel, Tran and screened-person emails
45 emails were selected by *either* phase: any flag, needs_review, or mention of Heron/Fenwick/Kestrel/Tran, Anika Brandt or Tom Weller. Each was re-read in full, with its phase-1 and final decision printed beside it (`work/verify_reread.txt`). Confirmed against the rules:
- **Heron (8):** Project Heron, Calloway 1004-002 (AAMk2fcb008853, AAMk1bc42b7170, AAMk32a123f501; AAMk3b84e55160 via stub). Blue Heron Marina 1007-001 Slip C (AAMk7218187993, AAMk15a9964aef, AAMk9012b2a414 – "Re: Heron" is the marina receipt). 1007-002 (AAMk1b66809a11, final). AAMk090f3ebdd3 is the brother's slip contract, in 1005-001 with a conflict flag. ✔
- **Fenwick (3):** AAMk8917362f25 (HOA ledger, debtor K. Albright, not a client) → 1006-001. AAMke3cf44dd3f → 1002-002, post-closing; potential-conflict. AAMk833acb6266 → 1006-001, potential-conflict. No stub crosses clients. ✔
- **Kestrel (12 + duplicates):** hold applied only from 2026-08-10. The three earlier 1001-001 emails carry no hold flag. The 08-07 duplicate goes to `_Duplicates` and the 08-14 duplicate is retained `_dup` with hold;duplicate-retained. The purge request has hold;attorney-action. The Kestrel CEO intake is needs_review → declined (memo_02). ✔
- **Tran / screened persons:** wall incidents are Anika ×3 (sender 08-05, cc 08-11, cc 08-18 via xref) and Tom ×1 (cc 08-26, final only). There is no incident for Tom on 08-05 (before his 08-15 start), and none for Anika on AAMk5645100358 (Dock 7 only) or AAMk9011fa2ac0 (firm billing). ✔
- **Other flagged items:** restricted ×4 under Restricted only; phishing (look-alike hartwe11-osei.test); delivery failure filed in 1005-001 with the original; misdirected Martinez left unread. ✔

Result: **no filing decision changed in verification.**

## V4. Agreement between files and box/
- **box/ vs filing log (independent of the checker):** `find box -type f` minus (every box_path + every attachments_saved entry) leaves exactly the 3 `.xref.txt` stubs, in **both** folders. Nothing is missing, extra or misnamed.
- **Cross-file script** (`work/tools/crosscheck.py`): the needs_review.md table and sections equal the log's needs_review set. attorney_actions.md names every email with an action flag and every needs_review email. Every wall incident row is flagged in the log and listed under the ethics partner. triage_notes.md has exactly 64 entries, one per email. → **phase1 OK, final OK.**
- **phase1 → final diff** (`changes_report.md`): 22 rows differ (5 substantive from memos 01–03, 17 path-only from memo_04). This matches memo_reply_01 (2 emails), 02 (2 emails), 03 (1 email/1 incident) and 04 (17 emails, 7 attachments, 1 stub). Every box path quoted in the replies resolves: new paths exist in output/final, old paths existed in output/phase1.
- No old `1001 Brightwater Foods` path remains in output/final (box/, CSVs, stubs, reports). The only mention is the historical "from" description in the triage addendum and the reply/report text.

## V5. Mistakes found during the work and what I changed
| # | found when | mistake | fix |
|---|---|---|---|
| 1 | first checker run on phase1 | **Checker bug:** an empty `Cc:` header produced a blank address, so two internal WP emails (AAMkbda7677796, AAMk017ff12229) were reported as having a non-firm participant. | Checker now ignores empty addresses. The data was correct; it then passed. |
| 2 | extra break test | **Checker gap:** a stray stub pointing to another client was reported only as "not backed by the log", not as crossing clients. | Reordered so the cross-client test runs on every stub first. It now reports "crosses clients (1006 … → 1002 …)". |
| 3 | code review of checker | A leftover no-op loop inside the per-email naming check. | Removed (no behaviour change). |
| 4 | before sending memo_reply_01 | **Reply error:** I wrote Ravi Iyer's count as 11 → 13. | Checked against both summaries; corrected to **9 → 11**. |
| 5 | memo_02 build | The builder did not create the new `Firm_Admin/Declined_Intake/` folder before copying into it. | Builder now creates each destination folder. Fixed before the round ran. |
| 6 | verification V4 | **Cross-check script false alarm** on phase1: it located the ethics-partner section by a phrase that also appears earlier in phase 1's Jonah section. | Anchored on the section heading. Phase1 OK; the data was correct. |

No filing decision (category, matter, cross-reference, privilege, flag) had to be corrected during verification. Judgment calls and interpretations are recorded in triage_notes.md: privilege-log scope, the duplicate tie-break, the `_dup` privilege value, stubs pointing into Restricted, potential-conflict on AAMk090f3ebdd3, and keeping new-matter-request on the declined intake.

## V6. Final checker output – output/phase1
```
{c1}```

## V7. Final checker output – output/final
```
{c2}```

## V8. Deliberate-break test (copy of output/phase1 in the scratchpad; final checker version)
Breaks: (1) **moved** `2026-08-24_1030_sato_rivera-mediation.eml` from 1008-001 into 1006-001; (2) **corrupted** the 1001-002 stub's "Filed at:" line; (3) **renamed** attachment `2026-08-04_scan_0812.pdf` → `appraisal_88_alder.pdf`.
```
{brk}```
**All three breaks were caught** (exit 1), each by its own check: primary/extra-file, stub target, attachment name.

Extra probe (cross-client stub, a restricted email moved under Clients/, a deleted hold duplicate), run on the earlier checker version:
```
{extra}```
After fix #2 the cross-client stub is also reported as `crosses clients (1006 Fenwick Lane HOA → 1002 Delgado Maria)`.

## Result
Both folders pass `tools/check_filing.py` cleanly, all cross-file checks agree, all 15 scans are re-confirmed, and **no unresolved mistake remains.**
