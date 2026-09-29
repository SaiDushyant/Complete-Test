from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(storage_state="auth/auth_state_client.json")
    page = context.new_page()
    page.goto("https://stage.xtremenext.com/client-portal/", wait_until="domcontentloaded")
    page.wait_for_selector("header", timeout=15000)
    page.wait_for_timeout(2000)
    
    # 1. Click Support
    sup = page.locator("header button[title*='support' i]").first
    print("Support button found:", sup.get_attribute("title"))
    sup.click()
    page.wait_for_timeout(1000)
    
    body_text = page.locator("body").inner_text()
    for line in body_text.splitlines():
        if any(w in line.lower() for w in ["support", "faq", "help", "ticket", "center"]):
            print("Found line:", line.strip())

    fixed_divs = page.locator("div.fixed").all()
    print("Fixed divs count:", len(fixed_divs))
    for i, m in enumerate(fixed_divs):
        cls = m.get_attribute("class")
        print(f"Container {i}: class={cls}")
        snippet = m.evaluate("el => el.outerHTML")[:300]
        print("  HTML snippet:", snippet)

    browser.close()
