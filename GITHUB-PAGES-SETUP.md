# Hourly updates on your actual GitHub Pages website

Website: https://deepaksdamcrc.github.io/sarkariupdate/
Repository: deepaksdamcrc/sarkariupdate, branch main, Pages source `/`.

The connected hourly editorial task independently writes Hindi updates, uses official information when it conflicts with the discovery report, and holds unresolved claims as private approval drafts. In the same run it copies the resulting published feed into this repository. GitHub Pages builds the updated main branch. Source-site credentials and the GitHub connection are acquired fresh by the cloud task; no repository Actions secret or separate Actions workflow is needed.

The public website reads `data/articles.json` relative to the project URL instead of an old hardcoded ZIP snapshot. Only published articles and locally generated covers reach the public site. Drafts, reference-site backlinks, provenance, passwords and sessions are excluded. Source sync is read-only and never changes the admin account.

## Instructions for the linked hourly task

After updating or checking the editorial feed, always mirror it here, even when the editorial check found no new items (a prior mirror run might have failed).

1. Use the connected GitHub account to open a fresh checkout of `deepaksdamcrc/sarkariupdate`, main. Preserve unrelated files and never force-push.
2. Get the linked editorial Site `appgprj_6afa85503c6881918a71cc61a89c6d19` using Sites `get_site`. Use only its returned current_live_url and siwc_bypass_bearer_token; do not generate/rotate credentials.
3. Run `python3 scripts/publish-pages.py --push` from the checkout. Through hidden stdin or an in-memory pipe, send one JSON object with `source_url` and `service_token`. Never put the token in command arguments, files, logs, source or the task prompt. Git uses the task's existing authenticated GitHub connection, not the source token.
4. The script reads only published articles, produces local illustrations, updates index.html/data/covers/export, and pushes only when public content changed. It never exports admin data and follows no source redirects. On a non-fast-forward rejection, fetch a clean current main and reapply once; do not force-push.
5. Check the GitHub Pages branch build and the live `data/articles.json` (allow normal deployment delay); compare IDs/content with the source feed. Do not claim live success until readback matches. Report an access/deployment blocker if it cannot complete. Routine successful updates require no user approval or success message; only unresolved editorial doubts need approval.

Pause/resume the linked task to stop/resume hourly checks. Existing admin-side publishing pause also blocks mirroring, so drafts or paused content are not newly published accidentally. Existing administrator management stays on its protected backend; GitHub Pages itself cannot execute the username/password backend.

## Local verification

`python3 -m unittest discover -s tests`

`python3 scripts/sync-pages.py --input export/published-articles.json --output _site`

`python3 -m http.server --directory _site 8000`

GitHub Pages serves the branch's current public files. Worker source files retained from the user's ZIP are backend source, not a running admin service on GitHub Pages. The current article snapshot is updated in `export/published-articles.json`; an old downloaded ZIP does not update itself.
