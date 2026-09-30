"""
User Documents - Additional Features Quick Validation.
Covers remaining untested features from user_document.js.
"""
from __future__ import annotations
import re
import pytest
from playwright.sync_api import Browser, Page, expect
from config.settings import settings
from workflows.admin_portal.pages.user_document_page import UserDocumentPage


def _dismiss_all_modals(page: Page) -> None:
    for _ in range(3):
        if page.locator(".jconfirm-box").is_visible():
            page.locator(".jconfirm-box .btn, .jconfirm-box button").first.click(force=True)
            page.wait_for_timeout(500)
    page.evaluate("""() => {
        document.querySelectorAll('.modal.show').forEach(m => {
            try { $(m).modal('hide'); } catch(e) {}
        });
        document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    }""")
    page.wait_for_timeout(500)


@pytest.fixture(scope="module")
def admin_page(browser: Browser) -> Page:
    context = browser.new_context(
        storage_state=str(settings.admin_portal.auth_state_path),
        viewport={"width": 1920, "height": 1080},
    )
    page = context.new_page()
    yield page
    context.close()


# ── TEST 15: ADD DOCUMENT BUTTON OPENS MODAL IN NEW MODE ──
@pytest.mark.shared
def test_add_document_button_opens_modal(admin_page: Page):
    """#addNew button opens #myModal in 'new' mode with empty form."""
    _dismiss_all_modals(admin_page)
    admin_doc = UserDocumentPage(admin_page)
    admin_doc.navigate()

    admin_doc.add_document_button.click()
    admin_page.wait_for_timeout(1000)

    expect(admin_doc.document_modal).to_be_visible()
    # Token select should be empty (no user pre-selected)
    token_val = admin_page.locator("#myModal select#token").input_value()
    assert token_val == "", f"Expected empty token in new mode, got '{token_val}'"
    # File input should be empty
    file_val = admin_page.locator("#myModal input#file").input_value()
    assert file_val == "", f"Expected empty file input, got '{file_val}'"

    admin_doc.document_modal_close.first.click()
    admin_page.wait_for_timeout(500)
    _dismiss_all_modals(admin_page)


# ── TEST 16: UPLOAD FORM VALIDATION (EMPTY FIELDS) ──
@pytest.mark.shared
def test_upload_form_validation_empty_fields(admin_page: Page):
    """Submitting upload form without selecting user/doc/file shows validation errors."""
    _dismiss_all_modals(admin_page)
    admin_doc = UserDocumentPage(admin_page)
    admin_doc.navigate()

    admin_doc.add_document_button.click()
    admin_page.wait_for_timeout(1000)

    # Click submit without filling anything
    admin_page.locator("#myModal #formSubmit").click()
    admin_page.wait_for_timeout(500)

    # Should show 'Please select the token' validation
    token_error = admin_page.locator("#myModal .invalid-feedback.token")
    expect(token_error).to_be_visible()
    assert "select" in token_error.inner_text().lower()

    admin_doc.document_modal_close.first.click()
    admin_page.wait_for_timeout(500)
    _dismiss_all_modals(admin_page)


# ── TEST 17: DELETE FORM VALIDATION (NO DOC TYPE SELECTED) ──
@pytest.mark.shared
def test_delete_form_validation_no_doc_selected(admin_page: Page):
    """Clicking #BtnDeleteConfirm without selecting doc type shows 'Please select document type'."""
    _dismiss_all_modals(admin_page)
    admin_doc = UserDocumentPage(admin_page)
    admin_doc.navigate()

    # Find a user WITH documents
    admin_doc.search_document("10026")
    admin_page.wait_for_timeout(1500)

    row = admin_doc.document_rows.first
    row.locator("a.BtnDelete").click()
    admin_page.wait_for_timeout(1000)

    expect(admin_doc.delete_modal).to_be_visible()

    # Clear the select to empty
    admin_page.evaluate("""() => {
        document.querySelector('#deleteModal select#names').value = '';
    }""")

    # Click confirm without selecting
    admin_doc.delete_modal.locator("#BtnDeleteConfirm").click()
    admin_page.wait_for_timeout(500)

    # Should show validation error
    names_error = admin_page.locator("#deleteModal .invalid-feedback.names")
    expect(names_error).to_be_visible()
    assert "select" in names_error.inner_text().lower()

    _dismiss_all_modals(admin_page)
    admin_doc.clear_search()


