#!/usr/bin/env python3
"""Mechanical builder. Reads MY recorded decisions (decisions CSV) and hand-written text
(config JSON: privilege-log descriptions, wall-incident actions, walls/holds facts, open issues)
and produces box/, filing_log.csv, wall_incidents.csv, privilege_log.csv and the count tables
of filing_summary.md. It assigns NO categories, matters, flags or privilege itself.
usage: build.py <mailbox_dir> <matters.csv> <decisions.csv> <config.json> <out_dir>"""
import sys, os, re, csv, json, shutil, email, email.policy
from email.utils import parsedate_to_datetime, getaddresses
from collections import Counter, OrderedDict

mailbox, matters_csv, dec_csv, cfg_json, out = sys.argv[1:6]
cfg = json.load(open(cfg_json))
matters = OrderedDict((m['matter_no'], m) for m in csv.DictReader(open(matters_csv, encoding='utf-8')))
decs = list(csv.DictReader(open(dec_csv, encoding='utf-8'), delimiter='|'))
FLAG_ORDER = ['hold', 'post-closing', 'ethical-wall', 'potential-conflict', 'declined-intake', 'new-matter-request', 'misdirected',
              'phishing', 'delivery-failure', 'restricted', 'duplicate-retained', 'attorney-action']
SPECIAL = {'needs_review': '_Needs_Review', 'firm_admin': 'Firm_Admin', 'non_matter': '_Non_Matter', 'duplicate': '_Duplicates'}

def is_restricted(mno): return 'RESTRICTED' in matters[mno]['notes']
def matter_dir(mno):
    m = matters[mno]
    return os.path.join('box', 'Restricted' if is_restricted(mno) else 'Clients', m['client_folder'], m['matter_folder'])

def slug(subject):
    s = subject.strip()
    while True:
        n = re.sub(r'^(re|fw|fwd)\s*:\s*', '', s, flags=re.I)
        if n == s: break
        s = n
    s = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:40].rstrip('-')
    return s or 'no-subject'

def lastname(from_hdr):
    name, addr = getaddresses([from_hdr])[0]
    base = name.split()[-1] if name.strip() else addr.split('@')[0]
    return re.sub(r'[^a-z0-9]', '', base.lower())

def load(fn):
    with open(os.path.join(mailbox, fn), 'rb') as f:
        return email.message_from_binary_file(f, policy=email.policy.default)

def fmt_people(h):
    return '; '.join(f'{n} <{a}>' if n else a for n, a in getaddresses([h])) if h else ''

if os.path.exists(out): shutil.rmtree(out)
os.makedirs(out)
for mno in matters:
    for sub in ('Correspondence', 'Documents'): os.makedirs(os.path.join(out, matter_dir(mno), sub), exist_ok=True)
for d in SPECIAL.values(): os.makedirs(os.path.join(out, 'box', d), exist_ok=True)

log, priv, walls = [], [], []
for d in decs:
    fn = d['email_file']; m = load(fn)
    dt = parsedate_to_datetime(m['Date'])
    flags = [f for f in d['flags'].split(';') if f]
    assert all(f in FLAG_ORDER for f in flags), (fn, flags)
    flags = sorted(set(flags), key=FLAG_ORDER.index)
    name = f"{dt:%Y-%m-%d}_{dt:%H%M}_{lastname(str(m['From']))}_{slug(str(m['Subject'] or ''))}.eml"
    cat, pm = d['category'], d['primary_matter']
    xrefs = [x for x in d['xref_matters'].split(';') if x]
    in_matter = bool(pm)  # matter emails and hold-retained duplicates
    if cat == 'duplicate' and in_matter:
        assert 'duplicate-retained' in flags
        name = name[:-4] + '_dup.eml'
    folder = os.path.join(matter_dir(pm), 'Correspondence') if in_matter else os.path.join('box', SPECIAL[cat])
    if 'declined-intake' in flags:  # memo_02: declined intake emails → box/Firm_Admin/Declined_Intake/
        assert cat == 'firm_admin' and not in_matter; folder = os.path.join('box', 'Firm_Admin', 'Declined_Intake')
    box_path = os.path.join(folder, name)
    dst = os.path.join(out, box_path); os.makedirs(os.path.dirname(dst), exist_ok=True)
    assert not os.path.exists(dst), ('name collision', dst)
    shutil.copyfile(os.path.join(mailbox, fn), dst)
    saved = []
    if in_matter:
        for part in m.iter_attachments():
            an = f"{dt:%Y-%m-%d}_{part.get_filename()}"
            ap = os.path.join(matter_dir(pm), 'Documents', an)
            assert not os.path.exists(os.path.join(out, ap)), ('attachment collision', ap)
            open(os.path.join(out, ap), 'wb').write(part.get_payload(decode=True))
            saved.append(ap)
    for x in xrefs:
        assert matters[x]['client_no'] == matters[pm]['client_no'], ('cross-client stub forbidden', fn, x)
        sp = os.path.join(out, matter_dir(x), 'Correspondence', name + '.xref.txt')
        open(sp, 'w').write(f'Filed at: {box_path}\n')
    row = OrderedDict(email_file=fn, received=f'{dt:%Y-%m-%d %H:%M}', sender=fmt_people(str(m['From'])),
                      subject=str(m['Subject'] or ''), category=cat, primary_matter=pm, xref_matters=';'.join(xrefs),
                      privilege=d['privilege'], flags=';'.join(flags), box_path=box_path, attachments_saved=';'.join(saved))
    log.append(row)
    # privilege log: every email filed in 1001-001 with AC or WP
    if pm == cfg['privilege_log_matter'] and d['privilege'] in ('AC', 'WP'):
        assert fn in cfg['privilege_descriptions'], ('missing privilege description', fn)
        priv.append(OrderedDict(date=f'{dt:%Y-%m-%d}', **{'from': fmt_people(str(m['From']))}, to=fmt_people(str(m['To'] or '')),
                                cc=fmt_people(str(m['Cc'] or '')), subject=str(m['Subject'] or ''), privilege=d['privilege'],
                                description=cfg['privilege_descriptions'][fn]))
    # wall incidents: one row per screened person per role on an ethical-wall email about the walled matter
    if 'ethical-wall' in flags:
        n = 0
        for w in cfg['walls']:
            if w['matter'] not in [pm] + xrefs or f"{dt:%Y-%m-%d}" < w['since']: continue
            for role, hdr in (('sender', 'From'), ('to', 'To'), ('cc', 'Cc')):
                if any(a.lower() == w['email'] for _, a in getaddresses([str(m[hdr] or '')])):
                    walls.append(OrderedDict(email_file=fn, received=row['received'], screened_person=w['person'], role=role,
                                             matter=w['matter'], action=cfg['wall_actions'][fn])); n += 1
        assert n, ('ethical-wall flag without a screened participant', fn)

