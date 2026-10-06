# Form notes: product data reconciliation task

**Title:** Product data reconciliation across Sage 50, Shopify and Amazon UK, with API sync and go-live changes

**Response to the previous feedback:**
The earlier upload was a 0-byte file, so the agent never received the inputs. This resubmission attaches a non-empty, complete archive, PRODUCT_task_inputs_COMPLETE.zip (about 0.7 MB), containing every input the prompt names:
- the Excel-damaged Sage 50 export
- the Amazon All Listings and FBA inventory reports
- fba_fee_tiers.csv
- channel_rules.md
- the three scanned supplier price lists (image-only, one rotated)
- the mock Shopify/Amazon API server with its README
- the client_update/ files (email, stocktake, revised price-list scan, refreshed FBA report)

INPUTS.md and MANIFEST.sha256 list every file and its SHA-256 checksum. The archive was extracted into an empty folder and its inventory and openability were verified:
- every checksum matches, and no file is empty
- every scan opens as an image
- the mock server starts and serves both APIs

The task itself is unchanged. The prompt now begins with an input check, so the agent stops and reports if anything is missing. It also asks the agent to do the work itself in the session (no sub-agents) and to read each scan itself. No artificial steps were added. A fresh full-input self-test was then run with this package, and its complete main-model trace is kept.

**Self-test steps:** [fill in the number from count_steps.py]

**Data:** All people, companies, products, barcodes and addresses are fictional, and the .test domains are reserved.
