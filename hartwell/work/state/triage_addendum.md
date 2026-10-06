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
