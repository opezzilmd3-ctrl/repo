#!/usr/bin/env python3
"""Print batch N (1-based, 8 per batch, Date order) in full: every header, body, attachment info + any text layer."""
import json, sys, subprocess, email, email.policy
rows = json.load(open(sys.argv[1])); n = int(sys.argv[2])
for i, r in enumerate(rows[(n-1)*8:n*8], start=(n-1)*8+1):
    print(f"################ #{i:02d} {r['file']}")
    m = email.message_from_binary_file(open('mailbox/'+r['file'], 'rb'), policy=email.policy.default)
    for k, v in m.items():
        if k.lower() not in ('content-transfer-encoding',): print(f"{k}: {v}")
    print('--- body ---'); print(r['body'].rstrip())
    for a in r['atts']:
        print(f"--- attachment: {a['name']} ({a['ctype']}, {a['bytes']} B, pages={a['pages']}, text_chars={a['text_chars']})")
        if a['text_chars']:
            print(subprocess.run(['pdftotext', '-layout', a['path'], '-'], capture_output=True, text=True).stdout.rstrip())
