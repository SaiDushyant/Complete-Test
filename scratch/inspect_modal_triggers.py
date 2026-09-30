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
    
    # Check JS code or DOM for references to dragable_modal
    js_refs = page.evaluate("""() => {
        const scripts = Array.from(document.querySelectorAll("script")).map(s => s.src || s.innerText);
        const modal = document.querySelector("#dragable_modal");
        const allBtns = Array.from(document.querySelectorAll("button, a, .btn")).map(b => ({
            text: b.innerText.trim(),
            id: b.id,
            className: b.className,
            attributes: Array.from(b.attributes).map(a => `${a.name}="${a.value}"`).join(" ")
        }));
        return {
            modalStyle: modal ? modal.style.cssText : "no modal",
            allBtns: allBtns
        };
    }""")
    print("=== ALL BUTTON ATTRIBUTES ON BBOOK ===")
    for btn in js_refs['allBtns']:
        print(btn)

    browser.close()
