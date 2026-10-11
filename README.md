# Jayam Info Official Resource Auto-Updater v2

## Included
- 466-record seed registry from Jayam Info master.
- 14 official discovery-source pages in `data/sources.json`.
- Weekly source change monitoring and candidate discovery.
- Monthly URL reachability observations.
- Append-only change log, candidate queue and URL check log.
- Searchable static website generator that publishes only records explicitly marked Verified Official.
- GitHub Pages deployment workflow.

## Setup needed (not running online yet)
1. Create a GitHub repository named `jayam-info-directory`.
2. Upload all ZIP contents to the repository root, including the hidden `.github` folder.
3. In Settings → Pages, select GitHub Actions as deployment source.
4. Open Actions and run the official source monitor manually.
5. Review `data/candidates.csv` and `data/change_log.csv`.
6. Run the deploy workflow once. The public website will include only strict verified records.

## Schedule
- Weekly source monitoring: Mondays 08:50 IST (`03:20 UTC`).
- Monthly URL reachability review: day 1 at 09:10 IST (`03:40 UTC`).
GitHub scheduled workflows can be delayed and require configuration; they are not guaranteed real-time triggers.

## Integrity rules
- A link discovered on a page is a candidate, not an approved resource.
- A successful HTTP response does not prove official ownership.
- One timeout, 403, 429 or 5xx is not proof a resource is dead.
- No script changes the official verification status automatically.
- The public website only shows records with an explicit verified-official status, including descriptive master statuses such as `Verified — official homepage` and `Verified — official service portal`. Source corroboration and direct homepage checks are distinct; the record status is retained in the generated data.
- Jayam Info must not claim government authorisation without formal authorisation.
- Existing 72-name gap from partially extracted IGOD categories remains a separate reconciliation task.

## Local run
```bash
pip install -r requirements.txt
python scripts/monitor_sources.py
python scripts/check_urls.py
python scripts/build_site.py
```
