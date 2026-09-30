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

    print("=== ORDER REPORT PAGE INFO ===")
    print("URL:", page.url)
    print("Title/Heading:", page.evaluate("() => document.querySelector('.page-title-box h4, h4.page-title, h4')?.innerText || 'No title'"))
    
    # Inspect top filter inputs
    filters = page.evaluate("""() => {
        return Array.from(document.querySelectorAll("input, select, button, a")).map(e => ({
            tag: e.tagName,
            type: e.type || '',
            id: e.id || '',
            name: e.name || '',
            className: e.className || '',
            value: e.value || '',
            placeholder: e.placeholder || '',
            text: e.innerText.trim(),
            optionsCount: e.tagName === 'SELECT' ? e.options.length : 0
        }));
    }""")
    print("=== FILTERS & BUTTONS ===")
    for f in filters:
        if f['id'] or f['name'] or f['text'] in ['Filter', 'Refresh', 'CSV', 'Excel', 'PDF']:
            print(f)

    # Inspect table headers
    ths = page.evaluate("() => Array.from(document.querySelectorAll('th')).map(e => e.innerText.trim())")
    print("\n=== TABLE HEADERS (Count:", len(ths), ") ===")
    print(ths)

    # Inspect sample rows if any
    rows = page.evaluate("() => Array.from(document.querySelectorAll('#datatable tbody tr, table tbody tr')).map(e => e.innerText.trim())")
    print("\n=== SAMPLE ROWS (Count:", len(rows), ") ===")
    print(rows[:5])

    browser.close()
