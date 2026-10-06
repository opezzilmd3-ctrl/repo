To: Carla Ruiz (office manager)
Cc: Mira Osei, Leah Park, Jonah Hartwell
Re: Your memo of 2026-10-01 – Client name change (Brightwater Foods Inc. → Brightwater Brands Inc.)

Carla,

The client folder is renamed from `box/Clients/1001 Brightwater Foods/` to **`box/Clients/1001 Brightwater Brands/`**. Everything that pointed to the old path has been updated. I re-read all 17 emails filed under client 1001 to confirm they still belong there. Matter numbers and matter folder names are unchanged (1001-001 Kestrel Supply Dispute, 1001-002 SunHarvest Trademark, 1001-003 General Corporate).

**What changed**
- **17 emails** had their box_path changed, as listed below. No category, matter, flag or privilege value changed. Hold flags, the retained duplicate and the attorney-action flag on the April-mailbox purge request all carry over.
- **7 extracted attachments** moved with their matters' Documents folders. Their file names are unchanged.
- **1 cross-reference stub** (`1001-002 SunHarvest Trademark/Correspondence/2026-08-10_1430_whitcomb_two-things.eml.xref.txt`) now reads `Filed at: box/Clients/1001 Brightwater Brands/1001-001 Kestrel Supply Dispute/Correspondence/2026-08-10_1430_whitcomb_two-things.eml`.
- The client name in the matter records used for filing is now Brightwater Brands Inc. The case caption "Brightwater v. Kestrel" in subjects and matter names is unchanged, because it is the emails' own text and the court caption.
- Not changed: the pre-hold duplicate AAMka2b1852f27.eml (in `box/_Duplicates/`), the declined Kestrel intake (in `box/Firm_Admin/Declined_Intake/`), the privilege log (7 entries; it carries no paths), wall incidents (4), needs_review (1), and all counts.

**Emails whose path changed** (old prefix `box/Clients/1001 Brightwater Foods/` → new prefix `box/Clients/1001 Brightwater Brands/`; the rest of each path is unchanged)

| email file | received | matter | path after the client folder |
|---|---|---|---|
| AAMkdd73cf256d.eml | 2026-08-03 09:12 | 1001-001 | `1001-001 Kestrel Supply Dispute/Correspondence/2026-08-03_0912_whitcomb_kestrel-shipment-records.eml` |
| AAMkdb8f4d3e27.eml | 2026-08-03 14:40 | 1001-002 | `1001-002 SunHarvest Trademark/Correspondence/2026-08-03_1440_park_sunharvest-uspto-office-action.eml` |
| AAMkc7ec99108d.eml | 2026-08-04 10:05 | 1001-001 | `1001-001 Kestrel Supply Dispute/Correspondence/2026-08-04_1005_tolland_brightwater-v-kestrel-proposed-protectiv.eml` |
| AAMk980ab8ab67.eml | 2026-08-07 11:00 | 1001-001 | `1001-001 Kestrel Supply Dispute/Correspondence/2026-08-07_1100_tolland_brightwater-v-kestrel-proposed-protectiv.eml` |
| AAMk65fb710734.eml | 2026-08-10 09:00 | 1001-001 | `1001-001 Kestrel Supply Dispute/Correspondence/2026-08-10_0900_osei_litigation-hold-notice-kestrel-dispute.eml` |
| AAMk73f6fa5db8.eml | 2026-08-10 14:30 | 1001-001 | `1001-001 Kestrel Supply Dispute/Correspondence/2026-08-10_1430_whitcomb_two-things.eml` |
| AAMkbda7677796.eml | 2026-08-11 10:10 | 1001-001 | `1001-001 Kestrel Supply Dispute/Correspondence/2026-08-11_1010_weller_kestrel-production-bates-ranges.eml` |
| AAMk5376c468ae.eml | 2026-08-14 09:05 | 1001-003 | `1001-003 General Corporate/Correspondence/2026-08-14_0905_whitcomb_board-minutes-q2.eml` |
| AAMk32d7a94ded.eml | 2026-08-14 11:25 | 1001-001 | `1001-001 Kestrel Supply Dispute/Correspondence/2026-08-14_1125_tolland_deposition-of-d-whitcomb.eml` |
| AAMk9770c6a5b8.eml | 2026-08-14 11:25 | 1001-001 | `1001-001 Kestrel Supply Dispute/Correspondence/2026-08-14_1125_tolland_deposition-of-d-whitcomb_dup.eml` |
| AAMk15d7185dda.eml | 2026-08-20 11:45 | 1001-001 | `1001-001 Kestrel Supply Dispute/Correspondence/2026-08-20_1145_whitcomb_april-emails.eml` |
| AAMk41b53302fc.eml | 2026-08-20 15:20 | 1001-002 | `1001-002 SunHarvest Trademark/Correspondence/2026-08-20_1520_park_sunharvest-response-filed.eml` |
| AAMk4ad8b9b45c.eml | 2026-08-25 11:00 | 1001-001 | `1001-001 Kestrel Supply Dispute/Correspondence/2026-08-25_1100_tolland_settlement-discussion-fre-408.eml` |
| AAMk1162f28d1a.eml | 2026-08-25 15:30 | 1001-001 | `1001-001 Kestrel Supply Dispute/Correspondence/2026-08-25_1530_osei_settlement-strategy-privileged.eml` |
| AAMk0de90794df.eml | 2026-08-28 09:00 | 1001-002 | `1001-002 SunHarvest Trademark/Correspondence/2026-08-28_0900_whitcomb_photos.eml` |
| AAMk03552454f1.eml | 2026-09-14 11:00 | 1001-001 | `1001-001 Kestrel Supply Dispute/Correspondence/2026-09-14_1100_tolland_kestrel-document-production-vol-2.eml` |
| AAMkecc20ef164.eml | 2026-09-25 16:00 | 1001-001 | `1001-001 Kestrel Supply Dispute/Correspondence/2026-09-25_1600_whitcomb_old-april-mailbox.eml` |

No old-path reference remains in box/, filing_log.csv, the stub or the report files. The rebuilt folder passes tools/check_filing.py.
