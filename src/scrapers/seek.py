"""Seek.com.au helper using a personal browser profile.

This module is intended for individual job seekers. It re-uses a local
browser profile so you only need to log in once. It is deliberately
limited in how many pages it requests and is not built for mass collection.
"""
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import quote_plus

from src.models.job import Job
from src.scrapers.base import BaseScraper


class SeekScraper(BaseScraper):
    name = "Seek"

    def __init__(self, profile_dir: str | Path, headless: bool = True):
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless

    def search(self, query: Dict[str, Any]) -> List[Job]:
        try:
            return asyncio.run(self._search_async(query))
        except Exception as e:
            print(f"[Seek] search failed: {e}")
            return []

    async def _search_async(self, query: Dict[str, Any]) -> List[Job]:
        from playwright.async_api import async_playwright

        keywords = query.get("keywords", "")
        location = query.get("location", "Brisbane QLD")
        max_pages = min(int(query.get("max_pages", 6)), 10)

        base = "https://www.seek.com.au/jobs"
        params = f"?keywords={quote_plus(keywords)}&where={quote_plus(location)}"

        jobs: List[Job] = []
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=self.headless,
                viewport={"width": 1280, "height": 900},
                args=["--disable-blink-features=AutomationControlled"],
                ignore_default_args=["--enable-automation"],
            )
            page = context.pages[0] if context.pages else await context.new_page()

            for page_num in range(1, max_pages + 1):
                url = f"{base}{params}&page={page_num}"
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                    await page.wait_for_timeout(1500)

                    cards = await page.query_selector_all(
                        '[data-automation="jobCard"], article[data-testid="job-card"], [data-automation="normalJob"]'
                    )
                    if not cards:
                        cards = await page.query_selector_all("article")

                    for card in cards:
                        try:
                            title_el = await card.query_selector('[data-automation="jobTitle"], a[data-automation="jobTitle"]')
                            company_el = await card.query_selector('[data-automation="jobCompany"], [data-automation="jobCompanyName"]')
                            loc_el = await card.query_selector('[data-automation="jobLocation"], [data-automation="jobCardLocation"]')
                            salary_el = await card.query_selector('[data-automation="jobSalary"]')
                            link_el = await card.query_selector('a[data-automation="jobTitle"], a[href*="/job/"]')

                            title = (await title_el.inner_text()).strip() if title_el else ""
                            company = (await company_el.inner_text()).strip() if company_el else "Unknown"
                            location_txt = (await loc_el.inner_text()).strip() if loc_el else location
                            salary_raw = (await salary_el.inner_text()).strip() if salary_el else ""
                            href = await link_el.get_attribute("href") if link_el else ""
                            if href and not href.startswith("http"):
                                href = "https://www.seek.com.au" + href

                            if not title:
                                continue

                            job_id = href.split("/")[-1].split("?")[0] if href else f"seek-{len(jobs)}"
                            jobs.append(Job(
                                id=f"seek-{job_id}",
                                title=title,
                                company=company,
                                location=location_txt,
                                salary_raw=salary_raw,
                                url=href,
                                apply_url=href,
                                source="Seek",
                                description="",
                            ))
                        except Exception:
                            continue

                    if len(cards) < 10:
                        break
                except Exception as e:
                    print(f"[Seek] page {page_num} error: {e}")
                    break

            await context.close()
        return jobs

    async def authenticate_interactive(self) -> bool:
        """Launch headed browser so user can log in. Profile is persisted."""
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=False,
                viewport={"width": 1280, "height": 900},
            )
            page = context.pages[0] if context.pages else await context.new_page()
            await page.goto("https://www.seek.com.au/sign-in", wait_until="domcontentloaded")
            print("[Seek] Browser opened. Please log in, then close the window when finished.")
            try:
                await page.wait_for_event("close", timeout=0)
            except Exception:
                pass
            await context.close()
        return True
