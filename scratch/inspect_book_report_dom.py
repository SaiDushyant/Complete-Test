"""
Scratch script to inspect Book Report page HTML.
"""

from playwright.sync_api import sync_playwright
from config.settings import settings
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage
from workflows.admin_portal.pages.admin_book_report_page import AdminBookReportPage

def inspect_book_report():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        login_page = AdminLoginPage(page)
        login_page.navigate()
        login_page.login()
        page.wait_for_timeout(2000)

        book_page = AdminBookReportPage(page)
        book_page.navigate()
        page.wait_for_timeout(2000)

        # Dump all select tags raw outerHTML
        select_htmls = page.evaluate("""() => {
            return Array.from(document.querySelectorAll("select")).map(s => s.outerHTML);
        }""")
        print("ALL SELECT OUTER HTMLs:")
        for s in select_htmls:
            print(" ->", s)

        browser.close()

if __name__ == "__main__":
    inspect_book_report()
