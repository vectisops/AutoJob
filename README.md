# AutoJob

**A personal job-search assistant for Australia — especially Brisbane and South East Queensland.**

AutoJob searches more widely than a normal job-board session, ranks what it finds against *your* preferences and résumé, then shows you only the strongest matches.  
You get better coverage of niche and less-obvious roles, without drowning in noise.

---

## The idea in one sentence

Collect a few hundred relevant listings → score them for you → return the best **30** → remember what you’ve already seen so the next search stays fresh.

---

## Who it’s for

AutoJob is built for **one person** hunting for their next role.

It is not a recruitment platform, not an agency tool, and not a bulk data harvester.  
Everything is sized for a single user: private, local, and under your control.

---

## What it does

### Broader search, tighter results
Ordinary job sites show you a narrow first page. AutoJob pulls a larger but still manageable set of listings (typically a few hundred across sources) so niche or poorly titled roles are less likely to be missed.  
It then ranks those results and returns a **maximum of 30** of the best matches.

### Ranked for *you*
You set locations, role types, keywords to include or exclude, and salary range.  
You can also upload your résumé (PDF or Word). AutoJob uses that information to score each job so the list reflects your background, not just generic keyword matches.

### Fresh results over time
Each search is compared against a private history kept only on your computer.  
Jobs you’ve already seen are filtered out, so later runs surface new opportunities instead of the same listings again.

### One-click apply
The top matches appear as clear cards with an **Apply Now** button.  
That button simply opens the official job page. AutoJob never submits applications for you — you stay in control.

### Light company context
You can look up basic information about an employer, including notes that are useful if you’re considering roles in South East Queensland.

### Private by design
Résumés, login sessions, search preferences, and job history stay on your machine.  
Nothing is uploaded to a central service for ranking or advertising.

---

## Built with SEQ in mind

Locations you can focus on include:

- Brisbane  
- Gold Coast  
- Sunshine Coast  
- Ipswich  
- Logan  
- Toowoomba  
- SEQ / Queensland more broadly  

You can also include other Australian cities or remote roles (Australia-wide or worldwide).  
Everything is chosen with simple checkboxes — no complicated configuration.

---

## How the app is organised

**Filters**  
Set locations, job titles, include/exclude keywords, salary range, and related preferences. Start a search from here.

**Results**  
See your top matches (up to 30) as cards with Apply Now. Export to a spreadsheet if you want to keep a longer record.

**Resume**  
Upload a CV or résumé so ranking can take your experience into account.

**Company Intel**  
Quick background on an employer, with SEQ-relevant lifestyle notes where useful.

**Settings**  
Connect free job-search API credentials if you have them, and complete a one-time login for sites that need a signed-in session. All of this stays local.

---

## Quick start (for testing)

```bash
git clone https://github.com/vectisops/AutoJob.git
cd AutoJob
pip install -r requirements.txt
playwright install chromium
python -m src.main
```

1. Settings → add free Adzuna API keys (https://developer.adzuna.com)  
2. Optional: Authenticate Seek (opens browser once)  
3. Filters → set locations / titles / keywords  
4. Optional: upload résumé  
5. Search → review Top 30 → Apply Now or Export Excel  

---

## Privacy

- Your résumé stays on your computer.  
- Login sessions for job sites are stored in a local browser profile only.  
- Job history used for de-duplication is a local file.  
- AutoJob is designed to help *you* find roles, not to collect data for anyone else.

---

*Personal job search for Australia. Quiet, local, and focused on the roles that actually fit.*
