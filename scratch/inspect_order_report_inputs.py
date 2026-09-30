import sys
sys.path.insert(0, ".")
from urllib.parse import urlsplit
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

    parts = urlsplit(settings.admin_portal.base_url)
    base_domain = f"{parts.scheme}://{parts.netloc}"

    page.goto(f"{base_domain}/admin/Controlbase/OrderReport")
    page.wait_for_timeout(3000)

    print("=== INPUTS ON ORDER REPORT PAGE ===")
    inputs = page.evaluate("""() => {
        return Array.from(document.querySelectorAll("input")).map(e => ({
            id: e.id,
            name: e.name,
            className: e.className,
            type: e.type,
            placeholder: e.placeholder,
            value: e.value,
            parentText: e.parentElement ? e.parentElement.innerText.trim() : ''
        }));
    }""")
    for inp in inputs:
        if inp['id'] or inp['name'] or 'date' in inp['className'].lower() or 'From' in inp['parentText']:
            print(inp)

    # Click Filter button
    filter_btn = page.locator("a#filterLeadReport").first
    if filter_btn.is_visible():
        filter_btn.click()
        page.wait_for_timeout(1000)
        print("=== AFTER CLICKING FILTER BUTTON (CHECK POPUPS/MODALS) ===")
        jconfirm = page.locator(".jconfirm-box, .jconfirm").first
        if jconfirm.is_visible():
            print("jconfirm text:", jconfirm.inner_text())

    browser.close()
