"""
AutoJob main GUI – CustomTkinter tabbed interface.
"""
from __future__ import annotations
import threading
import webbrowser
from pathlib import Path
from typing import List, Optional

import customtkinter as ctk
from tkinter import filedialog, messagebox

from src.utils.config import Config, DATA_DIR
from src.scrapers.aggregator import JobAggregator
from src.scrapers.seek import SeekScraper
from src.matching.resume_parser import ResumeParser
from src.matching.scorer import JobScorer
from src.osint.company_intel import CompanyIntel
from src.utils.exporters import export_to_excel
from src.utils.history import filter_new_jobs, save_history
from src.models.job import Job
from src.gui.widgets import ScrollableCheckFrame, KeywordListbox


# Common Australian / SEQ focused locations
LOCATIONS = [
    "Brisbane", "Gold Coast", "Sunshine Coast", "Ipswich", "Logan",
    "Toowoomba", "SEQ", "Queensland", "Sydney", "Melbourne",
    "Canberra", "Adelaide", "Perth", "Remote Australia", "Remote Worldwide",
]

# Broad role titles across industries (Seek / Adzuna AU style)
JOB_TITLES = [
    # Administration & Office
    "Administration Officer", "Office Administrator", "Receptionist", "Executive Assistant",
    "Personal Assistant", "Office Manager", "Data Entry", "Records Officer",
    # Customer service & retail
    "Customer Service Officer", "Customer Service Representative", "Call Centre Operator",
    "Retail Assistant", "Retail Manager", "Store Manager", "Sales Assistant",
    # Sales & marketing
    "Sales Representative", "Account Manager", "Business Development Manager",
    "Sales Manager", "Marketing Coordinator", "Marketing Manager", "Digital Marketing",
    "Content Writer", "Communications Officer",
    # Finance & accounting
    "Accountant", "Bookkeeper", "Accounts Payable", "Accounts Receivable",
    "Financial Analyst", "Finance Officer", "Payroll Officer", "Auditor",
    "Credit Controller", "Tax Accountant",
    # HR & recruitment
    "HR Advisor", "HR Manager", "Recruitment Consultant", "Talent Acquisition",
    "People and Culture", "Learning and Development",
    # Healthcare & aged care
    "Registered Nurse", "Enrolled Nurse", "Nurse", "Personal Care Worker",
    "Aged Care Worker", "Disability Support Worker", "Allied Health",
    "Physiotherapist", "Occupational Therapist", "Medical Receptionist",
    "Practice Manager", "Healthcare Assistant",
    # Education & childcare
    "Teacher", "Teacher Aide", "Early Childhood Educator", "Childcare Educator",
    "Tutor", "Trainer", "Instructional Designer",
    # Trades & construction
    "Electrician", "Plumber", "Carpenter", "Builder", "Boilermaker",
    "Welder", "Fitter and Turner", "Mechanic", "Diesel Mechanic",
    "Labourer", "Construction Worker", "Site Supervisor", "Project Supervisor",
    "Painter", "Landscaper", "Horticulturist",
    # Engineering (all disciplines)
    "Civil Engineer", "Structural Engineer", "Mechanical Engineer", "Electrical Engineer",
    "Mining Engineer", "Environmental Engineer", "Project Engineer", "Site Engineer",
    "Quantity Surveyor", "Draftsperson", "CAD Designer",
    # IT & technology
    "Software Engineer", "Software Developer", "Full Stack Developer", "Backend Developer",
    "Frontend Developer", "Python Developer", "Java Developer", "DevOps Engineer",
    "Cloud Engineer", "Systems Administrator", "IT Support", "Help Desk",
    "Network Engineer", "Cyber Security", "Data Analyst", "Data Engineer",
    "Business Analyst", "QA Tester", "Test Analyst",
    # Logistics, warehouse & transport
    "Warehouse Operator", "Warehouse Manager", "Forklift Operator", "Picker Packer",
    "Logistics Coordinator", "Supply Chain", "Truck Driver", "Delivery Driver",
    "Dispatcher", "Inventory Controller",
    # Hospitality & tourism
    "Chef", "Cook", "Kitchen Hand", "Waiter", "Barista", "Bartender",
    "Restaurant Manager", "Hotel Manager", "Housekeeper",
    # Government, defence & security
    "Public Servant", "Policy Officer",
    "Defence", "ADF", "Security Officer", "Security Guard", "Intelligence Analyst",
    "Compliance Officer", "WHS Officer", "OHS Advisor",
    # Legal
    "Solicitor", "Lawyer", "Paralegal", "Legal Secretary", "Conveyancer",
    # Science & environment
    "Laboratory Technician", "Scientist", "Research Assistant", "Environmental Officer",
    "Geologist", "Chemist",
    # Property & real estate
    "Property Manager", "Real Estate Agent", "Leasing Consultant", "Facilities Manager",
    # Management & professional
    "Project Manager", "Operations Manager", "General Manager", "Team Leader",
    "Supervisor", "Coordinator", "Consultant", "Analyst",
]


class AutoJobApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AutoJob – Australian Job Scraper")
        self.geometry("1180x780")
        self.minsize(1000, 650)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.config = Config()
        self.aggregator = JobAggregator(self.config)
        self.resume_parser = ResumeParser()
        self.company_intel = CompanyIntel()
        self.jobs: List[Job] = []
        self.top_jobs: List[Job] = []

        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkFrame(self, height=50, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="AutoJob", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", padx=16)
        ctk.CTkLabel(header, text="SEQ / Australia focused · Resume match · Company intel",
                     text_color="gray70").pack(side="left", padx=8)

        self.tabview = ctk.CTkTabview(self, corner_radius=8)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=8)

        self.tab_filters = self.tabview.add("Filters")
        self.tab_results = self.tabview.add("Results")
        self.tab_resume = self.tabview.add("Resume")
        self.tab_company = self.tabview.add("Company Intel")
        self.tab_settings = self.tabview.add("Settings")

        self._build_filters_tab()
        self._build_results_tab()
        self._build_resume_tab()
        self._build_company_tab()
        self._build_settings_tab()

        self.status = ctk.CTkLabel(self, text="Ready", anchor="w", height=24)
        self.status.pack(fill="x", padx=12, pady=(0, 6))

    def _build_filters_tab(self):
        outer = ctk.CTkFrame(self.tab_filters, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=8, pady=8)

        left = ctk.CTkFrame(outer)
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))

        ctk.CTkLabel(left, text="Keywords (search query)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=8, pady=(8, 0))
        self.keywords_entry = ctk.CTkEntry(
            left,
            placeholder_text="e.g. nurse OR electrician OR accountant — or leave blank and tick roles below",
        )
        self.keywords_entry.pack(fill="x", padx=8, pady=4)

        loc_frame = ctk.CTkFrame(left)
        loc_frame.pack(fill="both", expand=True, padx=8, pady=6)
        ctk.CTkLabel(loc_frame, text="Locations (multi-select)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=4)
        self.loc_checks = ScrollableCheckFrame(loc_frame, LOCATIONS, height=160)
        self.loc_checks.pack(fill="both", expand=True, padx=2, pady=2)
        self.loc_checks.set_selected(self.config.get("last_locations", ["Brisbane", "SEQ"]))

        title_frame = ctk.CTkFrame(left)
        title_frame.pack(fill="both", expand=True, padx=8, pady=6)
        ctk.CTkLabel(title_frame, text="Role titles (optional multi-select — any industry)",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=4)
        self.title_checks = ScrollableCheckFrame(title_frame, JOB_TITLES, height=180)
        self.title_checks.pack(fill="both", expand=True, padx=2, pady=2)

        right = ctk.CTkFrame(outer, width=320)
        right.pack(side="right", fill="y", padx=(6, 0))
        right.pack_propagate(False)

        ctk.CTkLabel(right, text="Salary (AUD)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(12, 0))
        sal_row = ctk.CTkFrame(right, fg_color="transparent")
        sal_row.pack(fill="x", padx=10, pady=4)
        self.salary_min = ctk.CTkEntry(sal_row, placeholder_text="Min", width=100)
        self.salary_min.pack(side="left", padx=(0, 6))
        self.salary_max = ctk.CTkEntry(sal_row, placeholder_text="Max", width=100)
        self.salary_max.pack(side="left")

        ctk.CTkLabel(right, text="Exclude keywords", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(12, 0))
        self.exclude_box = KeywordListbox(right, title="")
        self.exclude_box.pack(fill="x", padx=6, pady=4)
        self.exclude_box.set_keywords(self.config.get("exclude_keywords", []))

        ctk.CTkLabel(right, text="Include keywords (boost)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(8, 0))
        self.include_box = KeywordListbox(right, title="")
        self.include_box.pack(fill="x", padx=6, pady=4)

        self.include_remote = ctk.CTkCheckBox(right, text="Include free remote boards")
        self.include_remote.pack(anchor="w", padx=12, pady=8)
        self.include_remote.select()

        btn_row = ctk.CTkFrame(right, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=16)
        self.search_btn = ctk.CTkButton(btn_row, text="Search Jobs", height=40, font=ctk.CTkFont(size=15, weight="bold"),
                                        command=self._on_search)
        self.search_btn.pack(fill="x")

    def _build_results_tab(self):
        top = ctk.CTkFrame(self.tab_results, fg_color="transparent")
        top.pack(fill="x", padx=8, pady=6)
        ctk.CTkLabel(top, text="Top 30 most applicable matches", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        self.export_btn = ctk.CTkButton(top, text="Export Excel", width=120, command=self._export)
        self.export_btn.pack(side="right", padx=4)
        self.count_label = ctk.CTkLabel(top, text="")
        self.count_label.pack(side="right", padx=12)

        self.top_frame = ctk.CTkScrollableFrame(self.tab_results, height=320)
        self.top_frame.pack(fill="x", padx=8, pady=4)

        ctk.CTkLabel(self.tab_results, text="All results (sorted by score)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=12, pady=(8, 0))
        self.results_box = ctk.CTkTextbox(self.tab_results, font=ctk.CTkFont(family="Consolas", size=12))
        self.results_box.pack(fill="both", expand=True, padx=8, pady=6)

    def _render_results(self):
        for w in self.top_frame.winfo_children():
            w.destroy()

        self.top_jobs = self.jobs[:30]
        for i, job in enumerate(self.top_jobs, 1):
            card = ctk.CTkFrame(self.top_frame, corner_radius=8)
            card.pack(fill="x", padx=4, pady=4)

            left = ctk.CTkFrame(card, fg_color="transparent")
            left.pack(side="left", fill="both", expand=True, padx=10, pady=8)
            ctk.CTkLabel(left, text=f"#{i}  {job.title}", font=ctk.CTkFont(size=14, weight="bold"),
                         anchor="w").pack(anchor="w")
            meta = f"{job.company}  ·  {job.location}  ·  {job.salary_display}  ·  {job.source}  ·  Score {job.score}"
            ctk.CTkLabel(left, text=meta, text_color="gray70", anchor="w").pack(anchor="w")
            if job.match_reasons:
                ctk.CTkLabel(left, text=" · ".join(job.match_reasons[:3]), text_color="gray60",
                             font=ctk.CTkFont(size=11), anchor="w").pack(anchor="w")

            btn = ctk.CTkButton(card, text="Apply Now", width=110, height=32,
                                command=lambda u=job.apply_url or job.url: webbrowser.open(u) if u else None)
            btn.pack(side="right", padx=12, pady=12)

        self.results_box.delete("1.0", "end")
        lines = []
        for j in self.jobs:
            lines.append(f"[{j.score:5.1f}] {j.title[:55]:<55} | {j.company[:25]:<25} | {j.location[:20]:<20} | {j.source}")
        self.results_box.insert("1.0", "\n".join(lines) if lines else "No results yet.")
        self.count_label.configure(text=f"{len(self.jobs)} jobs")

    def _build_resume_tab(self):
        f = ctk.CTkFrame(self.tab_resume, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(f, text="Upload resume (PDF or DOCX) to improve ranking",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w")
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", pady=8)
        self.resume_path_var = ctk.StringVar(value=self.config.get("resume_path", "") or "No file selected")
        ctk.CTkLabel(row, textvariable=self.resume_path_var, anchor="w").pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row, text="Browse…", width=100, command=self._browse_resume).pack(side="right")

        ctk.CTkLabel(f, text="Extracted text preview", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(12, 0))
        self.resume_preview = ctk.CTkTextbox(f, height=300)
        self.resume_preview.pack(fill="both", expand=True, pady=6)

        if self.config.get("resume_path"):
            try:
                self.resume_parser.load(self.config.get("resume_path"))
                self.resume_preview.insert("1.0", self.resume_parser.text[:5000])
            except Exception:
                pass

    def _browse_resume(self):
        path = filedialog.askopenfilename(
            title="Select resume",
            filetypes=[("Documents", "*.pdf *.docx *.doc *.txt"), ("All", "*.*")]
        )
        if path:
            self.config.set("resume_path", path)
            self.resume_path_var.set(path)
            text = self.resume_parser.load(path)
            self.resume_preview.delete("1.0", "end")
            self.resume_preview.insert("1.0", text[:8000] or "(no text extracted)")

    def _build_company_tab(self):
        f = ctk.CTkFrame(self.tab_company, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=12, pady=12)
        ctk.CTkLabel(f, text="Company OSINT (basic public data)",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(f, text="Select a job from Results or type a company name below.",
                     text_color="gray70").pack(anchor="w")

        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", pady=8)
        self.company_entry = ctk.CTkEntry(row, placeholder_text="Company name")
        self.company_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(row, text="Lookup", width=100, command=self._lookup_company).pack(side="right")

        self.company_info = ctk.CTkTextbox(f)
        self.company_info.pack(fill="both", expand=True, pady=6)

    def _lookup_company(self):
        name = self.company_entry.get().strip()
        if not name and self.top_jobs:
            name = self.top_jobs[0].company
        if not name:
            return
        info = self.company_intel.lookup(name)
        lines = [
            f"Company: {info['company']}",
            f"Summary: {info.get('summary') or '—'}",
            f"Website: {info.get('website') or '—'}",
            f"Employee rating: {info.get('employee_rating') or 'Not available automatically'}",
            f"Rating source: {info.get('rating_source') or '—'}",
            "",
            "Lifestyle / SEQ notes:",
            info.get("lifestyle") or "—",
            "",
            "Notes:",
            *info.get("notes", []),
            "",
            "Tip: For accurate Glassdoor / Seek employer ratings, open the company page manually while logged in.",
        ]
        self.company_info.delete("1.0", "end")
        self.company_info.insert("1.0", "\n".join(lines))

    def _build_settings_tab(self):
        f = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(f, text="Adzuna API (recommended – free tier)", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(f, text="Register at https://developer.adzuna.com/  → enter app_id & app_key",
                     text_color="gray70").pack(anchor="w")

        form = ctk.CTkFrame(f)
        form.pack(fill="x", pady=10)
        ctk.CTkLabel(form, text="App ID").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.adzuna_id = ctk.CTkEntry(form, width=360)
        self.adzuna_id.grid(row=0, column=1, padx=8, pady=4)
        self.adzuna_id.insert(0, self.config.get("adzuna_app_id", ""))

        ctk.CTkLabel(form, text="App Key").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.adzuna_key = ctk.CTkEntry(form, width=360, show="•")
        self.adzuna_key.grid(row=1, column=1, padx=8, pady=4)
        self.adzuna_key.insert(0, self.config.get("adzuna_app_key", ""))

        ctk.CTkButton(form, text="Save API keys", command=self._save_keys).grid(row=2, column=1, sticky="e", padx=8, pady=8)

        ctk.CTkLabel(f, text="Seek authentication (persistent local browser profile)",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(20, 0))
        ctk.CTkLabel(f, text="Opens a real browser window. Log in to Seek, then close the window. Session stays on this machine only.",
                     text_color="gray70", wraplength=700).pack(anchor="w")
        ctk.CTkButton(f, text="Authenticate Seek (open browser)", width=260, height=36,
                      command=self._auth_seek).pack(anchor="w", pady=10)

        ctk.CTkLabel(f, text="Theme").pack(anchor="w", pady=(16, 0))
        self.theme_menu = ctk.CTkOptionMenu(f, values=["dark", "light", "system"], command=self._set_theme)
        self.theme_menu.set(self.config.get("theme", "dark"))
        self.theme_menu.pack(anchor="w", pady=4)

        ctk.CTkLabel(f, text=f"Data directory: {DATA_DIR}", text_color="gray60").pack(anchor="w", pady=20)

    def _save_keys(self):
        self.config.update({
            "adzuna_app_id": self.adzuna_id.get().strip(),
            "adzuna_app_key": self.adzuna_key.get().strip(),
        })
        self.aggregator = JobAggregator(self.config)
        self.status.configure(text="API keys saved locally.")
        messagebox.showinfo("Saved", "Adzuna keys stored in local config (not uploaded).")

    def _set_theme(self, mode: str):
        ctk.set_appearance_mode(mode)
        self.config.set("theme", mode)

    def _auth_seek(self):
        self.status.configure(text="Opening Seek login browser… log in then close the window.")
        def run():
            import asyncio
            loop = None
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                scraper = SeekScraper(self.config.get("seek_profile_dir"), headless=False)
                loop.run_until_complete(scraper.authenticate_interactive())
                self.after(0, lambda: self.status.configure(text="Seek session saved locally."))
            except Exception as e:
                self.after(0, lambda: self.status.configure(text=f"Auth error: {e}"))
            finally:
                if loop is not None:
                    try:
                        loop.close()
                    except Exception:
                        pass
        threading.Thread(target=run, daemon=True).start()

    def _on_search(self):
        self.search_btn.configure(state="disabled", text="Searching…")
        self.status.configure(text="Running scrapers…")
        self.tabview.set("Results")

        def worker():
            try:
                locs = self.loc_checks.get_selected()
                titles = self.title_checks.get_selected()
                keywords = self.keywords_entry.get().strip()
                title_bits = [f'"{t}"' for t in titles[:8]]
                if titles and not keywords:
                    keywords = " OR ".join(title_bits)
                elif titles and keywords:
                    keywords = keywords + " OR " + " OR ".join(title_bits[:5])

                # No tech-only default — require keywords or selected roles
                if not keywords:
                    self.after(0, lambda: self._search_error(
                        "Enter keywords or select at least one role title before searching."
                    ))
                    return

                primary_loc = locs[0] if locs else "Brisbane QLD"
                if "SEQ" in locs or "Queensland" in locs:
                    primary_loc = "Brisbane QLD"

                query = {
                    "keywords": keywords,
                    "location": primary_loc,
                    "preferred_locations": locs,
                    "include_keywords": self.include_box.get_keywords() + titles,
                    "salary_min": self._num(self.salary_min.get()),
                    "salary_max": self._num(self.salary_max.get()),
                    "results_per_page": int(self.config.get("results_per_page", 50)),
                    "max_pages": int(self.config.get("max_pages", 8)),
                    "sort_by": "relevance",
                }

                include_remote = bool(self.include_remote.get())
                raw_jobs = self.aggregator.search(query, include_remote=include_remote)

                resume_kw = self.resume_parser.keywords if self.resume_parser.text else set()
                scorer = JobScorer(resume_keywords=resume_kw, exclude=self.exclude_box.get_keywords())
                ranked = scorer.score(raw_jobs, query)

                new_only = filter_new_jobs(ranked)
                top_n = int(self.config.get("top_results", 30))
                result_jobs = new_only[:top_n]

                save_history(ranked)
                self.config.set("last_locations", locs)
                self.config.set("exclude_keywords", self.exclude_box.get_keywords())

                self.after(0, lambda jobs=result_jobs: self._search_done(jobs))
            except Exception as e:
                err = str(e)
                self.after(0, lambda: self._search_error(err))

        threading.Thread(target=worker, daemon=True).start()

    def _search_done(self, jobs: List[Job]):
        self.jobs = jobs
        self._render_results()
        self.search_btn.configure(state="normal", text="Search Jobs")
        self.status.configure(text=f"Done – {len(self.jobs)} unique jobs ranked. Top 30 ready.")

    def _search_error(self, msg: str):
        self.search_btn.configure(state="normal", text="Search Jobs")
        self.status.configure(text=f"Error: {msg}")
        self.after(50, lambda: messagebox.showerror("Search failed", msg))

    def _export(self):
        if not self.jobs:
            messagebox.showinfo("Export", "No jobs to export yet.")
            return
        path = export_to_excel(self.jobs)
        self.status.configure(text=f"Exported → {path}")
        messagebox.showinfo("Exported", f"Saved to:\n{path}")

    @staticmethod
    def _num(s: str) -> Optional[float]:
        s = (s or "").replace(",", "").strip()
        if not s:
            return None
        try:
            return float(s)
        except ValueError:
            return None


def run_app():
    app = AutoJobApp()
    app.mainloop()
