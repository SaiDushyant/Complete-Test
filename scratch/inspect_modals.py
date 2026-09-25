from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(storage_state="auth/auth_state_client.json")
    page = context.new_page()
    page.goto("https://stage.xtremenext.com/client-portal/", wait_until="domcontentloaded")
    page.wait_for_selector("header", timeout=15000)
    page.wait_for_timeout(2000)
    
    # 1. SUPPORT MODAL
    print("--- SUPPORT ---")
    support_btn = page.locator("header button[title*='support' i]").first
    support_btn.click()
    page.wait_for_timeout(1000)
    
    dialog = page.locator("div.fixed.inset-0, [role='dialog']").last
    d_text = dialog.inner_text().strip().replace("\n", " | ")[:300]
    print("Support text:", d_text)
    ctrls = dialog.locator("button, a").all()
    print(f"Support controls count: {len(ctrls)}")
    for i, c in enumerate(ctrls):
        tag = c.evaluate("el => el.tagName")
        txt = c.inner_text().strip().replace("\n", " ")
        title = c.get_attribute("title")
        aria = c.get_attribute("aria-label")
        href = c.get_attribute("href")
        print(f"  Ctrl {i}: <{tag}> text='{txt}', title='{title}', aria='{aria}', href='{href}'")
        
    # Close support modal
    close_btn = dialog.locator("button").first
    close_btn.click()
    page.wait_for_timeout(1000)
    
    # 2. CREATE ACCOUNT MODAL
    print("\n--- CREATE ACCOUNT ---")
    create_btn = page.locator("header button").filter(has_text="CREATE ACCOUNT").first
    create_btn.click()
    page.wait_for_timeout(1000)
    
    ca_dialog = page.locator("div.fixed.inset-0, [role='dialog']").last
    ca_text = ca_dialog.inner_text().strip().replace("\n", " | ")[:400]
    print("Create Account text:", ca_text)
    ca_ctrls = ca_dialog.locator("button, a, input, select").all()
    for i, c in enumerate(ca_ctrls):
        tag = c.evaluate("el => el.tagName")
        txt = c.inner_text().strip().replace("\n", " ")
        name = c.get_attribute("name")
        ctype = c.get_attribute("type")
        title = c.get_attribute("title")
        print(f"  CA Ctrl {i}: <{tag}> text='{txt}', name='{name}', type='{ctype}', title='{title}'")
        
    ca_close = ca_dialog.locator("button").first
    ca_close.click()
    page.wait_for_timeout(1000)

    # 3. ACCOUNT SWITCHER
    print("\n--- ACCOUNT SWITCHER ---")
    acct_btn = page.locator("header button").filter(has_text="Acct:").first
    acct_btn.click()
    page.wait_for_timeout(1000)
    acct_menu = page.locator("div.absolute, [role='menu']").all()
    for i, m in enumerate(acct_menu):
        txt = m.inner_text().strip().replace("\n", " | ")
        if len(txt) > 0 and any(k in txt.lower() for k in ["100", "acct", "demo", "real", "balance"]):
            print(f"  Acct menu {i}: text='{txt}'")
            for b in m.locator("button, div[role='menuitem'], a").all():
                item_txt = b.inner_text().strip().replace("\n", " ")
                print(f"    Item: text='{item_txt}'")

    browser.close()
