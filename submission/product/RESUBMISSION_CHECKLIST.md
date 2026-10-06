# Product reconciliation task: resubmission checklist

## Files
| File | Use |
|---|---|
| `submission/product/task_prompt_product.md` | The task prompt. Paste it into the form and into the self-test session. |
| `submission/product/PRODUCT_task_inputs_COMPLETE.zip` | The input archive (about 0.7 MB: 15 input files plus INPUTS.md and MANIFEST.sha256). Upload it as the form attachment. |
| `count_steps.py` (repo root) | Counts the steps after the self-test run. |
| `submission/product/FORM_NOTES.md` | Text you can paste into the form fields. |

The archive was extracted into an empty folder and checked:
- Every checksum matches, and no file is empty.
- The 4 scans open as images and have no text layer.
- The mock server starts from the extracted copy.
- A full reference run (phase 1 and the client update) completed with every Shopify change and every Amazon feed row accepted, and the live state matching.

The answer key is kept separately and is **not** in the repo or the zip.

## 1. Self-test (fresh run)
1. The `product/` folder of `opezzilmd3-ctrl/repo` (branch `claude/upbeat-cerf-vd59jf`) already holds the inputs. If an earlier run left `product/output/`, `product/sync/` or `product/mock_channels/data/state.json` behind, delete them first so the run starts from the client's original data.
2. Start a **new** session at claude.ai/code on `opezzilmd3-ctrl/repo`, on branch `claude/upbeat-cerf-vd59jf`.
3. Paste the whole of `task_prompt_product.md` and send nothing else. Don't step in until it finishes.
4. In the same session, send:
   > Please run the attached count_steps.py (python3 count_steps.py) to count the execution steps of this session and tell me the result. If the script says no session log was found, count the steps yourself following the rules it prints.
5. Take a screenshot of the reply showing **Steps: N**.
6. In the same session, send:
   > Copy this session's full log file (the .jsonl the script used) into a folder named trace/ in the repo, then commit and push it.

## 2. If the count is low
Don't add filler. Send the trace `.jsonl` for review. It shows exactly where the run cut corners.

## 3. Form
- **Prompt:** the full text of `task_prompt_product.md`.
- **Attachment:** `PRODUCT_task_inputs_COMPLETE.zip`. **Before submitting, check that it shows about 0.7 MB, not 0 bytes.**
- **Step count:** from the screenshot.
- The data is fully fictional. Don't add real client data.
