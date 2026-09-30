import sys
sys.path.insert(0, ".")
from playwright.sync_api import sync_playwright
from config.settings import settings
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage
from workflows.admin_portal.pages.admin_b_book_page import AdminBBookPage
from workflows.admin_portal.pages.admin_orders_page import AdminOrdersPage

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    # 1. Admin Login & Navigate to /admin/Controlbase/bBook
    admin_context = browser.new_context()
    admin_page = admin_context.new_page()
    admin_login = AdminLoginPage(admin_page)
    admin_login.navigate()
    admin_login.login()
    admin_page.wait_for_timeout(2000)

    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/bBook", wait_until="domcontentloaded")
    admin_page.wait_for_timeout(3000)

    # Click Buy Order (#buy)
    admin_page.click("button#buy, #buy")
    admin_page.wait_for_timeout(1000)

    # Select Account 10098 in #bbook_user_list
    bbook_user_select = admin_page.locator("select#bbook_user_list")
    options = bbook_user_select.evaluate("el => Array.from(el.options).map(o => ({text: o.text, val: o.value}))")
    acc_10098_val = None
    for opt in options:
        if "10098" in opt["text"]:
            acc_10098_val = opt["val"]
            break

    print("=== ACCOUNT 10098 OPTION VALUE ===")
    print(acc_10098_val)
    assert acc_10098_val is not None, f"Could not find Account 10098 in B-Book dropdown options: {options[:5]}"

    # Select Account 10098 in select#bbook_user_list (hidden select)
    bbook_user_select = admin_page.locator("select#bbook_user_list")
    bbook_user_select.evaluate(f"el => {{ el.value = '{acc_10098_val}'; el.dispatchEvent(new Event('change')); }}")
    admin_page.wait_for_timeout(500)

    # Select Symbol in select#symbols_list
    symbols_select = admin_page.locator("select#symbols_list")
    symbol_options = symbols_select.evaluate("el => Array.from(el.options).map(o => o.value)")
    target_symbol = symbol_options[1] if len(symbol_options) > 1 and symbol_options[1] else "EURUSD"
    symbols_select.evaluate(f"el => {{ el.value = '{target_symbol}'; el.dispatchEvent(new Event('change')); }}")
    admin_page.wait_for_timeout(500)

    # Fill Lot Size
    lot_input = admin_page.locator("#dragable_modal input.lotsize").first
    lot_input.fill("0.01")

    # Click Submit Order (button.placeorderx)
    submit_btn = admin_page.locator("#dragable_modal button.placeorderx").first
    print("Submit button text:", submit_btn.inner_text())
    submit_btn.click()
    admin_page.wait_for_timeout(3000)
    print("Successfully submitted B-Book Market Order for Account 10098!")

    browser.close()
