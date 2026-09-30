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
    
    # Click Buy Order button (#buy)
    page.click("button#buy, #buy")
    page.wait_for_timeout(1500)

    print("=== SELECTS & INPUTS INSIDE DRAGABLE_MODAL ===")
    modal_inputs = page.evaluate("""() => {
        const modal = document.querySelector("#dragable_modal");
        if (!modal) return "No modal found";
        return Array.from(modal.querySelectorAll("select, input, button")).map(e => ({
            tag: e.tagName,
            type: e.type || '',
            name: e.name || '',
            id: e.id || '',
            className: e.className || '',
            placeholder: e.placeholder || '',
            value: e.value || '',
            options: e.tagName === 'SELECT' ? Array.from(e.options).map(o => ({text: o.text.trim(), val: o.value})).slice(0, 10) : []
        }));
    }""")
    for i in modal_inputs:
        print(i)

    browser.close()
