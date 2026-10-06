#!/usr/bin/env python3
"""Validate a filing output folder against filing_rules.md and the inputs.

usage: check_filing.py <output_dir> [--inputs DIR] [--matters CSV]

  <output_dir>  folder holding box/, filing_log.csv, wall_incidents.csv, privilege_log.csv, filing_summary.md
  --inputs      folder holding mailbox/, matters.csv, staff.csv (default: parent of this tools/ folder)
  --matters     matters CSV that states the facts in force for this output (default: <output_dir>/matters_effective.csv
                if present, else <inputs>/matters.csv). Memos can change facts (holds, walls, status, restriction);
                the effective file records them in the same columns as matters.csv.

Memo_02 (2026-09-29) amendment supported: declined intake emails are category firm_admin, privilege n/a, flag
declined-intake (in place of potential-conflict), filed in box/Firm_Admin/Declined_Intake/.

Exit code 0 = PASS, 1 = FAIL (every problem is listed)."""
import sys, os, re, csv, hashlib, argparse, email, email.policy
from email.utils import parsedate_to_datetime, getaddresses
from collections import Counter, defaultdict

FLAG_ORDER = ['hold', 'post-closing', 'ethical-wall', 'potential-conflict', 'declined-intake', 'new-matter-request', 'misdirected',
              'phishing', 'delivery-failure', 'restricted', 'duplicate-retained', 'attorney-action']
CATS = ['matter', 'needs_review', 'firm_admin', 'non_matter', 'duplicate']
SPECIAL = {'needs_review': '_Needs_Review', 'firm_admin': 'Firm_Admin', 'non_matter': '_Non_Matter', 'duplicate': '_Duplicates'}
LOG_COLS = ['email_file', 'received', 'sender', 'subject', 'category', 'primary_matter', 'xref_matters', 'privilege',
            'flags', 'box_path', 'attachments_saved']
FIRM = '@hartwell-osei.test'

ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('--inputs'); ap.add_argument('--matters')
a = ap.parse_args()
OUT = a.out.rstrip('/')
INP = a.inputs or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAT = a.matters or (os.path.join(OUT, 'matters_effective.csv') if os.path.exists(os.path.join(OUT, 'matters_effective.csv'))
                    else os.path.join(INP, 'matters.csv'))
errors, checks = [], []
def err(check, msg): errors.append(f'[{check}] {msg}')
def section(name): checks.append(name)
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()

# ---------- facts from inputs ----------
matters = {m['matter_no']: m for m in csv.DictReader(open(MAT, encoding='utf-8'))}
staff = {s['name']: s['email'].lower() for s in csv.DictReader(open(os.path.join(INP, 'staff.csv'), encoding='utf-8'))}
def restricted(mno): return 'RESTRICTED' in matters[mno]['notes']
def hold_start(mno):
    m = re.search(r'Litigation hold from (\d{4}-\d{2}-\d{2})', matters[mno]['notes']); return m.group(1) if m else None
def walls(mno):
    return [(n, staff[n], d) for n, d in re.findall(r'ETHICAL WALL: (.+?) is screened from this matter \(since (\d{4}-\d{2}-\d{2})\)', matters[mno]['notes'])]
def mdir(mno):
    m = matters[mno]; return f"box/{'Restricted' if restricted(mno) else 'Clients'}/{m['client_folder']}/{m['matter_folder']}"

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
    return re.sub(r'[^a-z0-9]', '', (name.split()[-1] if name.strip() else addr.split('@')[0]).lower())

MB = os.path.join(INP, 'mailbox')
src = {}
for fn in sorted(os.listdir(MB)):
    p = os.path.join(MB, fn)
    m = email.message_from_binary_file(open(p, 'rb'), policy=email.policy.default)
    dt = parsedate_to_datetime(m['Date'])
    parts = [(addr.lower(), role) for role, h in (('sender', 'From'), ('to', 'To'), ('cc', 'Cc'))
             for _, addr in getaddresses([str(m[h] or '')]) if addr]
    src[fn] = dict(m=m, dt=dt, sha=sha(p), msgid=str(m['Message-ID']).strip(), parts=parts,
                   name=f"{dt:%Y-%m-%d}_{dt:%H%M}_{lastname(str(m['From']))}_{slug(str(m['Subject'] or ''))}.eml",
                   atts=[(pt.get_filename(), hashlib.sha256(pt.get_payload(decode=True)).hexdigest()) for pt in m.iter_attachments()])

