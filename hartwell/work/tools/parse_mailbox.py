#!/usr/bin/env python3
"""Mechanical parse of mailbox/*.eml: headers, body text, attachments. No filing decisions."""
import email, email.policy, sys, json, os, subprocess
from email.utils import parsedate_to_datetime
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
rows = []
for fn in sorted(os.listdir(src)):
    p = os.path.join(src, fn)
    with open(p, 'rb') as f:
        m = email.message_from_binary_file(f, policy=email.policy.default)
    d = parsedate_to_datetime(m['Date'])
    body = m.get_body(preferencelist=('plain', 'html'))
    atts = []
    for part in m.iter_attachments():
        name = part.get_filename()
        data = part.get_payload(decode=True)
        ad = os.path.join(out, 'att', fn[:-4]); os.makedirs(ad, exist_ok=True)
        ap = os.path.join(ad, name)
        open(ap, 'wb').write(data)
        info = subprocess.run(['pdfinfo', ap], capture_output=True, text=True)
        txt = subprocess.run(['pdftotext', '-layout', ap, '-'], capture_output=True, text=True).stdout
        atts.append({'name': name, 'ctype': part.get_content_type(), 'bytes': len(data),
                     'pdfinfo_ok': info.returncode == 0,
                     'pages': next((l.split()[-1] for l in info.stdout.splitlines() if l.startswith('Pages')), None),
                     'text_chars': len(txt.strip()), 'path': ap})
    rows.append({'file': fn, 'date': d.isoformat(), 'from': str(m['From']), 'to': str(m['To'] or ''),
                 'cc': str(m['Cc'] or ''), 'subject': str(m['Subject'] or ''), 'msgid': str(m['Message-ID'] or ''),
                 'in_reply_to': str(m['In-Reply-To'] or ''), 'references': str(m['References'] or ''),
                 'body': body.get_content() if body else '', 'atts': atts,
                 'defects': [str(x) for x in m.defects]})
rows.sort(key=lambda r: r['date'])
json.dump(rows, open(os.path.join(out, 'parsed.json'), 'w'), indent=1)
print(len(rows), 'emails;', sum(len(r['atts']) for r in rows), 'attachments;',
      sum(1 for r in rows for a in r['atts'] if a['pdfinfo_ok']), 'open OK;',
      sum(1 for r in rows for a in r['atts'] if a['text_chars'] == 0), 'image-only (no text layer)')
for r in rows:
    if r['defects']: print('DEFECT', r['file'], r['defects'])
    for a in r['atts']:
        if not a['pdfinfo_ok'] or a['ctype'] != 'application/pdf': print('PROBLEM', r['file'], a)
