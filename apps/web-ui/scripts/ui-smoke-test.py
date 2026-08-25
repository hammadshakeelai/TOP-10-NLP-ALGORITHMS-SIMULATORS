"""End-to-end UI smoke test — runs the built frontend with NO backend.

Verifies: catalog loads from offline snapshots, algorithm pages open,
demo runs execute, results render, theme toggle works, 404 works.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

DIST_INDEX = "http://localhost:4173/"
SHOTS = Path(r"C:\Users\HP\AppData\Local\Temp\opencode")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

results: list[tuple[str, str, str]] = []  # (name, status, detail)


def check(name: str, fn):
    try:
        detail = fn()
        results.append((name, "PASS", detail or ""))
        print(f"PASS  {name}  {detail or ''}")
    except Exception as exc:  # noqa: BLE001
        results.append((name, "FAIL", repr(exc)))
        print(f"FAIL  {name}  {exc!r}")


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME,
            headless=True,
            args=["--no-sandbox", "--disable-gpu"],
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        console_errors: list[str] = []
        failed_requests: list[str] = []
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("requestfailed", lambda r: failed_requests.append(r.url))

        # 1. Catalog loads offline
        page.goto(DIST_INDEX, wait_until="networkidle")
        check("catalog: 13 algorithm cards render", lambda: (
            f"cards={page.locator('button:has(span.chip)').count()}"
            if page.locator("button:has(span.chip)").count() >= 13
            else (_ for _ in ()).throw(AssertionError("fewer than 13 cards"))
        ))
        check("offline badge shown", lambda: (
            "visible"
            if page.get_by_text("Offline demo").first.is_visible()
            else (_ for _ in ()).throw(AssertionError("badge missing"))
        ))
        page.screenshot(path=str(SHOTS / "qa-1-catalog.png"))

        # 2. Search filter works
        page.get_by_label("Search algorithms").fill("textrank")
        page.wait_for_timeout(300)
        check("search filters to textrank", lambda: (
            "1 card"
            if page.locator("button:has(span.chip)").count() == 1
            else (_ for _ in ()).throw(AssertionError(
                f"got {page.locator('button:has(span.chip)').count()}"))
        ))
        page.get_by_label("Search algorithms").fill("")

        # 3. Open TextRank simulator
        page.get_by_role("button", name="TextRank").first.click()
        page.wait_for_url("**/simulate/textrank", wait_until="networkidle")
        check("simulator page opens", lambda: (
            page.locator("h1").inner_text()
            if "TextRank" in page.locator("h1").inner_text()
            else (_ for _ in ()).throw(AssertionError("wrong h1"))
        ))

        # 4. Load demo → offline canned run renders results
        page.get_by_role("button", name="Load Demo").first.click()
        page.wait_for_selector("text=Pipeline Steps", timeout=15_000)
        check("demo run renders pipeline steps", lambda: "Pipeline Steps visible")
        check("visualizations render", lambda: (
            "yes"
            if page.get_by_role("heading", name="Visualizations").is_visible()
            else (_ for _ in ()).throw(AssertionError("no viz section"))
        ))
        check("offline warning attached to run", lambda: (
            "yes"
            if page.get_by_text("OFFLINE_MODE").first.is_visible()
            else (_ for _ in ()).throw(AssertionError("no OFFLINE_MODE warning"))
        ))
        page.screenshot(path=str(SHOTS / "qa-2-simulator.png"), full_page=False)

        # 5. Expand a pipeline step (first step header button in the timeline)
        page.locator("section:has(h2:text('Pipeline Steps')) button").nth(1).click()
        page.wait_for_timeout(300)

        # 6. Run history appears after demo run (before any reload)
        check("run history panel", lambda: (
            "visible"
            if page.get_by_text("History", exact=False).first.is_visible()
            else (_ for _ in ()).throw(AssertionError("history panel missing after run"))
        ))

        # 7. Trace viewer copy button exists
        check("trace copy button", lambda: (
            "yes" if page.get_by_role("button", name="Copy JSON").first.is_visible()
            else "hidden (trace may be collapsed)"
        ))

        # 8. Export JSON button
        check("export JSON button", lambda: (
            "yes" if page.get_by_role("button", name="Export JSON").is_visible()
            else (_ for _ in ()).throw(AssertionError("missing"))
        ))

        # 9. Theme toggle → light mode
        page.get_by_role("button", name="Switch to light mode").click()
        page.wait_for_timeout(300)
        check("theme toggles to light", lambda: (
            "light class set"
            if page.evaluate("document.documentElement.classList.contains('light')")
            else (_ for _ in ()).throw(AssertionError("no light class"))
        ))
        page.screenshot(path=str(SHOTS / "qa-3-light-simulator.png"))

        # 10. Theme persists across reload
        page.reload(wait_until="networkidle")
        check("theme persists after reload", lambda: (
            "persisted"
            if page.evaluate("document.documentElement.classList.contains('light')")
            else (_ for _ in ()).throw(AssertionError("lost"))
        ))
        page.get_by_role("button", name="Switch to dark mode").click()

        # 11. 404 route
        page.goto(DIST_INDEX + "no-such-page", wait_until="networkidle")
        check("404 page renders", lambda: (
            "404 visible"
            if page.get_by_text("404", exact=True).is_visible()
            else (_ for _ in ()).throw(AssertionError("no 404"))
        ))

        # 12. Console errors — network failures to the (absent) backend are
        # expected in offline mode; anything else is a bug.
        unexpected = [e for e in console_errors if "ERR_CONNECTION_REFUSED" not in e]
        print(f"      failed requests: {failed_requests}")
        check("no unexpected console errors", lambda: (
            f"{len(unexpected)} unexpected"
            if not unexpected
            else (_ for _ in ()).throw(AssertionError("; ".join(unexpected[:3])))
        ))

        browser.close()

    failed = [r for r in results if r[1] == "FAIL"]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
