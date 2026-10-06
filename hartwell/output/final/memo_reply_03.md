To: Jonah Hartwell (ethics partner)
Cc: Mira Osei
Re: Your memo of 2026-09-30 – Tran ethical wall - expanded (Tom Weller from 2026-08-15)

Jonah,

I applied Tom Weller's screen from 1003-001 back to 2026-08-15. I re-read every email filed in or cross-referenced to Tran v. Northpoint, and every email Tom sent, received or was copied on. There is **one new incident**.

**New wall incident (wall_incidents.csv: 3 → 4 rows)**

| email file | received | screened person | role | matter | path (unchanged) |
|---|---|---|---|---|---|
| AAMk04f542441d.eml | 2026-08-26 09:45 | Tom Weller | cc | 1003-001 | `box/Clients/1003 Northpoint Logistics/1003-001 Tran Employment Claim/Correspondence/2026-08-26_0945_moreau_tran-mediation-authority.eml` |

This is Hank Moreau (Northpoint) to Mira, copying Tom, saying management approved settlement authority for the Tran mediation.
- Flag change on that email: none → **`ethical-wall`**. Category (matter), matter (1003-001), privilege (AC) and path are unchanged. No emails were moved.

**Checked, and not an incident for Tom**
- AAMkcd2f45e678.eml (2026-08-05, Anika Brandt → Mira, cc Tom, "Tran deposition outline?") is before 2026-08-15, so per your memo it does not count for Tom. It stays a single incident for Anika.
- AAMk65fb710734.eml (2026-08-10) and AAMkbda7677796.eml (2026-08-11) are Kestrel/1001-001. AAMk017ff12229.eml (2026-08-18) is Sato/1008-001. Tom is on these, but they are not about Tran.
- The other Tran emails (AAMka69d95847e, AAMk9f28518867, AAMka775139237) do not include Tom.

**Knock-on changes**
- Anika Brandt's three incidents are unchanged. Total incidents: **4** (Anika ×3, Tom ×1).
- Attorney actions: added under you (notify/confirm the new screen), under Mira (remove Tom from Tran work and correspondence; ask Northpoint not to copy him) and in a new section for Tom Weller (do not use the information; acknowledge the screen).
- Flag count: ethical-wall 3 → 4 emails. Category, matter and attorney counts are unchanged. The privilege log is unchanged (7 entries).
- The wall facts used for filing now record both screens on 1003-001 (Anika from 2026-07-01, Tom from 2026-08-15). The rebuilt folder passes tools/check_filing.py, which derives wall incidents independently from the headers and screen dates.