def wcsv(path, rows, cols):
    with open(os.path.join(out, path), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
wcsv('filing_log.csv', log, list(log[0].keys()))
wcsv('wall_incidents.csv', walls, ['email_file', 'received', 'screened_person', 'role', 'matter', 'action'])
wcsv('privilege_log.csv', priv, ['date', 'from', 'to', 'cc', 'subject', 'privilege', 'description'])

# filing_summary.md: count tables computed from the log + hand-written open issues
cats = Counter(r['category'] for r in log)
bym = Counter(r['primary_matter'] for r in log if r['primary_matter'])
bya = Counter(matters[r['primary_matter']]['responsible_attorney'] for r in log if r['primary_matter'])
nfiles = sum(len(fs) for _, _, fs in os.walk(os.path.join(out, 'box')))
L = [f"# Filing summary – {cfg['phase_title']}", '', f"Emails in mailbox: {len(log)}. Every email is filed exactly once as a primary copy.", '',
     '## Counts by category', '', '| category | count |', '|---|---|']
L += [f'| {c} | {cats.get(c, 0)} |' for c in ['matter', 'needs_review', 'firm_admin', 'non_matter', 'duplicate']]
L += [f'| **total** | {len(log)} |', '', '## Counts by primary matter (emails whose primary copy is in a matter folder, including hold-retained duplicates)', '',
      '| matter | matter folder | responsible attorney | status | count |', '|---|---|---|---|---|']
for mno, m in matters.items():
    L.append(f"| {mno} | {m['matter_folder']} | {m['responsible_attorney']} | {m['status']} | {bym.get(mno, 0)} |")
L += [f'| **total** | | | | {sum(bym.values())} |', '', '## Counts by responsible attorney (primary matter)', '', '| attorney | count |', '|---|---|']
for a in sorted(set(m['responsible_attorney'] for m in matters.values())): L.append(f'| {a} | {bya.get(a, 0)} |')
L += [f'| **total** | {sum(bya.values())} |', '']
stubs = sum(1 for r in log for x in r['xref_matters'].split(';') if x)
atts = sum(1 for r in log for x in r['attachments_saved'].split(';') if x)
L += ['## Files in box/', '', f'| item | count |', '|---|---|', f'| email copies (.eml) | {len(log)} |', f'| cross-reference stubs (.xref.txt) | {stubs} |',
      f'| extracted attachments (Documents/) | {atts} |', f'| **total files in box/** | {nfiles} |', '',
      '## Flags', '', '| flag | emails |', '|---|---|']
fl = Counter(f for r in log for f in r['flags'].split(';') if f)
L += [f'| {f} | {fl.get(f, 0)} |' for f in FLAG_ORDER]
L += ['', f'Wall incidents: {len(walls)}. Privilege log entries: {len(priv)}.', '', '## Open issues', '']
L += [f'{i}. {t}' for i, t in enumerate(cfg['open_issues'], 1)]
open(os.path.join(out, 'filing_summary.md'), 'w').write('\n'.join(L) + '\n')
print(f'built {out}: {len(log)} emails, {nfiles} files in box, {len(walls)} wall rows, {len(priv)} privilege rows, cats={dict(cats)}')
