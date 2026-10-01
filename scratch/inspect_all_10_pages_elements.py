"""
Exhaustive DOM Inspection script for all 10 Admin Console Order & Report Pages.
Dumps all interactive controls (inputs, selects, buttons, links, table headers, modals, cards).
"""

from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from config.settings import settings
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage

def inspect_all_10_pages():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        login_page = AdminLoginPage(page)
        login_page.navigate()
        login_page.login()
        page.wait_for_timeout(2000)

        targets = [
            ("1. All Orders", "/admin/Controlbase/order/all"),
            ("2. Open Orders", "/admin/Controlbase/order/open"),
            ("3. Closed Orders", "/admin/Controlbase/order/closed"),
            ("4. A Book", "/admin/Controlbase/aBook"),
            ("5. B Book", "/admin/Controlbase/bBook"),
            ("6. A Book User Margin", "/admin/Controlbase/aBookUserMargin"),
            ("7. B Book User Margin", "/admin/Controlbase/bBookUserMargin"),
            ("8. Order Report", "/admin/Controlbase/OrderReport"),
            ("9. Book Report", "/admin/Controlbase/bookReport"),
            ("10. Order Edit Log", "/admin/Controlbase/orderEditLog")
        ]

        parts = urlsplit(settings.admin_portal.base_url)
        base = f"{parts.scheme}://{parts.netloc}"

        for name, path in targets:
            url = f"{base}{path}"
            print(f"\n=======================================================")
            print(f"INSPECTING PAGE: {name} ({url})")
            print(f"=======================================================")
            
            try:
                page.goto(url, timeout=15000, wait_until="domcontentloaded")
            except Exception as e:
                print(f"Navigation fallback for {url}: {e}")
                try:
                    page.goto(url, timeout=15000, wait_until="commit")
                except Exception:
                    pass
            page.wait_for_timeout(2000)

            # Dump page elements
            dom_data = page.evaluate("""() => {
                const selects = Array.from(document.querySelectorAll("select")).map(s => ({
                    id: s.id,
                    name: s.name,
                    class: s.className,
                    parent: s.parentElement ? s.parentElement.innerText.split("\\n")[0].trim() : "",
                    optionsCount: s.options.length,
                    optionsSample: Array.from(s.options).slice(0, 5).map(o => o.text.trim())
                }));

                const inputs = Array.from(document.querySelectorAll("input")).map(i => ({
                    id: i.id,
                    name: i.name,
                    type: i.type,
                    placeholder: i.placeholder,
                    class: i.className
                }));

                const buttons = Array.from(document.querySelectorAll("button, a.btn, a[id]")).map(b => ({
                    id: b.id,
                    text: b.innerText.trim(),
                    tag: b.tagName,
                    class: b.className
                })).filter(b => b.text || b.id);

                const headers = Array.from(document.querySelectorAll("#datatable thead th, table thead th")).map(th => th.innerText.trim());

                return {
                    title: document.title,
                    selects: selects,
                    inputs: inputs,
                    buttons: buttons,
                    headers: headers
                };
            }""")

            print(f"Title: {dom_data['title']}")
            print(f"Table Headers ({len(dom_data['headers'])}): {dom_data['headers']}")
            print(f"Dropdown Selects ({len(dom_data['selects'])}): {dom_data['selects']}")
            print(f"Input Fields ({len(dom_data['inputs'])}): {dom_data['inputs']}")
            print(f"Buttons & Action Links ({len(dom_data['buttons'])}): {dom_data['buttons']}")

        browser.close()

if __name__ == "__main__":
    inspect_all_10_pages()
