from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(storage_state="auth/auth_state_client.json")
    page = context.new_page()
    page.goto("https://stage.xtremenext.com/client-portal/", wait_until="domcontentloaded")
    page.wait_for_selector("header", timeout=15000)
    page.wait_for_timeout(2000)
    
    print("=== HEADER SEARCH INPUT ===")
    search = page.locator("header input")
    print("Search count:", search.count())
    if search.count() > 0:
        placeholder = search.first.get_attribute("placeholder")
        print("Placeholder:", placeholder)
        
    print("\n=== SIDEBAR TOGGLE ===")
    toggle = page.locator("header button[title*='menu' i]")
    print("Toggle buttons:", toggle.count())
    for i, t in enumerate(toggle.all()):
        print(f"Toggle {i}: title={t.get_attribute('title')}, aria={t.get_attribute('aria-label')}")

    print("\n=== THEME TOGGLE ===")
    theme = page.locator("header button[title*='theme' i]")
    if theme.count() > 0:
        print("Theme button title:", theme.first.get_attribute("title"))

    print("\n=== NOTIFICATIONS ===")
    notif = page.locator("header button[title*='notification' i]")
    if notif.count() > 0:
        print("Notif title:", notif.first.get_attribute("title"))
        notif.first.click()
        page.wait_for_timeout(1000)
        popups = page.locator("[role='dialog'], [role='menu'], div.fixed, div.absolute").all()
        for i, pop in enumerate(popups):
            txt = pop.inner_text().strip()[:150].replace("\n", " | ")
            if any(k in txt.lower() for k in ["notification", "read", "unread"]):
                print(f"Notif pop {i}: text={txt}")
                buttons = pop.locator("button").all()
                for b in buttons:
                    print(f"  Notif button: text='{b.inner_text().strip()}', title='{b.get_attribute('title')}'")
        notif.first.click()
        page.wait_for_timeout(500)

    print("\n=== SUPPORT ===")
    support = page.locator("header button[title*='support' i]")
    if support.count() > 0:
        print("Support title:", support.first.get_attribute("title"))
        support.first.click()
        page.wait_for_timeout(1000)
        modals = page.locator("[role='dialog'], div.fixed").all()
        for i, m in enumerate(modals):
            txt = m.inner_text().strip()[:200].replace("\n", " | ")
            if any(k in txt.lower() for k in ["support", "faq", "ticket", "help", "account"]):
                print(f"Support modal {i}: text={txt}")
                buttons = m.locator("button, a").all()
                for b in buttons:
                    txt_clean = b.inner_text().strip().replace("\n", " ")
                print(f"  Support control: tag={b.evaluate('el => el.tagName')}, text='{txt_clean}', href={b.get_attribute('href')}")
        # Close support modal
        close_btn = page.locator("button[aria-label*='close' i], button[title*='close' i], button:has-text('✕'), button:has-text('Close')")
        if close_btn.count() > 0:
            close_btn.first.click()
        else:
            page.keyboard.press("Escape")
        page.wait_for_timeout(500)

    print("\n=== ACCOUNT SWITCHER ===")
    acct = page.locator("header button").filter(has_text="Acct:")
    if acct.count() > 0:
        print("Acct button text:", acct.first.inner_text().strip())
        acct.first.click()
        page.wait_for_timeout(1000)
        menus = page.locator("[role='menu'], [role='listbox'], div.absolute").all()
        for i, m in enumerate(menus):
            txt = m.inner_text().strip()[:200].replace("\n", " | ")
            if any(k in txt.lower() for k in ["acct", "balance", "100", "account"]):
                print(f"Acct dropdown {i}: {txt}")
        acct.first.click()
        page.wait_for_timeout(500)

    print("\n=== CREATE ACCOUNT POPUP ===")
    create_btn = page.locator("header button").filter(has_text="CREATE ACCOUNT")
    if create_btn.count() > 0:
        create_btn.first.click()
        page.wait_for_timeout(1000)
        modals = page.locator("[role='dialog'], div.fixed").all()
        for i, m in enumerate(modals):
            txt = m.inner_text().strip()[:300].replace("\n", " | ")
            if any(k in txt.lower() for k in ["account", "create", "demo", "live", "leverage", "type"]):
                print(f"Create Acct modal {i}: text={txt}")
                inputs = m.locator("input, select").all()
                for inp in inputs:
                    print(f"  Field: tag={inp.evaluate('el => el.tagName')}, name={inp.get_attribute('name')}, type={inp.get_attribute('type')}")
                buttons = m.locator("button").all()
                for b in buttons:
                    b_txt = b.inner_text().strip().replace("\n", " ")
                print(f"  Modal button: text='{b_txt}', title='{b.get_attribute('title')}'")

    print("\n=== PROFILE / LOGOUT ===")
    logout_btn = page.locator("header button[title*='logout' i]")
    print("Logout count:", logout_btn.count(), "title:", logout_btn.first.get_attribute("title") if logout_btn.count() > 0 else None)
    avatar = page.locator("header img, header .avatar, header [class*='avatar'], header [class*='profile']")
    print("Avatar/Profile elements count in header:", avatar.count())
    for i, a in enumerate(avatar.all()):
        print(f"Avatar {i}: tag={a.evaluate('el => el.tagName')}, class={a.get_attribute('class')}")

    browser.close()