# ---------- 1. filing log ----------
section('filing_log.csv: columns, one row per mailbox email')
rows = list(csv.DictReader(open(os.path.join(OUT, 'filing_log.csv'), encoding='utf-8')))
if rows and list(rows[0].keys()) != LOG_COLS: err('log', f'columns {list(rows[0].keys())} != {LOG_COLS}')
cnt = Counter(r['email_file'] for r in rows)
for fn in src:
    if cnt[fn] != 1: err('log', f'{fn} appears {cnt[fn]} times in filing_log.csv (must be exactly 1)')
for fn in cnt:
    if fn not in src: err('log', f'{fn} in filing_log.csv is not a mailbox email')
if len(rows) != len(src): err('log', f'{len(rows)} rows, mailbox has {len(src)} emails')
log = {r['email_file']: r for r in rows if r['email_file'] in src}
for fn, r in log.items():
    s = src[fn]
    if r['received'] != f"{s['dt']:%Y-%m-%d %H:%M}": err('log', f"{fn}: received {r['received']} != Date header {s['dt']:%Y-%m-%d %H:%M}")
    if r['subject'] != str(s['m']['Subject'] or ''): err('log', f'{fn}: subject differs from header')
    if r['category'] not in CATS: err('log', f"{fn}: unknown category {r['category']}")
    if r['primary_matter'] and r['primary_matter'] not in matters: err('log', f"{fn}: unknown matter {r['primary_matter']}")

# ---------- 2. primary copies: every box_path exists, every email exactly once ----------
section('box: every box_path exists, byte-identical to the mailbox original, each email exactly once as primary copy, no extra files')
box_files = set()
for root, _, fs in os.walk(os.path.join(OUT, 'box')):
    for f in fs: box_files.add(os.path.relpath(os.path.join(root, f), OUT).replace(os.sep, '/'))
emls = {p for p in box_files if p.endswith('.eml')}
logged = {}
for fn, r in log.items():
    p = r['box_path']
    if p not in box_files: err('primary', f'{fn}: box_path does not exist: {p}'); continue
    if sha(os.path.join(OUT, p)) != src[fn]['sha']: err('primary', f'{fn}: {p} is not a byte-identical copy of the original')
    if p in logged: err('primary', f'{fn} and {logged[p]} share box_path {p}')
    logged[p] = fn
for p in sorted(emls - set(logged)): err('primary', f'extra .eml in box not in filing log: {p}')
by_sha = Counter(sha(os.path.join(OUT, p)) for p in emls)
for fn, s in src.items():
    others = [o for o, t in src.items() if t['sha'] == s['sha']]
    if by_sha[s['sha']] != len(others): err('primary', f'{fn}: content found {by_sha[s["sha"]]} times in box (expected {len(others)})')

# ---------- 3. file names and folder placement ----------
section('names: <YYYY-MM-DD>_<HHMM>_<lastname>_<slug>.eml (+_dup for hold-retained duplicates); category → folder')
for fn, r in log.items():
    p, s = r['box_path'], src[fn]
    flags = [f for f in r['flags'].split(';') if f]
    exp = s['name'][:-4] + '_dup.eml' if 'duplicate-retained' in flags else s['name']
    if os.path.basename(p) != exp: err('name', f'{fn}: file name {os.path.basename(p)!r} != expected {exp!r}')
    cat, pm = r['category'], r['primary_matter']
    if cat == 'matter' or (cat == 'duplicate' and 'duplicate-retained' in flags):
        if not pm: err('folder', f'{fn}: {cat} without primary_matter'); continue
        if os.path.dirname(p) != mdir(pm) + '/Correspondence': err('folder', f'{fn}: {p} not in {mdir(pm)}/Correspondence')
    else:
        if pm: err('folder', f'{fn}: category {cat} must not carry primary_matter {pm}')
        want_dir = 'box/Firm_Admin/Declined_Intake' if 'declined-intake' in flags else 'box/' + SPECIAL[cat]
        if 'declined-intake' in flags and cat != 'firm_admin': err('folder', f'{fn}: declined-intake must be category firm_admin, got {cat}')
        if os.path.dirname(p) != want_dir: err('folder', f'{fn}: {cat} must be in {want_dir}/, got {p}')
for f in box_files:
    parts = f.split('/')
    if parts[1] in ('Clients', 'Restricted'):
        if len(parts) != 6 or parts[4] not in ('Correspondence', 'Documents'): err('folder', f'file outside a matter Correspondence/Documents folder: {f}')
    elif parts[1] == 'Firm_Admin' and len(parts) == 4 and parts[2] == 'Declined_Intake' and f.endswith('.eml'):
        pass
    elif parts[1] in SPECIAL.values():
        if len(parts) != 3 or not f.endswith('.eml'): err('folder', f'unexpected file in special folder: {f}')
    else: err('folder', f'file in unknown box location: {f}')