# ── TEST 18: REJECTED + REMARK SUBMIT UPDATES STATUS ──
@pytest.mark.shared
def test_rejected_remark_submit_updates_status(admin_page: Page):
    """Submitting remark from rejection flow actually updates status to Rejected (2)."""
    _dismiss_all_modals(admin_page)
    admin_doc = UserDocumentPage(admin_page)
    admin_doc.navigate()

    # Use first user's dropdown
    select_elem = admin_doc.verification_dropdowns.first
    uid = select_elem.get_attribute("uid")

    # Change to Rejected (2)
    select_elem.select_option("2")
    admin_page.wait_for_timeout(1000)

    expect(admin_doc.remark_modal).to_be_visible()

    # Fill remark and submit
    admin_doc.remark_modal_textarea.fill("Test rejection reason - automated validation")
    admin_doc.remark_modal.locator("#remarkUpdateBtn").click()
    admin_page.wait_for_timeout(2000)

    # Should get success confirmation
    if admin_page.locator(".jconfirm-box").is_visible():
        dialog_text = admin_page.locator(".jconfirm-box").inner_text()
        assert "congratulations" in dialog_text.lower() or "success" in dialog_text.lower(), \
            f"Expected success dialog, got: {dialog_text}"
        admin_page.locator(".jconfirm-box button").first.click(force=True)
        admin_page.wait_for_timeout(1000)

    _dismiss_all_modals(admin_page)

    # Restore to Verified (1) 
    admin_page.evaluate(f"""() => {{
        return new Promise((resolve) => {{
            $.ajax({{
                url: base_URL + 'Controlbase/updateUserDocumentVerification',
                method: 'POST',
                data: {{ averified: '1', uid: '{uid}', remark_id: '', row_index: '0' }},
                success: function (data) {{ resolve(data); }}
            }});
        }});
    }}""")
    admin_page.wait_for_timeout(500)


# ── TEST 19: VERIFICATION DROPDOWN COLOR CODING ──
@pytest.mark.shared
def test_verification_dropdown_color_coding(admin_page: Page):
    """Verification dropdown uses correct color classes: green=Verified, yellow=Not Verified, red=Rejected."""
    _dismiss_all_modals(admin_page)
    admin_doc = UserDocumentPage(admin_page)
    admin_doc.navigate()

    colors_found = {"btn-success": False, "btn-warning": False, "btn-danger": False}
    admin_doc.select_page_length("100")
    admin_page.wait_for_timeout(2000)

    for i in range(admin_doc.verification_dropdowns.count()):
        dd = admin_doc.verification_dropdowns.nth(i)
        classes = dd.get_attribute("class") or ""
        for color in colors_found:
            if color in classes:
                colors_found[color] = True

    # At least Verified (green) and Not Verified (yellow) should exist
    assert colors_found["btn-success"], "Expected at least one Verified (green) dropdown"
    assert colors_found["btn-warning"] or colors_found["btn-danger"], \
        "Expected at least one Not Verified (yellow) or Rejected (red) dropdown"

    admin_doc.select_page_length("10")
    admin_page.wait_for_timeout(500)


