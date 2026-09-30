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

    # Navigate to bBook and wait for table
    page.goto("https://stage.xtremenext.com/admin/Controlbase/bBook", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    
    print("=== CURRENT URL ===")
    print(page.url)

    print("=== ALL BUTTONS & LINKS ===")
    elements = page.evaluate("""() => {
        return Array.from(document.querySelectorAll("a, button, input[type='button'], input[type='submit']")).map(e => ({
            tag: e.tagName,
            text: e.innerText.trim(),
            id: e.id,
            className: e.className,
            href: e.href || '',
            dataTarget: e.getAttribute('data-target') || '',
            dataToggle: e.getAttribute('data-toggle') || '',
            onclick: e.getAttribute('onclick') || ''
        }));
    }""")
    for el in elements:
        if el['text'] or el['dataTarget'] or 'btn' in el['className']:
            print(el)

    print("=== ALL FORMS / MODALS ===")
    modals = page.evaluate("""() => {
        return Array.from(document.querySelectorAll(".modal, form")).map(e => ({
            tag: e.tagName,
            id: e.id,
            className: e.className,
            action: e.action || '',
            html: e.innerHTML.slice(0, 1000)
        }));
    }""")
    for m in modals:
        print(f"Tag: {m['tag']}, ID: {m['id']}, Class: {m['className']}, Action: {m['action']}")
        print(m['html'])
        print("------------------------------------------")

    # 2. Inspect /admin/Controlbase/bBookUserMargin
    page.goto(f"{settings.admin_portal.base_url}/Controlbase/bBookUserMargin")
    page.wait_for_timeout(3000)
    print("\n=== BBOOK USER MARGIN PAGE THs ===")
    print("THs:", page.evaluate("() => Array.from(document.querySelectorAll('th')).map(e => e.innerText.trim())"))

    bbook_margin_btns = page.evaluate("""() => {
        return Array.from(document.querySelectorAll("button, a.btn, input[type='button'], input[type='submit']")).map(e => ({
            tag: e.tagName,
            text: e.innerText.trim(),
            id: e.id,
            className: e.className,
            dataTarget: e.getAttribute('data-target') || '',
            onclick: e.getAttribute('onclick') || ''
        }));
    }""")
    print("=== BUTTONS ON BBOOK USER MARGIN PAGE ===")
    for b in bbook_margin_btns:
        print(b)

    browser.close()
