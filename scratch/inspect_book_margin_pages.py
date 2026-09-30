import sys
sys.path.insert(0, ".")
from playwright.sync_api import sync_playwright
from config.settings import settings
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    admin_login = AdminLoginPage(page)
    admin_login.navigate()
    admin_login.login()
    page.wait_for_timeout(2000)

    from urllib.parse import urlsplit
    parts = urlsplit(settings.admin_portal.base_url)
    base_domain = f"{parts.scheme}://{parts.netloc}"

    # 1. Inspect /admin/Controlbase/aBookUserMargin
    page.goto(f"{base_domain}/admin/Controlbase/aBookUserMargin")
    page.wait_for_timeout(3000)
    print("=== A BOOK USER MARGIN PAGE INFO ===")
    print("URL:", page.url)
    print("Title/Heading:", page.evaluate("() => document.querySelector('.page-title-box, h4, h3')?.innerText || 'No title'"))
    print("THs:", page.evaluate("() => Array.from(document.querySelectorAll('th')).map(e => e.innerText.trim())"))
    rows = page.evaluate("() => Array.from(document.querySelectorAll('#datatable tbody tr')).map(e => e.innerText.trim())")
    print("Rows:", rows[:5])

    # 2. Inspect /admin/Controlbase/bBookUserMargin
    page.goto(f"{base_domain}/admin/Controlbase/bBookUserMargin")
    page.wait_for_timeout(3000)
    print("\n=== B BOOK USER MARGIN PAGE INFO ===")
    print("URL:", page.url)
    print("Title/Heading:", page.evaluate("() => document.querySelector('.page-title-box, h4, h3')?.innerText || 'No title'"))
    print("THs:", page.evaluate("() => Array.from(document.querySelectorAll('th')).map(e => e.innerText.trim())"))
    b_rows = page.evaluate("() => Array.from(document.querySelectorAll('#datatable tbody tr')).map(e => e.innerText.trim())")
    print("Rows:", b_rows[:5])

    browser.close()
