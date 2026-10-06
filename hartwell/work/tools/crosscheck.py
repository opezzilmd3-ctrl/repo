#!/usr/bin/env python3
"""Mechanical cross-file consistency checks between the report files of one output folder."""
import csv, re, sys, os
out = sys.argv[1]; bad = []
log = {r['email_file']: r for r in csv.DictReader(open(f'{out}/filing_log.csv'))}
nr = open(f'{out}/needs_review.md').read(); aa = open(f'{out}/attorney_actions.md').read(); tn = open(f'{out}/triage_notes.md').read()
# needs_review.md table rows == log needs_review set
table = set(re.findall(r'^\| \d+ \| (AAMk\w+\.eml) \|', nr, flags=re.M))
want = {f for f, r in log.items() if r['category'] == 'needs_review'}
if table != want: bad.append(f'needs_review.md table {sorted(table)} != log {sorted(want)}')
for f in want:
    if not re.search(r'^## \d+\. ' + re.escape(f), nr, flags=re.M): bad.append(f'needs_review.md: no section for {f}')
# attorney_actions.md covers every email carrying an action flag
ACT = {'post-closing', 'potential-conflict', 'new-matter-request', 'ethical-wall', 'delivery-failure', 'phishing', 'attorney-action', 'misdirected', 'declined-intake'}
for f, r in log.items():
    if ACT & set(r['flags'].split(';')) and f not in aa: bad.append(f'attorney_actions.md misses {f} ({r["flags"]})')
for f in want:
    if f not in aa: bad.append(f'attorney_actions.md misses needs_review {f}')
# wall incidents: every row's email is ethical-wall flagged and named in attorney_actions under the ethics partner
for w in csv.DictReader(open(f'{out}/wall_incidents.csv')):
    if 'ethical-wall' not in log[w['email_file']]['flags']: bad.append(f'wall row {w["email_file"]} without flag')
    ep = aa.split('## Jonah Hartwell – as ethics partner')[1].split('\n## ')[0]
    if w['email_file'] not in ep: bad.append(f'wall incident {w["email_file"]} not listed for the ethics partner')
# triage notes: one entry per email
for f in log:
    if not re.search(r'^### \d+\. ' + re.escape(f), tn, flags=re.M): bad.append(f'triage_notes.md has no entry for {f}')
if len(re.findall(r'^### \d+\. AAMk', tn, flags=re.M)) != 64: bad.append('triage_notes.md entry count != 64')
# every box_path in log text is mentioned with the right folder kind in needs_review (only _Needs_Review)
for f in want:
    if not log[f]['box_path'].startswith('box/_Needs_Review/'): bad.append(f'{f} needs_review not in _Needs_Review')
print(out, 'cross-file consistency:', 'OK' if not bad else 'PROBLEMS'); [print('  ', b) for b in bad]