# ---------- 4. restricted ----------
section('restricted matters only under box/Restricted/, nothing else there; restricted flag')
for f in box_files:
    parts = f.split('/')
    if parts[1] not in ('Clients', 'Restricted') or len(parts) < 4: continue
    hit = [k for k, m in matters.items() if m['client_folder'] == parts[2] and m['matter_folder'] == parts[3]]
    if not hit: err('restricted', f'folder is not a matter in matters.csv: {"/".join(parts[:4])}'); continue
    if restricted(hit[0]) and parts[1] != 'Restricted': err('restricted', f'restricted matter {hit[0]} content outside box/Restricted: {f}')
    if not restricted(hit[0]) and parts[1] == 'Restricted': err('restricted', f'non-restricted matter {hit[0]} under box/Restricted: {f}')
for fn, r in log.items():
    pm = r['primary_matter']; has = 'restricted' in r['flags'].split(';')
    if pm and restricted(pm) != has: err('restricted', f'{fn}: restricted flag {has} but matter {pm} restricted={restricted(pm)}')
    if not pm and has: err('restricted', f'{fn}: restricted flag on a non-matter email')

# ---------- 5. stubs ----------
section('cross-reference stubs: one line "Filed at: <path>", path exists, same client, matches xref_matters')
stubs = {p for p in box_files if p.endswith('.xref.txt')}
expected_stubs = {}
for fn, r in log.items():
    for x in [x for x in r['xref_matters'].split(';') if x]:
        if x not in matters: err('stub', f'{fn}: unknown xref matter {x}'); continue
        if not r['primary_matter']: err('stub', f'{fn}: xref without primary matter'); continue
        if x == r['primary_matter']: err('stub', f'{fn}: xref equals primary matter')
        if matters[x]['client_no'] != matters[r['primary_matter']]['client_no']:
            err('stub', f'{fn}: xref {x} is a different client from {r["primary_matter"]} (forbidden by rule 2)')
        expected_stubs[f"{mdir(x)}/Correspondence/{os.path.basename(r['box_path'])}.xref.txt"] = (fn, r['box_path'])
for p in sorted(stubs):
    lines = open(os.path.join(OUT, p), encoding='utf-8').read().splitlines()
    if len(lines) != 1 or not lines[0].startswith('Filed at: '): err('stub', f'{p}: must contain exactly one line "Filed at: <path>", got {lines!r}'); continue
    target = lines[0][len('Filed at: '):]
    if target not in box_files: err('stub', f'{p}: Filed at path does not exist: {target}')
    sp, tp = p.split('/'), target.split('/')
    if len(tp) > 2 and sp[2] != tp[2]: err('stub', f'{p}: crosses clients ({sp[2]} → {tp[2]})')
    if p not in expected_stubs: err('stub', f'{p}: stub not backed by any xref_matters entry in the log'); continue
    if target != expected_stubs[p][1]: err('stub', f'{p}: points to {target}, primary copy is {expected_stubs[p][1]}')
for p in sorted(set(expected_stubs) - stubs): err('stub', f'missing stub {p} for {expected_stubs[p][0]}')

# ---------- 6. attachments ----------
section('attachments: matter emails → Documents/<YYYY-MM-DD>_<original name>, byte-identical; none for other categories')
expected_docs = {}
for fn, r in log.items():
    s = src[fn]; saved = [x for x in r['attachments_saved'].split(';') if x]
    if r['primary_matter']:
        exp = [f"{mdir(r['primary_matter'])}/Documents/{s['dt']:%Y-%m-%d}_{n}" for n, _ in s['atts']]
        for (n, h), e in zip(s['atts'], exp):
            if e in expected_docs: err('attach', f'{fn}: attachment path collision {e}')
            expected_docs[e] = (fn, h)
        if sorted(saved) != sorted(exp): err('attach', f'{fn}: attachments_saved {saved} != expected {exp}')
    elif saved: err('attach', f'{fn}: category {r["category"]} must not have extracted attachments')
docs = {p for p in box_files if '/Documents/' in p}
for p in sorted(docs):
    if p not in expected_docs: err('attach', f'unexpected or misnamed file in Documents: {p}')
    elif sha(os.path.join(OUT, p)) != expected_docs[p][1]: err('attach', f'{p}: content differs from the attachment of {expected_docs[p][0]}')
for p in sorted(set(expected_docs) - docs): err('attach', f'missing extracted attachment {p} (from {expected_docs[p][0]})')