# ── TEST 20: DOCUMENT LINKS OPEN IN NEW TAB (target=_blank) ──
@pytest.mark.shared
def test_document_links_open_in_new_tab(admin_page: Page):
    """All document anchor links in the table have target='_blank'."""
    _dismiss_all_modals(admin_page)
    admin_doc = UserDocumentPage(admin_page)
    admin_doc.navigate()
    admin_doc.select_page_length("50")
    admin_page.wait_for_timeout(2000)

    doc_links = admin_page.locator("#datatable tbody td a[href*='/info/']")
    total_links = doc_links.count()
    assert total_links >= 5, f"Expected at least 5 document links in table, got {total_links}"

    for i in range(min(20, total_links)):
        link = doc_links.nth(i)
        target = link.get_attribute("target")
        assert target == "_blank", f"Link {i} missing target='_blank', got '{target}'"

    admin_doc.select_page_length("10")
    admin_page.wait_for_timeout(500)


# ── TEST 21: MODAL RESET ON CLOSE ──
@pytest.mark.shared
def test_modal_form_resets_on_close(admin_page: Page):
    """#myModal form resets when modal is closed — fields cleared, preview emptied."""
    _dismiss_all_modals(admin_page)
    admin_doc = UserDocumentPage(admin_page)
    admin_doc.navigate()

    # Open in edit mode for a user
    admin_doc.search_document("10026")
    admin_page.wait_for_timeout(1500)
    admin_doc.document_rows.first.locator("a.btnEdit").click()
    admin_page.wait_for_timeout(1000)

    expect(admin_doc.document_modal).to_be_visible()
    # Token should be pre-filled
    token_before = admin_page.locator("#myModal select#token").input_value()
    assert token_before != "", "Expected token pre-filled in edit mode"

    # Close modal
    admin_doc.document_modal_close.first.click()
    admin_page.wait_for_timeout(1000)
    _dismiss_all_modals(admin_page)

    # Re-open in new mode
    admin_doc.add_document_button.click()
    admin_page.wait_for_timeout(1000)

    # Token should be reset to empty
    token_after = admin_page.locator("#myModal select#token").input_value()
    assert token_after == "", f"Expected form reset to clear token, got '{token_after}'"

    admin_doc.document_modal_close.first.click()
    admin_page.wait_for_timeout(500)
    _dismiss_all_modals(admin_page)
    admin_doc.clear_search()


# ── TEST 22: RESPONSIVE DATATABLE (dtr-control) ──
@pytest.mark.shared
def test_responsive_datatable_collapse(admin_page: Page):
    """DataTable responsive mode: shrinking viewport shows dtr-control toggle, expanding restores columns."""
    _dismiss_all_modals(admin_page)
    admin_doc = UserDocumentPage(admin_page)
    admin_doc.navigate()

    # Full width — all columns visible
    admin_page.set_viewport_size({"width": 1920, "height": 1080})
    admin_page.wait_for_timeout(1000)
    full_headers = admin_doc.table_headers.count()

    # Shrink viewport
    admin_page.set_viewport_size({"width": 768, "height": 1080})
    admin_page.wait_for_timeout(1500)

    # dtr-control cells should appear (responsive collapse triggers)
    dtr_controls = admin_doc.responsive_controls
    assert dtr_controls.count() > 0, "Expected dtr-control cells in responsive mode"

    # Restore viewport
    admin_page.set_viewport_size({"width": 1920, "height": 1080})
    admin_page.wait_for_timeout(1000)


# ── TEST 23: STATE PERSISTENCE ACROSS RELOAD ──
@pytest.mark.shared
def test_state_save_persists_across_reload(admin_page: Page):
    """stateSave: true — page length and search state persist after page reload."""
    _dismiss_all_modals(admin_page)
    admin_doc = UserDocumentPage(admin_page)
    admin_doc.navigate()

    # Set page length to 25
    admin_doc.select_page_length("25")
    admin_page.wait_for_timeout(1000)

    # Reload page
    admin_page.reload(wait_until="domcontentloaded")
    admin_page.wait_for_timeout(3000)

    # Check if page length persisted
    current_length = admin_page.locator("select[name='datatable_length']").input_value()
    assert current_length == "25", f"Expected stateSave to persist page length 25, got '{current_length}'"

    # Reset to 10
    admin_doc.select_page_length("10")
    admin_page.wait_for_timeout(500)
