#!/usr/bin/env python3
"""Mechanical: rebuild a working output folder from work/state and run the checker on it.
usage: round.py <dest>"""
import sys, subprocess, shutil, os
dest = sys.argv[1]
subprocess.run([sys.executable, '-I', 'work/tools/build.py', 'mailbox', 'work/state/matters_effective.csv', 'work/state/decisions.csv',
                'work/state/config.json', dest], check=True)
for f in ('needs_review.md', 'attorney_actions.md', 'matters_effective.csv'): shutil.copy(os.path.join('work/state', f), dest)
with open(os.path.join(dest, 'triage_notes.md'), 'w') as o:
    o.write(open('output/phase1/triage_notes.md').read())
    if os.path.exists('work/state/triage_addendum.md'): o.write('\n' + open('work/state/triage_addendum.md').read())
r = subprocess.run([sys.executable, '-I', 'tools/check_filing.py', dest], capture_output=True, text=True)
print('\n'.join(l for l in r.stdout.splitlines() if not l.startswith('  check:'))); sys.exit(r.returncode)
