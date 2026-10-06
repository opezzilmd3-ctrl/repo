# Law-firm task: resubmission checklist

## Files in this package
| File | Use |
|---|---|
| `task_prompt_law.md` | The task prompt. Paste it into the form and into the self-test session. |
| `LAW_task_inputs_COMPLETE.zip` | The input archive (about 1.4 MB, 71 files plus INPUTS.md and MANIFEST.sha256). Upload it as the form attachment. |
| `count_steps.py` | Counts the steps after the self-test run. |
| `FORM_NOTES.md` | Text you can paste into the form fields. |

## 1. Self-test (fresh run)
1. Put the contents of `LAW_task_inputs_COMPLETE.zip` (not the zip itself) and `count_steps.py` in the root of the `law-task` repo. That folder must contain `mailbox/`, `matters.csv`, `staff.csv`, `filing_rules.md`, `memos/`, `INPUTS.md` and `MANIFEST.sha256`. Delete any `output/`, `tools/` or `trace/` folder left over from the previous run.
2. Start a **new** session at claude.ai/code on `law-task`.
3. Paste the whole of `task_prompt_law.md` and send nothing else. Don't step in until it finishes.
4. In the same session, send:
   > Please run the attached count_steps.py (python3 count_steps.py) to count the execution steps of this session and tell me the result. If the script says no session log was found, count the steps yourself following the rules it prints.
5. Take a screenshot of the reply that shows **Steps: N**. You need at least 50.
6. In the same session, send:
   > Copy this session's full log file (the .jsonl the script used) into a folder named trace/ in the repo, then commit and push it.

## 2. If the count is below 50
Don't add filler steps. Send the trace `.jsonl` for review. It shows where the run cut corners (sub-agents, batched scans, keyword scripts), and the prompt gets tightened at that point.

## 3. Form
- **Prompt:** the full text of `task_prompt_law.md`.
- **Attachment:** `LAW_task_inputs_COMPLETE.zip`. **Before you submit, check that it shows about 1.4 MB, not 0 bytes.**
- **Step count:** the number from the screenshot. Attach the screenshot if the form allows it.
- Use only the fictional data in the package. Don't use real client emails or reviews.