# ---------- 7. duplicates and hold ----------
section('duplicates (Message-ID) and litigation hold: retained duplicates, hold flag')
first = {}
for fn in sorted(src, key=lambda f: (src[f]['dt'], f)):
    mid = src[fn]['msgid']
    if mid in first:
        orig = first[mid]; r, ro = log.get(fn), log.get(orig)
        if not r or not ro: continue
        if r['category'] != 'duplicate': err('dup', f'{fn}: same Message-ID as {orig} but category {r["category"]}')
        om = ro['primary_matter']; hs = hold_start(om) if om else None
        must_retain = bool(hs) and f"{src[fn]['dt']:%Y-%m-%d}" >= hs
        fl = r['flags'].split(';')
        if must_retain:
            if r['primary_matter'] != om or not r['box_path'].endswith('_dup.eml') or not ('hold' in fl and 'duplicate-retained' in fl):
                err('dup', f'{fn}: duplicate of {orig} under hold must be retained in {om} Correspondence as _dup with hold;duplicate-retained')
        elif os.path.dirname(r['box_path']) != 'box/_Duplicates': err('dup', f'{fn}: duplicate of {orig} must go to box/_Duplicates/')
    else:
        first[mid] = fn
        if log.get(fn, {}).get('category') == 'duplicate': err('dup', f'{fn}: category duplicate but no earlier email has its Message-ID')
for fn, r in log.items():
    pm = r['primary_matter']; hs = hold_start(pm) if pm else None
    want = bool(hs) and f"{src[fn]['dt']:%Y-%m-%d}" >= hs
    if want != ('hold' in r['flags'].split(';')): err('hold', f'{fn}: hold flag should be {want} (matter {pm or "-"}, hold start {hs})')

# ---------- 8. flags: vocabulary, order, closed matters, walls ----------
section('flags: vocabulary and order; post-closing; ethical wall + wall_incidents.csv')
exp_walls = set()
for fn, r in log.items():
    fl = [f for f in r['flags'].split(';') if f]
    for f in fl:
        if f not in FLAG_ORDER: err('flags', f'{fn}: unknown flag {f}')
    if [f for f in fl if f in FLAG_ORDER] != sorted([f for f in fl if f in FLAG_ORDER], key=FLAG_ORDER.index) or len(set(fl)) != len(fl):
        err('flags', f'{fn}: flags not in rule-5 order or repeated: {r["flags"]}')
    pm = r['primary_matter']; d = f"{src[fn]['dt']:%Y-%m-%d}"
    if pm:
        m = matters[pm]
        want = m['status'] == 'closed' and bool(m['closed_date']) and d > m['closed_date']
        if want != ('post-closing' in fl): err('flags', f'{fn}: post-closing should be {want} ({pm} {m["status"]} {m["closed_date"]})')
    elif 'post-closing' in fl: err('flags', f'{fn}: post-closing on a non-matter email')
    if ('duplicate-retained' in fl) != (r['category'] == 'duplicate' and bool(pm)): err('flags', f'{fn}: duplicate-retained inconsistent')
    if 'delivery-failure' in fl and r['category'] == 'matter' and not pm: err('flags', f'{fn}: bounce must be filed in the original email matter')
    wall_hit = False
    for x in ([pm] if pm else []) + [x for x in r['xref_matters'].split(';') if x]:
        for person, addr, since in walls(x):
            for paddr, role in src[fn]['parts']:
                if paddr == addr and d >= since:
                    exp_walls.add((fn, person, role, x)); wall_hit = True
    if wall_hit != ('ethical-wall' in fl): err('wall', f'{fn}: ethical-wall flag should be {wall_hit}')
wi = list(csv.DictReader(open(os.path.join(OUT, 'wall_incidents.csv'), encoding='utf-8')))
if wi and list(wi[0].keys()) != ['email_file', 'received', 'screened_person', 'role', 'matter', 'action']: err('wall', 'wall_incidents.csv columns wrong')
got = Counter((w['email_file'], w['screened_person'], w['role'], w['matter']) for w in wi)
for k in exp_walls - set(got): err('wall', f'missing wall incident {k}')
for k in set(got) - exp_walls: err('wall', f'wall incident not supported by headers/matters: {k}')
for k, n in got.items():
    if n > 1: err('wall', f'wall incident listed {n} times: {k}')
for w in wi:
    if w['email_file'] in log and w['received'] != log[w['email_file']]['received']: err('wall', f'{w["email_file"]}: received mismatch')
    if not w['action'].strip(): err('wall', f'{w["email_file"]}: empty action')

