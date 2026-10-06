I'm a legal operations consultant. A small law firm, Hartwell & Osei LLP, is moving from Outlook to Box, and I need its exported mailbox filed into the new Box structure following the firm's filing rules. Work in the folder that contains mailbox/ (64 .eml files exported from Outlook), matters.csv, staff.csv, filing_rules.md, memos/ (four dated memos), INPUTS.md and MANIFEST.sha256.

## Inputs
- mailbox/*.eml: the exported emails. File names are Outlook IDs and tell you nothing. Many emails carry PDF attachments, and 15 of those are image-only scans (one is rotated). No OCR software is installed, so you must look at each scan yourself. Several emails can only be identified from their attachment.
- matters.csv: every client and matter, with folder names, responsible attorney, status, closed dates, litigation holds, ethical walls and restricted matters.
- staff.csv: firm staff.
- filing_rules.md: the firm's filing rules. Follow them exactly.
- memos/: four memos sent after the first filing pass. Do not read them until Part 3.
- INPUTS.md and MANIFEST.sha256: the list of the 71 input files and their checksums.

## Before you start: confirm the inputs
Check that you received the complete file set: run `sha256sum -c MANIFEST.sha256`, compare the folder with INPUTS.md, and confirm that all 64 emails parse and that their 24 PDF attachments open. If anything is missing, empty or unreadable, stop and tell me exactly what. Do not guess or work around missing client files. Only the checksums and file list are checked here. The memo contents are still read only in Part 3.

## How to work
- Do all of the work yourself in this session. Do not hand any part of it to sub-agents, background tasks or parallel workers. I review your own trace, and work done elsewhere is not in it.
- Every filing decision must come from you reading that email and its attachments. Do not write a script that assigns categories, matters, flags or privilege by keyword or domain matching. The rules forbid filing by keyword alone. Scripts are fine for mechanical work: parsing headers, extracting attachments, building file names, copying files and writing the CSVs from the decisions you recorded.
- Work through to the end without stopping to ask me questions. Where the inputs leave something open, decide by the rules, record the reasoning in triage_notes.md, and use needs_review where the rules call for it. Stop early only for the input problem described above.
- Look at each scanned page as its own image. Do not combine scans into a montage or contact sheet, because small renders hide the details that decide the matter (names, file numbers, the rotated page).

## Part 1: First filing pass (everything in output/phase1/)
1. Before filing anything, triage the mailbox in batches of 8 emails, in Date order. For each batch, read every email in full, open every attachment (scans as images), and append the batch's entries to triage_notes.md before you open the next batch. When a later email changes your view of an earlier one (a reply, a forward, a bounce, a duplicate), go back and correct the earlier entry, and say so in the note. triage_notes.md contains one entry per email with the sender, recipients, date, Message-ID, a one-line summary of the body, what each attachment shows (for scans, what you saw), the category and matter you chose, and why. Note every judgment call: overlapping names, two-matter emails, walls, holds, closed matters, conflicts, duplicates.
2. Build the Box structure in output/phase1/box/ exactly as the rules describe. Copy each email under its new file name, extract the attachments of matter emails into Documents/, and create the cross-reference stubs. Every email must appear exactly once as a primary copy.
3. Produce these files in output/phase1/:
   - filing_log.csv: one row per email, with columns email_file (the original mailbox name), received (YYYY-MM-DD HH:MM), sender, subject, category, primary_matter, xref_matters, privilege, flags, box_path, attachments_saved.
   - wall_incidents.csv: email_file, received, screened_person, role (sender/to/cc), matter, action.
   - privilege_log.csv: every email filed in matter 1001-001 (under litigation hold) with privilege AC or WP, with columns date, from, to, cc, subject, privilege, description. The description must not reveal privileged content.
   - needs_review.md: every needs_review email with the reason, what the firm must decide, and who should decide it.
   - attorney_actions.md: for each attorney (and for IT and the ethics partner), the emails that need their action and why. This covers post-closing items, potential conflicts, new-matter requests, wall incidents, delivery failures, phishing and requests that conflict with the hold.
   - filing_summary.md: counts by category, by matter and by responsible attorney; the number of files in box/; and the open issues.

## Part 2: Checker
Write tools/check_filing.py, which takes an output folder and validates it against the rules and the inputs. It must check that every mailbox email appears exactly once as a primary copy; that every box_path in filing_log.csv exists; that file names follow the naming rule; that restricted matters sit only under box/Restricted/; that every stub's "Filed at:" path exists and that no stub crosses clients; that every extracted attachment exists and is named correctly; that hold duplicates are retained; and that the counts in filing_summary.md match the log. Run it against output/phase1/ and fix the data or the checker until it passes cleanly. Then copy output/phase1/ to a scratch folder, break three things in the copy (move a file, corrupt a stub, rename an attachment), and confirm the checker catches all three.

## Part 3: Memos (final state in output/final/)
Now read the memos in date order, one at a time. Each one changes facts. Do not read the next memo until you have finished the current one: find every email the memo affects by re-reading those emails (not by searching for keywords), update those decisions and every file that depends on them, rebuild box/ in a working folder, run tools/check_filing.py against it and make it pass, and then write the matching memo_reply_0N.md telling the sender exactly what you changed (emails moved, flags, incidents, paths).
After the last memo:
- output/final/ must contain the complete, current version of box/ and of every Part 1 file.
- Write changes_report.md: every email whose category, matter, flags, privilege or path differs between output/phase1/filing_log.csv and output/final/filing_log.csv, with the memo that caused the change, plus the changes to the wall incidents, privilege log, needs_review list, attorney actions and counts.
- Run tools/check_filing.py against output/final/ and make it pass.

## Verification
Before finishing, open every scanned attachment again as an image and confirm the matter you chose for it. Re-read every email you flagged or placed in needs_review, and every email involving Heron, Fenwick, Kestrel, Tran or a screened person, and confirm the decision against the rules. Check that the files in each output folder agree with each other and with box/. If you find a mistake, fix the decision, rebuild everything that depends on it, and check again. Write verification_log.md listing each check, the mistakes found, what you changed, the final checker output for both folders, and the result of the deliberate-break test.

## Acceptance checks (how I will judge the result)
- triage_notes.md covers all 64 emails, and every scanned attachment is described from its image.
- Both filing logs have exactly 64 rows, and every category, matter, cross-reference, privilege value, flag and path follows the rules (and, for final, the memos).
- box/ in each folder matches its filing log exactly: no missing, extra or misnamed files. Restricted items stay under Restricted, and no stub or copy crosses clients.
- wall_incidents.csv, privilege_log.csv, needs_review.md and attorney_actions.md are complete and correct for their phase.
- The checker really validates the rules, passes on both folders and catches the three deliberate breaks.
- memo_reply_01 to 04 and changes_report.md match the real differences between phase 1 and final.
- verification_log.md shows real comparisons, and no unresolved mistake remains.
- No decision relies on information that is not in the emails, their attachments, the CSVs, the rules or the memos.
- The trace shows the work: each email and each scan was actually read, triage was done batch by batch, each memo was handled and checked before the next, and no sub-agents were used.

When finished, give me a short summary: category counts for phase 1 and final, the emails in needs_review at each phase, the wall incidents, the privilege log count, what each memo changed, and the checker results.
