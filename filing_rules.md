# Hartwell & Osei LLP: email filing rules (Outlook export → Box)

Applies to every message in mailbox/. All people, clients and matters are listed in matters.csv and staff.csv. Firm staff use @hartwell-osei.test addresses.

## 1. Categories (each email gets exactly one)
- **matter**: concerns an existing open or closed matter in matters.csv.
- **needs_review**: cannot be filed in a client folder yet. This covers a request for legal services that does not belong to any existing matter (a possible new matter), a request to represent a party who is adverse to an existing client (conflict check), and an email clearly meant for another firm or person (misdirected; do not read it further).
- **firm_admin**: the firm's own business (billing, IT, storage, staff notices).
- **non_matter**: unsolicited marketing, newsletters, personal messages, and suspected phishing.
- **duplicate**: same Message-ID as an earlier email (see rule 6).

Identify the matter from everything available: sender, recipients, subject, body, and the content of every attachment (several attachments are scans, so read them). Client contacts are not listed. Work them out from email domains and content. Names and code names can overlap between unrelated matters. Never file by keyword alone.

## 2. Emails touching two matters
- If an email makes substantive requests or updates on two matters **of the same client**, the primary matter is the one addressed first in the body. File the email there, and put a cross-reference stub in the other matter's Correspondence folder.
- Never place a stub, a copy or any reference in a **different client's** folders. If an email affects another client, use the potential-conflict flag instead (rule 5).
- If an email mainly concerns an existing matter but also asks for services on something new, file it in the existing matter and add the flag new-matter-request.

## 3. Box paths
- Matter emails: `box/Clients/<client_folder>/<matter_folder>/Correspondence/<file name>`
- Restricted matters (matters.csv notes say RESTRICTED): `box/Restricted/<client_folder>/<matter_folder>/Correspondence/<file name>`
- Attachments of matter emails: extract each into the matter's `Documents/` folder (beside Correspondence) as `<YYYY-MM-DD>_<original attachment filename>`, using the email's date.
- Cross-reference stub: `<other matter>/Correspondence/<email file name>.xref.txt`, containing exactly one line: `Filed at: <box path of the primary copy>`
- needs_review → `box/_Needs_Review/`, firm_admin → `box/Firm_Admin/`, non_matter → `box/_Non_Matter/`, duplicate → `box/_Duplicates/`. Attachments of these are not extracted.

## 4. File name
`<YYYY-MM-DD>_<HHMM>_<sender last name>_<subject slug>.eml`
- Date and time: as written in the email's Date header (local time shown there).
- Sender last name: the last word of the sender's display name, lowercase, letters and digits only. If there is no display name, use the part of the address before @.
- Subject slug: remove leading `RE:`, `Re:`, `FW:`, `Fwd:` prefixes (any case, repeatedly). Lowercase it, replace every run of characters other than a-z and 0-9 with one hyphen, trim hyphens from both ends, and cut to 40 characters (then trim a trailing hyphen). If the result is empty, use `no-subject`.

## 5. Flags (the filing log lists every flag that applies, separated by ";", in this order)
- `hold`: filed in a matter under litigation hold, with a date on or after the hold start.
- `post-closing`: filed in a closed matter, dated after its closed date.
- `ethical-wall`: a person screened from a matter sent, received or was copied on an email about that matter (primary or cross-referenced), on or after the screen's start date.
- `potential-conflict`: the email shows that one client's interests are adverse to another current client, or that an adverse party wants to hire the firm.
- `new-matter-request`: asks for legal services outside every existing matter.
- `misdirected`: clearly intended for someone else.
- `phishing`: impersonates the firm or asks staff to enter credentials.
- `delivery-failure`: a bounce or non-delivery notice. File it in the matter of the original email.
- `restricted`: filed in a restricted matter.
- `duplicate-retained`: a duplicate kept under rule 6.
- `attorney-action`: the client asks for something the hold forbids (for example, deleting data).

## 6. Duplicates and litigation hold
- A duplicate (same Message-ID as an earlier email) goes to `box/_Duplicates/`.
- Exception: if the original is filed in a matter under litigation hold and the duplicate is dated on or after the hold start, keep it in the matter's Correspondence folder with `_dup` added before `.eml`, flags `hold;duplicate-retained`.
- Under hold, nothing may be deleted or left out.

## 7. Privilege (for matter emails; everything else is `n/a`)
- `AC`: between firm staff and the client (its people), about the matter.
- `WP`: internal, firm staff only, about the matter.
- `none`: anyone else takes part (opposing counsel, third parties, insurers, automated senders).

## 8. Ethical walls
Anyone screened from a matter must not receive or send anything about it. Each incident is one row in wall_incidents.csv. The ethics partner (Jonah Hartwell) must be told about every incident.
