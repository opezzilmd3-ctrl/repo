# Form notes: law-firm email filing task

**Title:** Email filing migration from Outlook to Box for a law firm: 64 emails, conflicts, ethical walls and litigation hold

**Response to the previous feedback:**
The earlier upload was a 0-byte file, so the agent never received the inputs. This resubmission attaches the complete archive, LAW_task_inputs_COMPLETE.zip (about 1.4 MB). It holds 64 .eml emails with 24 PDF attachments (15 of them image-only scans), matters.csv, staff.csv, filing_rules.md and the four dated memos, plus INPUTS.md and MANIFEST.sha256 listing every file and its SHA-256 checksum. The archive was extracted into an empty folder and checked: every checksum matches, every email parses, every attachment opens, no file is empty, and no answer key is included. The prompt now starts with an input check, so the agent stops and reports if anything is missing instead of working around it. The task itself is unchanged. The prompt only requires the agent to do the work itself and in order: each email and scan is read, triage is recorded batch by batch, and each memo is applied and checked before the next. No artificial steps were added. A fresh full-input self-test was then run with the corrected prompt, and its complete main-model trace is kept.

**Self-test steps:** [fill in the number from count_steps.py]

**Background:** [optional: legal-ops / document-workflow experience, e.g. building review and filing automations in n8n]

**Data:** All people, clients, matters and addresses are fictional and use reserved .test domains.
