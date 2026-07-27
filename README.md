# AutoJob

**Modern, cross-platform Python GUI job scraper focused on Australian (SEQ / Brisbane) opportunities.**

Built with CustomTkinter for a clean, tabbed interface. Supports API sources + authenticated browser sessions for major Australian boards, resume-based matching, Excel export, and light company OSINT.

> **Important**: Respect website Terms of Service. Authenticated scraping is for personal use only. You are responsible for compliance with Seek, Indeed, LinkedIn, etc. terms. Prefer official APIs where available.

## Features

- **Tabbed modern UI** (CustomTkinter)
  - Filters
  - Results + Top 20 ranked matches with one-click Apply
  - Resume manager
  - Company / OSINT intel
  - Settings & authentication

- **Sources**
  - Adzuna API (primary, free tier, excellent Australia coverage)
  - Seek.com.au (Playwright + persistent local browser profile / login session)
  - Remote-focused boards (Remotive, Jobicy, etc.)
  - Extensible aggregator

- **Filters**
  - Multi-select locations (Brisbane, Gold Coast, Sunshine Coast, Ipswich, SEQ, QLD, major cities, Remote AU, Remote Worldwide)
  - Selectable job titles / categories common on Australian boards
  - Include / exclude keyword lists (title + description)
  - Salary min/max
  - Experience level
  - Contract type, work type (full-time, contract, hybrid, remote)
  - Date posted

- **Resume matching**
  - Upload PDF or DOCX
  - Extract skills / experience text
  - Score jobs against resume + your filters → ranked Top 20

- **Results**
  - Sortable table
  - Top 20 cards with **Apply Now** button (opens official apply URL)
  - Export to Excel (cross-platform) or CSV/JSON

- **Company OSINT (basic)**
  - Company name, location, website inference
  - Employee ratings where publicly discoverable (Seek employer reviews, Glassdoor summaries via careful public lookup)
  - Lifestyle / SEQ notes where relevant

- **Session management**
  - Login once to Seek (or other supported sites) via guided browser
  - Persistent local profile stored only on your machine
  - No credentials sent to any third party by this tool

## Requirements

- Python 3.10+
- All major OS: Windows, macOS, Linux

```bash
pip install -r requirements.txt
playwright install chromium   # required for Seek / browser sessions
```

## Quick Start

1. Clone the repo and switch to the `AutoJob` branch:
   ```bash
   git clone https://github.com/vectisops/AutoJob.git
   cd AutoJob
   git checkout AutoJob
   ```

2. Install dependencies (see above).

3. (Optional but recommended) Register free Adzuna API keys:  
   https://developer.adzuna.com/  
   Enter `app_id` and `app_key` in the Settings tab.

4. Run:
   ```bash
   python -m src.main
   ```

5. In Settings → Authenticate Seek: a browser window opens. Log in normally. Close when done. Session is saved locally under `data/browser_profiles/`.

6. Set filters, optionally upload resume, hit Search. Review Top 20, export Excel, click Apply.

## Project Structure

```
src/
  gui/          # CustomTkinter tabs and widgets
  scrapers/     # Adzuna, Seek (Playwright), remote, aggregator
  matching/     # Resume parser + job scorer
  osint/        # Light company intel
  models/       # Job dataclass
  utils/        # config, exporters, session helpers
config/         # example settings
data/           # local only (gitignored) – sessions, resumes, exports
```

## Configuration

API keys and preferences are stored locally (never committed). Use the Settings tab or edit `config/settings.json` after first run.

## Legal & Ethics

- This tool is for **personal research and job hunting** only.
- Do not use for bulk commercial scraping or spam applications.
- Authenticated sessions stay on your machine.
- Rate-limit yourself. Prefer Adzuna API over heavy browser scraping when possible.
- Glassdoor / employee ratings are best-effort public data only; many sites block automated access.

## Roadmap / Extensibility

- More authenticated sources (LinkedIn, company Greenhouse/Lever pages)
- Deeper OSINT (ASIC lookup, news sentiment)
- Scheduling / background runs
- Integration hooks for multi-agent systems

## License

Apache-2.0 (or as chosen by repo owner).

---

Built for sovereign, local-first tooling. Feedback and PRs welcome on the `AutoJob` branch.
