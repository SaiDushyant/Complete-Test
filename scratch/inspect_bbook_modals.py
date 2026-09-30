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
    page.goto(f"{settings.admin_portal.base_url}/Controlbase/bBook")
    page.wait_for_timeout(3000)
    
    print("=== BUTTONS & LINKS ON BBOOK PAGE ===")
    btns = page.evaluate("""() => {
        return Array.from(document.querySelectorAll("a, button")).map(e => ({
            tag: e.tagName,
            text: e.innerText.trim(),
            className: e.className,
            href: e.href || '',
            target: e.getAttribute('data-target') || ''
        }));
    }""")
    for b in btns:
        if b['text'] or b['target']:
            print(b)

    print("=== MODALS IN DOM ===")
    modals = page.evaluate("""() => {
        return Array.from(document.querySelectorAll(".modal")).map(e => ({
            id: e.id,
            className: e.className,
            html: e.innerHTML
        }));
    }""")
    for m in modals:
        print(f"ID: {m['id']}, Class: {m['className']}")
        print(m['html'][:2000])
        print("------------------------------------------")

    browser.close()