# ---------- 9. privilege ----------
section('privilege values; privilege_log.csv = every 1001-001 email with AC/WP')
for fn, r in log.items():
    pv, pm = r['privilege'], r['primary_matter']
    if not pm:
        if pv != 'n/a': err('priv', f'{fn}: {r["category"]} must have privilege n/a, got {pv}')
        continue
    if pv not in ('AC', 'WP', 'none'): err('priv', f'{fn}: matter email privilege must be AC/WP/none, got {pv}'); continue
    addrs = {p for p, _ in src[fn]['parts']}
    firm = {p for p in addrs if p.endswith(FIRM)}
    if pv == 'WP' and firm != addrs: err('priv', f'{fn}: WP but non-firm participants {sorted(addrs - firm)}')
    if firm == addrs and pv != 'WP' and not any(p.startswith('mailer-daemon') for p in addrs): err('priv', f'{fn}: firm-only email must be WP, got {pv}')
    if pv == 'AC' and not firm: err('priv', f'{fn}: AC but no firm participant')
pl = list(csv.DictReader(open(os.path.join(OUT, 'privilege_log.csv'), encoding='utf-8')))
if pl and list(pl[0].keys()) != ['date', 'from', 'to', 'cc', 'subject', 'privilege', 'description']: err('priv', 'privilege_log.csv columns wrong')
hold_matters = [k for k in matters if hold_start(k)]
exp_pl = Counter((r['received'][:10], r['subject'], r['privilege']) for r in log.values()
                 if r['primary_matter'] in hold_matters and r['privilege'] in ('AC', 'WP'))
got_pl = Counter((p['date'], p['subject'], p['privilege']) for p in pl)
for k in exp_pl - got_pl: err('priv', f'privilege log missing {k}')
for k in got_pl - exp_pl: err('priv', f'privilege log has unexpected {k}')
for p in pl:
    if not p['description'].strip(): err('priv', f'privilege log entry {p["subject"]!r} has no description')

# ---------- 10. summary counts ----------
section('filing_summary.md counts match filing_log.csv and box/')
summ = open(os.path.join(OUT, 'filing_summary.md'), encoding='utf-8').read()
def table_val(key):
    m = re.findall(r'^\|\s*' + re.escape(key) + r'\s*\|(?:[^|\n]*\|)*?\s*(\d+)\s*\|\s*$', summ, flags=re.M)
    return [int(x) for x in m]
cats = Counter(r['category'] for r in log.values())
for c in CATS:
    v = table_val(c)
    if not v or v[0] != cats.get(c, 0): err('summary', f'category {c}: summary {v[:1]} != log {cats.get(c, 0)}')
bym = Counter(r['primary_matter'] for r in log.values() if r['primary_matter'])
for k in matters:
    v = table_val(k)
    if not v or v[0] != bym.get(k, 0): err('summary', f'matter {k}: summary {v[:1]} != log {bym.get(k, 0)}')
bya = Counter(matters[r['primary_matter']]['responsible_attorney'] for r in log.values() if r['primary_matter'])
for att in set(m['responsible_attorney'] for m in matters.values()):
    v = table_val(att)
    if not v or v[0] != bya.get(att, 0): err('summary', f'attorney {att}: summary {v[:1]} != log {bya.get(att, 0)}')
v = table_val('**total files in box/**')
if not v or v[0] != len(box_files): err('summary', f'files in box: summary {v[:1]} != actual {len(box_files)}')
for label, n in (('email copies (.eml)', len(emls)), ('cross-reference stubs (.xref.txt)', len(stubs)), ('extracted attachments (Documents/)', len(docs))):
    v = table_val(label)
    if not v or v[0] != n: err('summary', f'{label}: summary {v[:1]} != actual {n}')
fl = Counter(f for r in log.values() for f in r['flags'].split(';') if f)
for f in FLAG_ORDER:
    v = table_val(f)
    if v and v[0] != fl.get(f, 0): err('summary', f'flag {f}: summary {v[0]} != log {fl.get(f, 0)}')
m = re.search(r'Wall incidents: (\d+)\. Privilege log entries: (\d+)\.', summ)
if not m or (int(m.group(1)), int(m.group(2))) != (len(wi), len(pl)): err('summary', f'wall/privilege counts line wrong (actual {len(wi)}/{len(pl)})')

# ---------- report ----------
print(f'check_filing.py  output={OUT}  matters={MAT}')
print(f'emails={len(src)} log_rows={len(rows)} box_files={len(box_files)} (eml={len(emls)} stubs={len(stubs)} documents={len(docs)}) '
      f'wall_incidents={len(wi)} privilege_log={len(pl)}')
for c in checks: print('  check:', c)
if errors:
    print(f'FAIL – {len(errors)} problem(s):')
    for e in errors: print('  ' + e)
    sys.exit(1)
print('PASS – all checks clean')
