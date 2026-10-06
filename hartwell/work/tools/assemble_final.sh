#!/bin/sh
# Mechanical: rebuild the final state from work/state into output/final and check it.
set -e
cd /home/user/repo/hartwell
python3 -I work/tools/round.py work/rounds/final_build
rm -rf output/final && mkdir -p output/final
cp -r work/rounds/final_build/box output/final/
cp work/rounds/final_build/*.csv work/rounds/final_build/*.md output/final/
cp work/state/memo_reply_0*.md output/final/
[ -f work/state/verification_log.md ] && cp work/state/verification_log.md output/final/ || true
[ -f work/state/changes_report.md ] && cp work/state/changes_report.md output/final/ || true
python3 -I tools/check_filing.py output/final | grep -v '^  check:'
