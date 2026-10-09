# Final rework: what to upload

The review failed only because the wrong file was attached (a PNG screenshot) and no native session log was included. The task, the prompt and the self-test are fine: the self-test ran for 81 steps, and its results match the answer key.

## 1. Get the session log (the missing evidence)
Open the session **"Northfield product data reconciliation"** at claude.ai/code. It's waiting on a compliance question: answer it, or ignore it. Then send:

> Copy this session's full Claude Code log file (the session .jsonl under ~/.claude/projects/ that count_steps.py used) to trace/product_selftest_session.jsonl at the repo root, not inside product/. Then run `python3 count_steps.py trace/product_selftest_session.jsonl` and show me the output. Commit and push to branch claude/upbeat-cerf-vd59jf.

The output must show **Steps: 81**. Take a screenshot of it. Then download `trace/product_selftest_session.jsonl` from GitHub (the branch above, open the file, then the download button).

## 2. Upload to the form
| Field | What to put |
|---|---|
| Prompt | the full text of `submission/product/task_prompt_product.md` (unchanged) |
| **Input attachment** | **`submission/product/PRODUCT_task_inputs_COMPLETE.zip`**, about 0.7 MB. NOT a screenshot. |
| Trace / log | `product_selftest_session.jsonl` |
| Step evidence | the screenshot showing Steps: 81 |
| Notes | the text of `submission/product/FORM_NOTES.md` |

If the form has only one attachment slot, the input zip goes there. Send the .jsonl and the screenshot through the extra-files field, or reply to the reviewer's message with them.

## 3. Before you press submit
- The attachment's name ends in `.zip` and its size shows about 0.7 MB, not 0 bytes.
- Don't upload the answer key.
