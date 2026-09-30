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

    page.goto("https://stage.xtremenext.com/admin/Controlbase/bBook", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    
    print("=== DRAGABLE MODAL HTML ===")
    dragable_modal = page.locator("#dragable_modal")
    if dragable_modal.count() > 0:
        print(dragable_modal.evaluate("el => el.outerHTML"))

    print("=== HOW IS DRAGABLE MODAL OPENED? (LOOKING FOR TRIGGER BUTTONS) ===")
    triggers = page.evaluate("""() => {
        return Array.from(document.querySelectorAll("[data-target='#dragable_modal'], [data-bs-target='#dragable_modal'], .btnPlaceOrder, button.place-order, a:has-text('Order')")).map(e => ({
            tag: e.tagName, text: e.innerText.trim(), id: e.id, className: e.className, outerHTML: e.outerHTML
        }));
    }""")
    for t in triggers:
        print(t)

    browser.close()
