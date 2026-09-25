from playwright.async_api import Page


async def extract_elements(
    page: Page,
) -> list:
    """
    Extract comprehensive and sanitized DOM element metadata from the current HTML page.
    Excludes sensitive credential values (passwords, auth tokens) from output.
    """

    elements = await page.locator("*").evaluate_all(
        """
        elements => {
            const SENSITIVE_KEY_PATTERN = /(?:password|passwd|secret|token|auth|api_key|credit|cvv)/i;

            function getText(element) {
                return (element.innerText || "")
                    .trim()
                    .replace(/\\s+/g, " ")
                    .substring(0, 500);
            }

            function getDirectText(element) {
                let direct = "";
                for (const node of element.childNodes) {
                    if (node.nodeType === 3 /* Node.TEXT_NODE */) {
                        direct += node.nodeValue;
                    }
                }
                return direct.trim().replace(/\\s+/g, " ").substring(0, 500);
            }

            function getSanitizedAttributes(element) {
                const attributes = {};
                const tag = element.tagName.toLowerCase();
                const isPasswordInput = tag === "input" && (element.type || "").toLowerCase() === "password";

                for (const attr of element.attributes) {
                    const name = attr.name;
                    let val = attr.value;

                    // Redact sensitive attributes (e.g., value on password fields, auth tokens)
                    if (isPasswordInput && name === "value") {
                        val = "[REDACTED]";
                    } else if (SENSITIVE_KEY_PATTERN.test(name) && val.length > 0) {
                        val = "[REDACTED]";
                    }

                    attributes[name] = val;
                }
                return attributes;
            }

            function getBoundingBox(element) {
                const rect = element.getBoundingClientRect();
                return {
                    x: Math.round(rect.x * 100) / 100,
                    y: Math.round(rect.y * 100) / 100,
                    width: Math.round(rect.width * 100) / 100,
                    height: Math.round(rect.height * 100) / 100
                };
            }

            function isVisible(element) {
                try {
                    const style = window.getComputedStyle(element);
                    const rect = element.getBoundingClientRect();
                    return (
                        style.display !== "none" &&
                        style.visibility !== "hidden" &&
                        style.opacity !== "0" &&
                        rect.width > 0 &&
                        rect.height > 0
                    );
                } catch (_) {
                    return false;
                }
            }

            function generateLocatorAndUniqueness(element) {
                const tag = element.tagName.toLowerCase();

                // 1. ID
                if (element.id && typeof element.id === "string" && element.id.trim().length > 0) {
                    const idSelector = "#" + CSS.escape(element.id.trim());
                    try {
                        const count = document.querySelectorAll(idSelector).length;
                        return { locator: idSelector, is_unique: count === 1 };
                    } catch (_) {}
                }

                // 2. data-testid
                const testId = element.getAttribute("data-testid");
                if (testId) {
                    const testIdSelector = `[data-testid="${testId.replace(/"/g, '\\\\"')}"]`;
                    try {
                        const count = document.querySelectorAll(testIdSelector).length;
                        return { locator: testIdSelector, is_unique: count === 1 };
                    } catch (_) {}
                }

                // 3. Name attribute for form controls
                const name = element.getAttribute("name");
                if (name && ["input", "textarea", "select", "button", "form"].includes(tag)) {
                    const nameSelector = `${tag}[name="${name.replace(/"/g, '\\\\"')}"]`;
                    try {
                        const count = document.querySelectorAll(nameSelector).length;
                        return { locator: nameSelector, is_unique: count === 1 };
                    } catch (_) {}
                }

                // 4. aria-label
                const ariaLabel = element.getAttribute("aria-label");
                // 4. aria-label
                const ariaLabel = element.getAttribute("aria-label");
                if (ariaLabel && ariaLabel.trim().length > 0 && ariaLabel.length < 80) {
                    const ariaSelector = `[aria-label="${ariaLabel.trim().replace(/"/g, '\\\\')}"]`;
                    try {
                        const count = document.querySelectorAll(ariaSelector).length;
                        return { locator: ariaSelector, is_unique: count === 1 };
                    } catch (_) {}
                }

                // 5. Semantic data attributes (data-symbol, data-offer, data-bid, data-page, data-nav, data-view)
                for (const attrKey of ["data-symbol", "data-offer", "data-bid", "data-nav", "data-page", "data-view"]) {
                    const attrVal = element.getAttribute(attrKey);
                    if (attrVal && attrVal.length > 0 && attrVal.length < 60) {
                        const sel = `[${attrKey}="${attrVal.replace(/"/g, '\\\\')}"]`;
                        try {
                            const count = document.querySelectorAll(sel).length;
                            if (count === 1) {
                                return { locator: sel, is_unique: true };
                            }
                        } catch (_) {}
                    }
                }

                // 6. Tag + stable class combination (filtering volatile/flash classes)
                if (element.classList && element.classList.length > 0) {
                    const VOLATILE_CLASSES = new Set([
                        "redx", "bluex", "greenx", "redx-btn", "bluex-btn", "greenx-btn",
                        "flash-red", "flash-green", "fadeIn", "fadeOut", "fade-in", "fade-out",
                        "animsition-loading", "animsition", "animated", "show", "collapsing",
                        "watchlist-skeleton", "watchlist-initial-loading", "up", "down",
                        "active", "hover"
                    ]);
                    const classList = Array.from(element.classList).filter(c => c && !c.includes(":") && !VOLATILE_CLASSES.has(c));
                    if (classList.length > 0) {
                        const classSelector = tag + "." + classList.map(c => CSS.escape(c)).join(".");
                        try {
                            const count = document.querySelectorAll(classSelector).length;
                            return { locator: classSelector, is_unique: count === 1 };
                        } catch (_) {}
                    }
                }

                // 7. Anchor href locator
                if (tag === "a") {
                    const href = element.getAttribute("href");
                    if (href && href.length > 0 && href.length < 100) {
                        const hrefSelector = `a[href="${href.replace(/"/g, '\\\\')}"]`;
                        try {
                            const count = document.querySelectorAll(hrefSelector).length;
                            return { locator: hrefSelector, is_unique: count === 1 };
                        } catch (_) {}
                    }
                }

                // 8. Fallback
                return { locator: tag, is_unique: false };
            }

            return elements.map((element, index) => {
                const tag = element.tagName.toLowerCase();
                const isFormElement = ["input", "textarea", "select", "button"].includes(tag);
                const isPassword = tag === "input" && (element.type || "").toLowerCase() === "password";
                const isSensitiveName = SENSITIVE_KEY_PATTERN.test(element.name || "") || SENSITIVE_KEY_PATTERN.test(element.id || "");

                const { locator, is_unique } = generateLocatorAndUniqueness(element);

                const result = {
                    index: index,
                    tag: tag,
                    id: element.id || null,
                    classes: typeof element.className === "string" && element.className.trim().length > 0 ? element.className.trim() : null,
                    text: getText(element),
                    direct_text: getDirectText(element),
                    is_leaf: element.children.length === 0,
                    attributes: getSanitizedAttributes(element),
                    visible: isVisible(element),
                    locator: locator,
                    is_unique: is_unique,
                    in_table_cell: Boolean(element.closest && element.closest("td, th")),
                    role: element.getAttribute("role") || null,
                    aria_label: element.getAttribute("aria-label") || null,
                    aria_describedby: element.getAttribute("aria-describedby") || null,
                    bounding_box: getBoundingBox(element)
                };

                if (isFormElement) {
                    result.enabled = !element.disabled;
                }

                // Input element details
                if (tag === "input") {
                    result.input_type = element.type || "text";
                    result.name = element.name || null;
                    result.placeholder = element.placeholder || null;
                    result.checked = Boolean(element.checked);

                    if (isPassword || isSensitiveName) {
                        result.value = "[REDACTED]";
                    } else {
                        result.value = element.value !== undefined ? String(element.value).substring(0, 300) : null;
                    }
                }

                // Textarea
                if (tag === "textarea") {
                    result.name = element.name || null;
                    result.placeholder = element.placeholder || null;
                    if (isSensitiveName) {
                        result.value = "[REDACTED]";
                    } else {
                        result.value = element.value !== undefined ? String(element.value).substring(0, 300) : null;
                    }
                }

                // Links
                if (tag === "a") {
                    result.href = element.href || element.getAttribute("href") || null;
                    result.link_text = getText(element);
                }

                // Images
                if (tag === "img") {
                    result.src = element.src || element.getAttribute("src") || null;
                    result.alt = element.alt || null;
                }

                // Select
                if (tag === "select") {
                    result.name = element.name || null;
                    result.value = element.value || null;
                    try {
                        const selectedOpt = element.options ? element.options[element.selectedIndex] : null;
                        result.selected_text = selectedOpt ? selectedOpt.text : null;
                    } catch (_) {
                        result.selected_text = null;
                    }
                }

                // Button
                if (tag === "button") {
                    result.button_type = element.type || "submit";
                    result.name = element.name || null;
                }

                return result;
            });
        }
        """
    )

    return elements
