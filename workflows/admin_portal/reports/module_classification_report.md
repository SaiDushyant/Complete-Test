# Admin Portal - All 282 Test Cases Classified by Module

**Total Tests**: 282 | **Total Passed**: 282 | **Status**: 100% Passed

---

## Summary by Module

| # | Module Name | Test File | Test Count | Status |
|---|---|---|:---:|:---:|
| 1 | Sidebar & Navigation Module | `test_admin_example.py` | 10 | **PASSED** |
| 2 | Dashboard Content & Analytics Module | `test_admin_dashboard_content.py` | 5 | **PASSED** |
| 3 | Copy Trading Module | `test_admin_copy_trading.py` | 19 | **PASSED** |
| 4 | Private Copy Trading Module | `test_admin_private_copy_trading.py` | 24 | **PASSED** |
| 5 | MAM (Multi-Account Manager) Module | `test_admin_mam.py` | 21 | **PASSED** |
| 6 | PAMM Module | `test_admin_pamm.py` | 20 | **PASSED** |
| 7 | Leads Report Module | `test_admin_leads_report.py` | 19 | **PASSED** |
| 8 | Manage Leads Module | `test_admin_manage_leads.py` | 20 | **PASSED** |
| 9 | LP Transaction Module | `test_admin_lp_transaction.py` | 16 | **PASSED** |
| 10 | LP Commission Log Module | `test_admin_lp_commission_log.py` | 16 | **PASSED** |
| 11 | LP Execution Config Module | `test_admin_lp_execution_config.py` | 12 | **PASSED** |
| 12 | User Management Module | `test_admin_user_management.py` | 23 | **PASSED** |
| 13 | Account Requests Module | `test_admin_account_requests.py` | 15 | **PASSED** |
| 14 | User Document Verification Module | `test_admin_user_document.py` | 16 | **PASSED** |
| 15 | Role & Permission Module | `test_admin_role_permission.py` | 14 | **PASSED** |
| 16 | Manager User Management Module | `test_admin_manager_user_management.py` | 14 | **PASSED** |
| 17 | Manager Management Module | `test_admin_manager_management.py` | 18 | **PASSED** |

---

## Detailed Module Breakdown

### 1. Sidebar & Navigation Module (10 Tests)
**File:** [test_admin_example.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_example.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_login_page_renders_form_elements` | The Admin login page displays the username and password fields. | **PASSED** |
| 2 | `test_admin_can_view_management_dashboard` | The administrator can log in and open the Admin Dashboard. | **PASSED** |
| 3 | `test_admin_user_management_page_loads` | The Admin User Management page opens and displays the users table. | **PASSED** |
| 4 | `test_admin_user_management_has_create_user_action` | The User Management page shows the Add User/Create Account button. | **PASSED** |
| 5 | `test_admin_user_management_search_is_available` | The User Management page shows the search field. | **PASSED** |
| 6 | `test_admin_profile_menu_shows_admin_details` | The Admin profile menu opens and shows the admin name and role. | **PASSED** |
| 7 | `test_admin_profile_menu_has_logout_link` | The Admin profile menu contains a working Logout link. | **PASSED** |
| 8 | `test_admin_theme_toggle_is_visible` | The Admin Dashboard displays the theme switch button. | **PASSED** |
| 9 | `test_admin_notifications_are_available` | The Admin Dashboard displays notifications and the Mark all read option. | **PASSED** |
| 10 | `test_admin_sidebar_menu_button_is_visible` | The Admin Dashboard displays the button used to open the sidebar menu. | **PASSED** |

### 2. Dashboard Content & Analytics Module (5 Tests)
**File:** [test_admin_dashboard_content.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_dashboard_content.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_dashboard_kpi_values_are_numeric` | The Dashboard KPI cards display valid numeric values. | **PASSED** |
| 2 | `test_admin_dashboard_charts_are_rendered` | The Dashboard displays both the Deposits vs Withdrawals and A-Book vs B-Book charts. | **PASSED** |
| 3 | `test_admin_dashboard_heading_is_displayed` | The Admin Dashboard displays the Dashboard heading. | **PASSED** |
| 4 | `test_admin_dashboard_main_kpi_cards_are_displayed` | The Dashboard displays the Deposit, Withdrawal, and User KPI cards. | **PASSED** |
| 5 | `test_admin_dashboard_book_sections_are_displayed` | The Dashboard displays both the A-Book and B-Book sections. | **PASSED** |

### 3. Copy Trading Module (19 Tests)
**File:** [test_admin_copy_trading.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_copy_trading.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_copy_trading_page_loads_and_displays_heading` | The Admin Copy Trading page opens and displays the Copy Trading heading. | **PASSED** |
| 2 | `test_admin_copy_trading_table_headers_and_columns_are_valid` | The Copy Trading table displays all 6 expected column headers. | **PASSED** |
| 3 | `test_admin_copy_trading_client_portal_requests_does_not_redirect` | Clicking Client Portal Requests opens the modal dialog and stays on the Admin panel without redirecting to the client portal. | **PASSED** |
| 4 | `test_admin_copy_trading_datatable_controls_are_present` | The Copy Trading page displays the table length dropdown and search filter. | **PASSED** |
| 5 | `test_admin_copy_trading_table_rows_have_valid_data` | The Copy Trading table contains rows with valid numeric account IDs and action buttons. | **PASSED** |
| 6 | `test_admin_copy_trading_search_filters_rows` | The Copy Trading search input filters the data rows. | **PASSED** |
| 7 | `test_admin_copy_trading_followers_list_action` | Clicking Followers List opens the followers details or empty report alert. | **PASSED** |
| 8 | `test_admin_copy_trading_topbar_branding_and_title` | The Copy Trading topbar renders the brand logo, page title, and sidebar toggle button. | **PASSED** |
| 9 | `test_admin_copy_trading_theme_toggle_switches_modes` | The theme switch button toggles the layout mode between dark and light. | **PASSED** |
| 10 | `test_admin_copy_trading_notifications_dropdown_and_items` | The notifications button opens the dropdown menu showing items and the Mark all read option. | **PASSED** |
| 11 | `test_admin_copy_trading_profile_dropdown_and_logout_link` | The user profile menu displays the admin details and a working Logout link. | **PASSED** |
| 12 | `test_admin_copy_trading_table_column_sorting` | Clicking table column headers updates the sorting state and re-orders records. | **PASSED** |
| 13 | `test_admin_copy_trading_table_pagination_and_info` | The Copy Trading table displays status entry info and pagination controls. | **PASSED** |
| 14 | `test_admin_copy_trading_responsive_row_expansion` | Clicking the responsive row toggle expands the child row with trader action details. | **PASSED** |
| 15 | `test_admin_copy_trading_edit_trader_modal_opens` | Clicking the edit pencil opens the Edit Trader modal with name and fee inputs. | **PASSED** |
| 16 | `test_admin_copy_trading_requests_modal_table_structure_and_headers` | The Client Portal Requests modal displays the requests table and 7 columns. | **PASSED** |
| 17 | `test_admin_copy_trading_requests_modal_rows_and_actions` | The Client Portal Requests table shows pending requests with Approve and Reject buttons. | **PASSED** |
| 18 | `test_admin_copy_trading_page_length_to_10_generates_3_pages` | Selecting 10 entries updates the table to 1-10 of 21 and generates 3 pagination pages. | **PASSED** |
| 19 | `test_admin_copy_trading_responsive_plus_symbol_opens_followers_inner_table` | In responsive or zoomed view, clicking (+) reveals Followers List and opens the inner table. | **PASSED** |

### 4. Private Copy Trading Module (24 Tests)
**File:** [test_admin_private_copy_trading.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_private_copy_trading.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_private_copy_trading_page_loads_and_displays_heading` | The Admin Private Copy Trading page opens and displays the Manage Private Copier heading. | **PASSED** |
| 2 | `test_admin_private_copy_trading_topbar_branding_and_title` | The Private Copy Trading topbar renders the brand logo, page title, and sidebar toggle button. | **PASSED** |
| 3 | `test_admin_private_copy_trading_theme_toggle_switches_modes` | The theme switch button on Private Copy Trading toggles the layout mode between dark and light. | **PASSED** |
| 4 | `test_admin_private_copy_trading_notifications_dropdown` | The notifications button on Private Copy Trading opens the dropdown menu and Mark all read link. | **PASSED** |
| 5 | `test_admin_private_copy_trading_profile_dropdown_and_logout_link` | The user profile menu on Private Copy Trading displays the admin credentials and a working Logout link. | **PASSED** |
| 6 | `test_admin_private_copy_trading_table_headers_and_columns_are_valid` | All 8 Private Copy Trading table column headers are rendered correctly. | **PASSED** |
| 7 | `test_admin_private_copy_trading_table_rows_and_data_structure` | The table rows render valid serial numbers, master names, accounts, and slaves preview. | **PASSED** |
| 8 | `test_admin_private_copy_trading_search_filters_by_master_name` | Typing a master name into the search bar filters the rows to matching records. | **PASSED** |
| 9 | `test_admin_private_copy_trading_search_filters_by_master_account_id` | Searching by Master Account ID isolates the matching private copier entry. | **PASSED** |
| 10 | `test_admin_private_copy_trading_search_filters_by_slave_details` | Searching by slave follower details isolates the corresponding master row. | **PASSED** |
| 11 | `test_admin_private_copy_trading_search_nonexistent_query_shows_empty_state` | Searching for a nonexistent term shows no matching records and zero entries status. | **PASSED** |
| 12 | `test_admin_private_copy_trading_table_column_sorting` | Clicking sortable headers toggles column sorting between ascending and descending. | **PASSED** |
| 13 | `test_admin_private_copy_trading_pagination_and_info_status` | DataTable info status and pagination controls render active status correctly. | **PASSED** |
| 14 | `test_admin_private_copy_trading_length_dropdown_selection` | Changing page length dropdown updates table length options (10, 25, 50, 100). | **PASSED** |
| 15 | `test_admin_private_copy_trading_responsive_control_expansion` | Responsive dtr-control button expands collapsed row details. | **PASSED** |
| 16 | `test_admin_private_copy_trading_create_copier_button_and_modal` | Clicking Create Copier reveals the Private Copy Trading configuration modal and form. | **PASSED** |
| 17 | `test_admin_private_copy_trading_datatable_controls_are_present` | The Private Copy Trading DataTable displays length select and search input controls. | **PASSED** |
| 18 | `test_admin_private_copy_trading_view_slaves_modal_opens_and_closes` | Clicking View Slaves opens the Slave Accounts modal and displays the slaves list. | **PASSED** |
| 19 | `test_admin_private_copy_trading_create_copier_modal_form_fields_and_inputs` | The Create Copier modal renders search inputs, copy type select, and direction radios. | **PASSED** |
| 20 | `test_admin_private_copy_trading_create_copier_copy_type_multiplier_toggle` | Selecting Multiplier Wise dynamically displays the Multiplier Value input field. | **PASSED** |
| 21 | `test_admin_private_copy_trading_create_copier_trading_direction_radio_toggle` | Toggling Trading Direction switches selection between Normal Copy and Reverse Copy. | **PASSED** |
| 22 | `test_admin_private_copy_trading_create_copier_empty_submission_validation` | Submitting an empty form is prevented and the configuration modal remains open. | **PASSED** |
| 23 | `test_admin_private_copy_trading_slave_accounts_modal_content_and_rows` | The Slave Accounts modal renders rows displaying slave index, name, and account numbers. | **PASSED** |
| 24 | `test_admin_private_copy_trading_edit_copier_modal_opens` | Clicking the edit pencil icon opens the Private Copy Trading configuration modal. | **PASSED** |

### 5. MAM (Multi-Account Manager) Module (21 Tests)
**File:** [test_admin_mam.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_mam.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_mam_topbar_branding_and_title` | The Manage MAM topbar renders the brand logo, page title, and sidebar toggle button. | **PASSED** |
| 2 | `test_admin_mam_topbar_sidebar_toggle_action` | Clicking the vertical menu toggle button dynamically collapses or expands the admin sidebar. | **PASSED** |
| 3 | `test_admin_mam_theme_toggle_switches_modes` | The theme switch button on Manage MAM toggles the layout mode between dark and light. | **PASSED** |
| 4 | `test_admin_mam_notifications_dropdown` | The notifications button on Manage MAM opens the dropdown menu and Mark all read link. | **PASSED** |
| 5 | `test_admin_mam_profile_dropdown_and_logout_link` | The user profile menu on Manage MAM displays the admin credentials and a working Logout link. | **PASSED** |
| 6 | `test_admin_mam_table_card_and_datatable_controls` | The Manage MAM card wrapper displays length select dropdown (10, 25, 50, 100) and search filter. | **PASSED** |
| 7 | `test_admin_mam_table_headers_and_columns_are_valid` | All 6 Manage MAM table column headers and sortable configurations are rendered correctly. | **PASSED** |
| 8 | `test_admin_mam_table_rows_data_integrity` | The Manage MAM table rows display valid sequential S.No, MAM name edit buttons, account IDs, and tokens. | **PASSED** |
| 9 | `test_admin_mam_edit_mam_name_modal_opens_and_closes` | Clicking the MAM name edit pencil opens the MAM Details modal with name prefilled and dismisses safely. | **PASSED** |
| 10 | `test_admin_mam_followers_list_zero_count_shows_alert` | Clicking Followers List on a MAM with zero followers displays the No followers assigned alert. | **PASSED** |
| 11 | `test_admin_mam_followers_list_nonzero_count_expands_subtable` | Clicking Followers List on a MAM with followers expands the inner subtable with follower details. | **PASSED** |
| 12 | `test_admin_mam_edit_mam_share_modal_opens_and_closes` | Clicking edit MAM share inside the subtable opens the User Management modal with share percentage. | **PASSED** |
| 13 | `test_admin_mam_page_length_selection` | Changing page length dropdown updates visible row count and DataTable pagination info. | **PASSED** |
| 14 | `test_admin_mam_search_filters_by_mam_name` | Entering a MAM manager name into the search bar filters the rows correctly. | **PASSED** |
| 15 | `test_admin_mam_search_filters_by_account_id` | Searching by Account ID isolates the matching MAM manager record. | **PASSED** |
| 16 | `test_admin_mam_search_nonexistent_query_shows_empty_state` | Searching for a nonexistent term shows no matching records and zero entries status. | **PASSED** |
| 17 | `test_admin_mam_table_column_sorting` | Clicking sortable headers toggles column sorting between ascending and descending. | **PASSED** |
| 18 | `test_admin_mam_table_pagination_and_info` | DataTable info status and pagination controls render active status correctly. | **PASSED** |
| 19 | `test_admin_mam_page_loads_and_displays_heading` | The Admin Manage MAM page opens and displays the Manage MAM heading. | **PASSED** |
| 20 | `test_admin_mam_requests_button_and_modal_structure` | The MAM Requests button displays pending count and opens the requests approval modal. | **PASSED** |
| 21 | `test_admin_mam_edit_mam_name_empty_submission_validation` | Submitting an empty MAM name is prevented and the MAM Details modal remains open. | **PASSED** |

### 6. PAMM Module (20 Tests)
**File:** [test_admin_pamm.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_pamm.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_pamm_topbar_branding_and_title` | The Manage PAMM topbar renders the brand logo, page title, and sidebar toggle button. | **PASSED** |
| 2 | `test_admin_pamm_topbar_sidebar_toggle_action` | Clicking the vertical menu toggle button on Manage PAMM dynamically collapses or expands the sidebar. | **PASSED** |
| 3 | `test_admin_pamm_theme_toggle_switches_modes` | The theme switch button on Manage PAMM toggles the layout mode between dark and light. | **PASSED** |
| 4 | `test_admin_pamm_notifications_dropdown` | The notifications button on Manage PAMM opens the dropdown menu, badge, and Mark all read link. | **PASSED** |
| 5 | `test_admin_pamm_profile_dropdown_and_logout_link` | The user profile menu on Manage PAMM displays admin details and a working Logout link. | **PASSED** |
| 6 | `test_admin_pamm_page_loads_and_displays_heading` | The Admin Manage PAMM page opens and displays the Manage PAMM heading. | **PASSED** |
| 7 | `test_admin_pamm_requests_button_and_modal_structure` | The PAMM Requests button displays pending count badge and opens the requests approval modal. | **PASSED** |
| 8 | `test_admin_pamm_table_card_and_datatable_controls` | The Manage PAMM card wrapper displays length select dropdown (10, 25, 50, 100) and search filter. | **PASSED** |
| 9 | `test_admin_pamm_table_headers_and_columns_are_valid` | All 6 Manage PAMM table column headers and sortable configurations are rendered correctly. | **PASSED** |
| 10 | `test_admin_pamm_table_rows_data_integrity` | The Manage PAMM table rows display valid sequential S.No, PAMM name edit buttons, account IDs, and tokens. | **PASSED** |
| 11 | `test_admin_pamm_edit_pamm_name_empty_submission_validation` | Submitting an empty PAMM name is prevented and the PAMM Details modal remains open. | **PASSED** |
| 12 | `test_admin_pamm_followers_list_zero_count_shows_alert` | Clicking Followers List on a PAMM with zero followers displays the No followers assigned alert. | **PASSED** |
| 13 | `test_admin_pamm_followers_list_nonzero_count_expands_subtable` | Clicking Followers List on a PAMM with followers expands the inner subtable with follower details. | **PASSED** |
| 14 | `test_admin_pamm_page_length_selection` | Changing page length dropdown updates visible row count and DataTable pagination info. | **PASSED** |
| 15 | `test_admin_pamm_search_filters_by_pamm_name` | Entering a PAMM manager name into the search bar filters the rows correctly. | **PASSED** |
| 16 | `test_admin_pamm_search_filters_by_account_id` | Searching by Account ID isolates the matching PAMM manager record. | **PASSED** |
| 17 | `test_admin_pamm_search_nonexistent_query_shows_empty_state` | Searching for a nonexistent term shows no matching records and zero entries status. | **PASSED** |
| 18 | `test_admin_pamm_table_column_sorting` | Clicking sortable headers toggles column sorting between ascending and descending. | **PASSED** |
| 19 | `test_admin_pamm_table_pagination_and_info` | DataTable info status and pagination controls render active status correctly. | **PASSED** |
| 20 | `test_admin_pamm_edit_pamm_name_modal_opens_and_closes` | Clicking the PAMM name edit pencil opens the PAMM Details modal with name prefilled and dismisses safely. | **PASSED** |

### 7. Leads Report Module (19 Tests)
**File:** [test_admin_leads_report.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_leads_report.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_leads_report_topbar_branding_and_title` | The Leads Report topbar renders the brand logo, page title, and sidebar toggle button. | **PASSED** |
| 2 | `test_admin_leads_report_topbar_sidebar_toggle_action` | Clicking the vertical menu toggle button on Leads Report dynamically collapses or expands the sidebar. | **PASSED** |
| 3 | `test_admin_leads_report_theme_toggle_switches_modes` | The theme switch button on Leads Report toggles the layout mode between dark and light. | **PASSED** |
| 4 | `test_admin_leads_report_notifications_dropdown` | The notifications button on Leads Report opens the dropdown menu, badge, and Mark all read link. | **PASSED** |
| 5 | `test_admin_leads_report_profile_dropdown_and_logout_link` | The user profile menu on Leads Report displays admin details and a working Logout link. | **PASSED** |
| 6 | `test_admin_leads_report_filter_bar_structure_and_visibility` | The Leads Report filter bar renders date pickers, dropdown selects, and action buttons. | **PASSED** |
| 7 | `test_admin_leads_report_employee_dropdown_options` | The Employee select dropdown contains default placeholder, All, and employee options. | **PASSED** |
| 8 | `test_admin_leads_report_lead_type_dropdown_options` | The Lead Type dropdown displays placeholder, All option, and valid lead categories. | **PASSED** |
| 9 | `test_admin_leads_report_date_inputs_interaction` | The fromDate and toDate input fields accept date modifications. | **PASSED** |
| 10 | `test_admin_leads_report_filter_button_action` | Clicking the Filter button applies the selected date range and filter criteria. | **PASSED** |
| 11 | `test_admin_leads_report_download_button_attributes` | The Download XLSX button displays correct styling and action attributes. | **PASSED** |
| 12 | `test_admin_leads_report_employee_specific_options_selection` | Selecting specific employee options by ID updates the dropdown state accurately. | **PASSED** |
| 13 | `test_admin_leads_report_lead_type_specific_options_selection` | Selecting specific lead category options updates the dropdown value correctly. | **PASSED** |
| 14 | `test_admin_leads_report_table_card_and_controls` | The Leads Report card displays the table container and search filter. | **PASSED** |
| 15 | `test_admin_leads_report_table_headers_and_columns_are_valid` | All 8 Leads Report table column headers and sortable configurations are rendered correctly. | **PASSED** |
| 16 | `test_admin_leads_report_table_empty_state_or_data_integrity` | The Leads Report table renders valid data rows or displays the empty state message with correct colspan. | **PASSED** |
| 17 | `test_admin_leads_report_table_column_sorting` | Clicking sortable column headers on Leads Report toggles ascending and descending sort order. | **PASSED** |
| 18 | `test_admin_leads_report_table_search_filter_interaction` | Entering text in the Leads Report search filter filters the table and clears cleanly. | **PASSED** |
| 19 | `test_admin_leads_report_table_pagination_and_info` | The Leads Report DataTable info status and pagination controls render correctly. | **PASSED** |

### 8. Manage Leads Module (20 Tests)
**File:** [test_admin_manage_leads.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_manage_leads.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_manage_leads_topbar_branding_and_title` | The Manage Leads topbar renders the brand logo, page title, and sidebar toggle button. | **PASSED** |
| 2 | `test_admin_manage_leads_topbar_sidebar_toggle_action` | Clicking the vertical menu toggle button on Manage Leads dynamically collapses or expands the sidebar. | **PASSED** |
| 3 | `test_admin_manage_leads_theme_toggle_switches_modes` | The theme switch button on Manage Leads toggles the layout mode between dark and light. | **PASSED** |
| 4 | `test_admin_manage_leads_notifications_dropdown` | The notifications button on Manage Leads opens the dropdown menu, badge, and Mark all read link. | **PASSED** |
| 5 | `test_admin_manage_leads_profile_dropdown_and_logout_link` | The user profile menu on Manage Leads displays admin details and a working Logout link. | **PASSED** |
| 6 | `test_admin_manage_leads_action_buttons_and_permissions_rendered` | The Manage Leads actions bar displays Lead Types, Add Lead, Bulk Upload buttons, and permission flags. | **PASSED** |
| 7 | `test_admin_manage_leads_add_lead_modal_opens_and_closes` | Clicking the Add Lead button opens the Leads Form modal with employee and lead type selectors and dismisses safely. | **PASSED** |
| 8 | `test_admin_manage_leads_add_lead_empty_submission_validation` | Submitting an empty Leads Form prevents submission and keeps the modal open. | **PASSED** |
| 9 | `test_admin_manage_leads_bulk_upload_modal_opens_and_closes` | Clicking the Bulk Upload button opens the Bulk Upload modal with file input and dismisses safely. | **PASSED** |
| 10 | `test_admin_manage_leads_lead_types_modal_opens_and_closes` | Clicking the Lead Types button opens the Lead Type Form modal with lead category options and dismisses cleanly. | **PASSED** |
| 11 | `test_admin_manage_leads_table_card_and_datatable_controls` | The Manage Leads card wrapper displays length select dropdown (10, 25, 50, 100) and search filter. | **PASSED** |
| 12 | `test_admin_manage_leads_table_headers_and_columns_are_valid` | All 9 Manage Leads table column headers and sortable configurations are rendered correctly. | **PASSED** |
| 13 | `test_admin_manage_leads_table_rows_data_integrity` | The Manage Leads table rows display valid sequential S.No, details, edit buttons, and delete buttons. | **PASSED** |
| 14 | `test_admin_manage_leads_edit_lead_action_opens_modal_prefilled` | Clicking the edit pencil icon opens the Leads Form modal prefilled with existing lead details and dismisses safely. | **PASSED** |
| 15 | `test_admin_manage_leads_page_length_selection` | Changing page length dropdown updates visible row count and DataTable pagination info. | **PASSED** |
| 16 | `test_admin_manage_leads_search_filters_by_name` | Entering a lead name into the search bar filters the rows correctly. | **PASSED** |
| 17 | `test_admin_manage_leads_search_filters_by_email` | Searching by lead email isolates the matching lead record. | **PASSED** |
| 18 | `test_admin_manage_leads_search_nonexistent_query_shows_empty_state` | Searching for a nonexistent term shows no matching records and zero entries status. | **PASSED** |
| 19 | `test_admin_manage_leads_table_column_sorting` | Clicking sortable headers toggles column sorting between ascending and descending. | **PASSED** |
| 20 | `test_admin_manage_leads_table_pagination_and_info` | DataTable info status and pagination controls render active status correctly. | **PASSED** |

### 9. LP Transaction Module (16 Tests)
**File:** [test_admin_lp_transaction.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_lp_transaction.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_lp_transaction_topbar_branding_and_title` | The LP Transaction topbar renders the brand logo, page title, and sidebar toggle button. | **PASSED** |
| 2 | `test_admin_lp_transaction_topbar_sidebar_toggle_action` | Clicking the vertical menu toggle button on LP Transaction dynamically collapses or expands the sidebar. | **PASSED** |
| 3 | `test_admin_lp_transaction_theme_toggle_switches_modes` | The theme switch button on LP Transaction toggles the layout mode between dark and light. | **PASSED** |
| 4 | `test_admin_lp_transaction_notifications_dropdown` | The notifications button on LP Transaction opens the dropdown menu, badge, and Mark all read link. | **PASSED** |
| 5 | `test_admin_lp_transaction_profile_dropdown_and_logout_link` | The user profile menu on LP Transaction displays admin details and a working Logout link. | **PASSED** |
| 6 | `test_admin_lp_transaction_add_modal_opens_and_closes` | Clicking Add Transaction opens the Transaction Details modal with form inputs and dismisses cleanly. | **PASSED** |
| 7 | `test_admin_lp_transaction_add_modal_empty_submission_validation` | Submitting an empty Transaction Details form prevents submission and keeps the modal open. | **PASSED** |
| 8 | `test_admin_lp_transaction_page_loads_and_displays_heading` | The Admin LP Transaction page opens and displays the Abook Balance Transaction heading and Add Transaction button. | **PASSED** |
| 9 | `test_admin_lp_transaction_add_modal_field_inputs_and_reset` | The Add Transaction modal inputs accept transaction type, amount, and payment mode correctly. | **PASSED** |
| 10 | `test_admin_lp_transaction_table_card_and_datatable_controls` | The LP Transaction table card renders the DataTable wrapper, length selector, and search filter. | **PASSED** |
| 11 | `test_admin_lp_transaction_table_headers_and_columns_are_valid` | The LP Transaction table displays 5 columns (S.No, Transaction Type, Amount, Mode of Payment, Date Time) with sortable headers. | **PASSED** |
| 12 | `test_admin_lp_transaction_table_length_dropdown_selection` | Selecting different page length options updates the table length dropdown value. | **PASSED** |
| 13 | `test_admin_lp_transaction_table_search_filtering` | Searching for a query filters the records or displays the empty state accordingly. | **PASSED** |
| 14 | `test_admin_lp_transaction_table_column_sorting` | Clicking column headers updates the sorting order between ascending and descending. | **PASSED** |
| 15 | `test_admin_lp_transaction_table_empty_state_and_info` | The LP Transaction table displays the current records or empty state message with entries info. | **PASSED** |
| 16 | `test_admin_lp_transaction_table_pagination_controls` | The LP Transaction table displays pagination buttons with disabled state when there are no extra pages. | **PASSED** |

### 10. LP Commission Log Module (16 Tests)
**File:** [test_admin_lp_commission_log.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_lp_commission_log.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_lp_commission_log_topbar_branding_and_title` | The LP Commission Log topbar renders the brand logo, page title, and sidebar toggle button. | **PASSED** |
| 2 | `test_admin_lp_commission_log_topbar_sidebar_toggle_action` | Clicking the vertical menu toggle button on LP Commission Log dynamically collapses or expands the sidebar. | **PASSED** |
| 3 | `test_admin_lp_commission_log_theme_toggle_switches_modes` | The theme switch button on LP Commission Log toggles the layout mode between dark and light. | **PASSED** |
| 4 | `test_admin_lp_commission_log_notifications_dropdown` | The notifications button on LP Commission Log opens the dropdown menu with badge and not found message. | **PASSED** |
| 5 | `test_admin_lp_commission_log_profile_dropdown_and_logout_link` | The user profile menu on LP Commission Log displays admin details and a working Logout link. | **PASSED** |
| 6 | `test_admin_lp_commission_log_table_card_and_datatable_controls` | The LP Commission Log table card renders the DataTable wrapper, length selector, export buttons, and search filter. | **PASSED** |
| 7 | `test_admin_lp_commission_log_export_buttons_attributes` | The LP Commission Log table displays CSV, PDF, and Print export buttons. | **PASSED** |
| 8 | `test_admin_lp_commission_log_table_headers_and_columns` | The LP Commission Log table displays 6 columns (S.No, Order ID, Commission, Price, Lot, Date Time) with sortable headers. | **PASSED** |
| 9 | `test_admin_lp_commission_log_table_rows_data_integrity` | The LP Commission Log table renders valid records with numeric IDs, monetary values, and timestamps. | **PASSED** |
| 10 | `test_admin_lp_commission_log_table_length_dropdown_selection` | Changing page length dropdown dynamically updates the number of displayed records. | **PASSED** |
| 11 | `test_admin_lp_commission_log_table_search_filtering` | Searching filters table rows by query and shows empty state for unmatched terms. | **PASSED** |
| 12 | `test_admin_lp_commission_log_table_pagination_controls` | Clicking pagination Next and Previous controls traverses through log entries correctly. | **PASSED** |
| 13 | `test_admin_lp_commission_log_table_column_sorting` | Clicking table headers toggles the column sorting between ascending and descending. | **PASSED** |
| 14 | `test_admin_lp_commission_log_table_scroll_container_and_responsive_controls` | The LP Commission Log table renders scroll wrapper containers with responsive expansion control cells. | **PASSED** |
| 15 | `test_admin_lp_commission_log_pagination_numbered_page_navigation` | Clicking numbered pagination buttons switches active pages and updates entry records accordingly. | **PASSED** |
| 16 | `test_admin_lp_commission_log_page_2_pagination_state_and_navigation` | On page 2, Previous button is enabled, active page is 2, info displays 'Showing 51 to 100', and ellipsis is present. | **PASSED** |

### 11. LP Execution Config Module (12 Tests)
**File:** [test_admin_lp_execution_config.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_lp_execution_config.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_lp_execution_config_topbar_branding_and_title` | The LP Execution Config topbar renders brand logo, page title, and sidebar toggle button. | **PASSED** |
| 2 | `test_admin_lp_execution_config_topbar_sidebar_toggle_action` | Clicking the vertical menu toggle button on LP Execution Config dynamically collapses or expands the sidebar. | **PASSED** |
| 3 | `test_admin_lp_execution_config_theme_toggle_switches_modes` | The theme switch button on LP Execution Config toggles the layout mode between dark and light. | **PASSED** |
| 4 | `test_admin_lp_execution_config_notifications_dropdown` | The notifications button on LP Execution Config opens the dropdown menu with badge and mark all read link. | **PASSED** |
| 5 | `test_admin_lp_execution_config_profile_dropdown_and_logout_link` | The user profile menu on LP Execution Config displays admin details and a working Logout link. | **PASSED** |
| 6 | `test_admin_lp_execution_config_form_container_and_elements` | The LP Execution Config page displays the configuration card, form container, and save button. | **PASSED** |
| 7 | `test_admin_lp_execution_config_toggle_switch_attributes_and_behavior` | The LP Execution Config form renders the A-book execution toggle switch with correct label and toggle state. | **PASSED** |
| 8 | `test_admin_lp_execution_config_provider_dropdown_options` | The Provider select dropdown displays MatchTrade, FIX Bridge, and None options. | **PASSED** |
| 9 | `test_admin_lp_execution_config_owner_selects_and_options` | All 4 execution owner dropdowns display Local OMS, Python to LP, and LP server options. | **PASSED** |
| 10 | `test_admin_lp_execution_config_url_inputs_attributes_and_types` | The 4 URL fields (REST, WS Primary, WS Fallback, Bridge API) are configured with type url and form-control styling. | **PASSED** |
| 11 | `test_admin_lp_execution_config_url_inputs_editing_and_values` | The URL input fields accept valid URL values and allow updating configuration endpoints. | **PASSED** |
| 12 | `test_admin_lp_execution_config_save_button_attributes` | The Save Config button is styled as a primary action with status message container. | **PASSED** |

### 12. User Management Module (23 Tests)
**File:** [test_admin_user_management.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_user_management.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_user_topbar_branding_and_title` | The User Management topbar renders the brand logo, page title 'User', and sidebar toggle button. | **PASSED** |
| 2 | `test_admin_user_topbar_sidebar_toggle_action` | Clicking the vertical menu toggle button on User Management dynamically collapses or expands the sidebar. | **PASSED** |
| 3 | `test_admin_user_theme_toggle_switches_modes` | The theme switch button on User Management toggles the layout mode between dark and light. | **PASSED** |
| 4 | `test_admin_user_notifications_dropdown` | The notifications button on User Management opens the dropdown menu with badge and mark all read link. | **PASSED** |
| 5 | `test_admin_user_profile_dropdown_and_logout_link` | The user profile menu on User Management displays admin details and a working Logout link. | **PASSED** |
| 6 | `test_admin_user_page_actions_container_and_buttons_rendered` | The User Management page renders the actions container with Create Account, Add User, and Refresh buttons. | **PASSED** |
| 7 | `test_admin_user_page_actions_hidden_permission_inputs` | The User Management action container includes all 6 hidden permission configuration flags. | **PASSED** |
| 8 | `test_admin_user_refresh_button_action` | Clicking the Refresh button triggers page data reload without causing layout errors. | **PASSED** |
| 9 | `test_admin_user_create_account_button_opens_modal` | Clicking Create Account opens the Create Account modal with valid title and close action. | **PASSED** |
| 10 | `test_admin_user_add_user_button_opens_modal` | Clicking Add User opens the User Details modal with valid title and close action. | **PASSED** |
| 11 | `test_admin_user_table_card_and_datatable_controls` | The User Management table card renders the DataTable wrapper, length selector, and search filter. | **PASSED** |
| 12 | `test_admin_user_export_buttons_rendered` | The User Management table displays CSV, PDF, and Excel export buttons. | **PASSED** |
| 13 | `test_admin_user_date_filter_controls` | The User Management table renders datetime-local From and To inputs with Go and Clear action buttons. | **PASSED** |
| 14 | `test_admin_user_table_rows_data_integrity` | The User Management table renders valid rows with Account IDs, client credentials, and financial values. | **PASSED** |
| 15 | `test_admin_user_table_pagination_controls` | Clicking pagination Next and Previous controls traverses through user entries correctly. | **PASSED** |
| 16 | `test_admin_user_table_headers_and_columns` | The User Management table displays 17 structured columns with sortable headers. | **PASSED** |
| 17 | `test_admin_user_table_row_select_dropdowns` | User table rows display inline status dropdowns for Email, Document, Account Type, Status, and Book. | **PASSED** |
| 18 | `test_admin_user_length_dropdown_selection` | Changing entries per page dropdown updates the displayed user records. | **PASSED** |
| 19 | `test_admin_user_search_filtering` | Searching filters user rows by query and shows empty state for unmatched terms. | **PASSED** |
| 20 | `test_admin_user_pagination_page_2_every_possible_way` | Navigating to Page 2 via page number button and Next button updates active state, Previous button, and entry range to 11-20. | **PASSED** |
| 21 | `test_admin_user_verification_dropdowns_and_verified_behavior` | Verification dropdowns for Email, Document, and Status expose Verified/Not Verified options and dynamic success/danger styling. | **PASSED** |
| 22 | `test_admin_user_page_2_row_buttons_verification` | Rows on Page 2 display verified status selects, action buttons, and responsive controls identical to Page 1. | **PASSED** |
| 23 | `test_admin_user_table_row_action_buttons_and_expanded_details` | Table rows render action buttons (Edit, Delete, Edit ID) and expanding responsive row reveals trading controls (MAM, PAMM, Copy Trading). | **PASSED** |

### 13. Account Requests Module (15 Tests)
**File:** [test_admin_account_requests.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_account_requests.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_account_requests_topbar_branding_and_title` | The Account Requests topbar renders brand logo, page title 'Account Requests', and sidebar toggle button. | **PASSED** |
| 2 | `test_admin_account_requests_topbar_sidebar_toggle_action` | Clicking the vertical menu toggle button on Account Requests dynamically collapses or expands the sidebar. | **PASSED** |
| 3 | `test_admin_account_requests_theme_toggle_switches_modes` | The theme switch button on Account Requests toggles the layout mode between dark and light. | **PASSED** |
| 4 | `test_admin_account_requests_notifications_dropdown` | The notifications button on Account Requests opens the dropdown menu with badge and mark all read link. | **PASSED** |
| 5 | `test_admin_account_requests_profile_dropdown_and_logout_link` | The user profile menu on Account Requests displays admin details and a working Logout link. | **PASSED** |
| 6 | `test_admin_account_requests_card_heading_and_refresh_action` | The Client Account Creation Requests card renders the title and Refresh button triggers table reload. | **PASSED** |
| 7 | `test_admin_account_requests_table_headers_and_columns` | The Account Requests table renders 11 structured columns with sortable headers. | **PASSED** |
| 8 | `test_admin_account_requests_table_rows_data_integrity` | The Account Requests table displays valid client requests with emails, accounts, and timestamps. | **PASSED** |
| 9 | `test_admin_account_requests_length_dropdown_selection` | Changing entries per page dropdown updates visible records and pagination status info. | **PASSED** |
| 10 | `test_admin_account_requests_search_filtering` | Searching filters request records by query and displays empty state for unmatched terms. | **PASSED** |
| 11 | `test_admin_account_requests_table_column_sorting` | Clicking table headers toggles column sorting between ascending and descending order. | **PASSED** |
| 12 | `test_admin_account_requests_pagination_controls` | Traversing via Next and Previous pagination controls updates displayed requests and active page state. | **PASSED** |
| 13 | `test_admin_account_requests_pagination_page_2_every_possible_way` | Navigating to Page 2 via page number button and Next button updates active state, entry range 11-16, and disabled controls. | **PASSED** |
| 14 | `test_admin_account_requests_page_2_data_and_action_verification` | Records on Page 2 display complete client details, reviewed admins, and consistent table structure. | **PASSED** |
| 15 | `test_admin_account_requests_status_badges_and_action_buttons` | Pending requests render Approve and Reject action buttons while reviewed records show status badges. | **PASSED** |

### 14. User Document Verification Module (16 Tests)
**File:** [test_admin_user_document.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_user_document.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_user_document_topbar_branding_and_title` | The User Document topbar renders brand logo, page title 'User Document', and sidebar toggle button. | **PASSED** |
| 2 | `test_admin_user_document_topbar_sidebar_toggle_action` | Clicking the vertical menu toggle button on User Document dynamically collapses or expands the sidebar. | **PASSED** |
| 3 | `test_admin_user_document_theme_toggle_switches_modes` | The theme switch button on User Document toggles the layout mode between dark and light. | **PASSED** |
| 4 | `test_admin_user_document_notifications_dropdown` | The notifications button on User Document opens the dropdown menu with badge and mark all read link. | **PASSED** |
| 5 | `test_admin_user_document_profile_dropdown_and_logout_link` | The user profile menu on User Document displays admin details and a working Logout link. | **PASSED** |
| 6 | `test_admin_user_document_page_actions_and_hidden_permissions` | The User Document page displays Add Document action, hidden permission flags, and working creation modal. | **PASSED** |
| 7 | `test_admin_user_document_table_card_and_13_column_headers` | The User Document table displays the card wrapper, 13 exact column headers, and 10 initial rows. | **PASSED** |
| 8 | `test_admin_user_document_table_rows_data_and_file_links` | The User Document table rows display valid user records with clickable document links or hyphens. | **PASSED** |
| 9 | `test_admin_user_document_verification_dropdown_status_and_classes` | The verification status dropdown renders Verified, Not Verified, and Rejected with dynamic color classes and remark triggers. | **PASSED** |
| 10 | `test_admin_user_document_remarks_action_opens_modal` | Clicking the pencil remark icon on a user document opens the Remarks Form modal with textarea and update action. | **PASSED** |
| 11 | `test_admin_user_document_edit_action_opens_form_modal` | Clicking the edit document action icon opens the User Document Form modal. | **PASSED** |
| 12 | `test_admin_user_document_delete_action_with_and_without_documents` | Clicking delete on records without documents shows an error alert, while records with documents open the Delete Document Form modal. | **PASSED** |
| 13 | `test_admin_user_document_length_dropdown_selection` | Changing entries per page dropdown updates visible documents count and pagination status info. | **PASSED** |
| 14 | `test_admin_user_document_date_filter_controls` | Entering date range filters documents table by timestamp and Clear button resets input fields. | **PASSED** |
| 15 | `test_admin_user_document_search_filtering` | Searching filters documents by client name or account ID and shows empty state when unmatched. | **PASSED** |
| 16 | `test_admin_user_document_pagination_page_2_every_possible_way` | Navigating to Page 2 via number button and Next button updates active state, entry range 11-20, and enables Previous button. | **PASSED** |

### 15. Role & Permission Module (14 Tests)
**File:** [test_admin_role_permission.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_role_permission.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_role_permission_topbar_branding_and_title` | The Role Permission topbar renders brand logo, page title 'Role Permission', and sidebar toggle button. | **PASSED** |
| 2 | `test_admin_role_permission_topbar_sidebar_toggle_action` | Clicking the vertical menu toggle button on Role Permission dynamically collapses or expands the sidebar. | **PASSED** |
| 3 | `test_admin_role_permission_theme_toggle_switches_modes` | The theme switch button on Role Permission toggles the layout mode between dark and light. | **PASSED** |
| 4 | `test_admin_role_permission_notifications_dropdown` | The notifications button on Role Permission opens the dropdown menu with badge and mark all read link. | **PASSED** |
| 5 | `test_admin_role_permission_profile_dropdown_and_logout_link` | The user profile menu on Role Permission displays admin details and a working Logout link. | **PASSED** |
| 6 | `test_admin_role_permission_page_actions_and_hidden_flags` | The Role Permission page displays Add Role Permission action, hidden permission flags, and working creation modal. | **PASSED** |
| 7 | `test_admin_role_permission_table_card_and_column_headers` | The Role Permission table card displays 3 column headers (S.No, Role Name, Action) and 4 records. | **PASSED** |
| 8 | `test_admin_role_permission_table_rows_data_integrity` | The Role Permission table rows display valid roles with name edit, permissions link, and delete action buttons. | **PASSED** |
| 9 | `test_admin_role_permission_edit_role_name_action_modal` | Clicking the pencil edit icon opens the Role Permission Form modal pre-populated with existing role name. | **PASSED** |
| 10 | `test_admin_role_permission_edit_permissions_navigation_link` | The edit permissions icon link points to the correct role permissions configuration URL. | **PASSED** |
| 11 | `test_admin_role_permission_delete_action_triggers_sweetalert` | Clicking the delete icon on a role triggers the SweetAlert2 confirmation dialog and cancel dismisses it safely. | **PASSED** |
| 12 | `test_admin_role_permission_length_dropdown_selection` | Changing entries per page dropdown updates visible roles count and pagination status info. | **PASSED** |
| 13 | `test_admin_role_permission_search_filtering` | Searching filters roles by name and displays empty state text when unmatched. | **PASSED** |
| 14 | `test_admin_role_permission_pagination_controls` | The pagination controls reflect single-page status with disabled Previous and Next buttons. | **PASSED** |

### 16. Manager User Management Module (14 Tests)
**File:** [test_admin_manager_user_management.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_manager_user_management.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_manager_user_management_topbar_branding_and_title` | The User Management topbar renders brand logo, page title 'User Management', and sidebar toggle button. | **PASSED** |
| 2 | `test_admin_manager_user_management_topbar_sidebar_toggle_action` | Clicking the vertical menu toggle button on User Management dynamically collapses or expands the sidebar. | **PASSED** |
| 3 | `test_admin_manager_user_management_theme_toggle_switches_modes` | The theme switch button on User Management toggles the layout mode between dark and light. | **PASSED** |
| 4 | `test_admin_manager_user_management_notifications_dropdown` | The notifications button on User Management opens the dropdown menu with badge and mark all read link. | **PASSED** |
| 5 | `test_admin_manager_user_management_profile_dropdown_and_logout_link` | The user profile menu on User Management displays admin details and a working Logout link. | **PASSED** |
| 6 | `test_admin_manager_user_management_page_actions_and_hidden_flags` | The User Management page displays Add User action, hidden permission flags, and working creation modal. | **PASSED** |
| 7 | `test_admin_manager_user_management_table_card_and_column_headers` | The User Management table card displays 6 column headers (S.No, User Name, User Type, Login OTP, Action, Active) and data rows. | **PASSED** |
| 8 | `test_admin_manager_user_management_table_rows_data_integrity` | The User Management table rows display valid users with edit, password reset, delete, and active status switch controls. | **PASSED** |
| 9 | `test_admin_manager_user_management_edit_user_action_modal` | Clicking the edit user icon opens the User Management modal pre-populated with user details. | **PASSED** |
| 10 | `test_admin_manager_user_management_delete_action_triggers_sweetalert` | Clicking the delete icon on a user triggers the SweetAlert2 confirmation dialog and cancel dismisses it safely. | **PASSED** |
| 11 | `test_admin_manager_user_management_length_dropdown_selection` | Changing entries per page dropdown updates visible users count and pagination status info. | **PASSED** |
| 12 | `test_admin_manager_user_management_search_filtering` | Searching filters users by name and displays empty state text when unmatched. | **PASSED** |
| 13 | `test_admin_manager_user_management_pagination_controls` | Pagination controls traverse between page 1 and page 2 correctly when length is set to 10. | **PASSED** |
| 14 | `test_admin_manager_user_management_reset_password_modal` | Clicking the reset password icon opens the password update modal. | **PASSED** |

### 17. Manager Management Module (18 Tests)
**File:** [test_admin_manager_management.py](file:///d:/Complete-Test/workflows/admin_portal/tests/test_admin_manager_management.py)

| # | Test Function | Scenario Description | Status |
|---|---|---|:---:|
| 1 | `test_admin_manager_management_topbar_branding_and_title` | The Manager Management topbar renders brand logo, page title 'Manager Management', and sidebar toggle button. | **PASSED** |
| 2 | `test_admin_manager_management_topbar_sidebar_toggle_action` | Clicking the vertical menu toggle button on Manager Management dynamically collapses or expands the sidebar. | **PASSED** |
| 3 | `test_admin_manager_management_theme_toggle_switches_modes` | The theme switch button on Manager Management toggles the layout mode between dark and light. | **PASSED** |
| 4 | `test_admin_manager_management_notifications_dropdown` | The notifications button on Manager Management opens the dropdown menu with badge and mark all read link. | **PASSED** |
| 5 | `test_admin_manager_management_profile_dropdown_and_logout_link` | The user profile menu on Manager Management displays admin details and a working Logout link. | **PASSED** |
| 6 | `test_admin_manager_management_add_manager_button_and_modal` | The Manager Management page displays Add Manager button and clicking opens the creation modal. | **PASSED** |
| 7 | `test_admin_manager_management_table_rows_data_integrity` | The Manager Management table rows display valid managers with sequential S.No, names, emails, and action buttons. | **PASSED** |
| 8 | `test_admin_manager_management_edit_manager_action_modal` | Clicking the edit icon opens the Manager modal and close button dismisses it cleanly. | **PASSED** |
| 9 | `test_admin_manager_management_delete_action_triggers_sweetalert` | Clicking the delete icon on a manager triggers the SweetAlert2 confirmation dialog and cancel dismisses it safely. | **PASSED** |
| 10 | `test_admin_manager_management_length_dropdown_selection` | Changing entries per page dropdown updates visible managers count and pagination status info. | **PASSED** |
| 11 | `test_admin_manager_management_search_filtering` | Searching filters managers by name and displays empty state text when unmatched. | **PASSED** |
| 12 | `test_admin_manager_management_pagination_controls` | Pagination controls traverse between page 1 and page 2 correctly when length is set to 10. | **PASSED** |
| 13 | `test_admin_manager_management_table_card_and_column_headers` | The Manager Management table card displays 5 column headers (S.No, Manager Name, Email, Password, Action) and data rows. | **PASSED** |
| 14 | `test_admin_manager_management_permissions_hidden_inputs` | The page-title-box hidden inputs define edit and delete manager permissions with active values. | **PASSED** |
| 15 | `test_admin_manager_management_add_modal_form_fields` | The Add Manager modal renders all required form inputs: username, email, password, and submit button. | **PASSED** |
| 16 | `test_admin_manager_management_table_sorting_by_manager_name` | Clicking the Manager Name column header toggles DataTable sorting order between ascending and descending. | **PASSED** |
| 17 | `test_admin_manager_management_passwords_are_masked` | The Manager Management table rows display securely masked passwords for credentials protection. | **PASSED** |
| 18 | `test_admin_manager_management_row_action_button_tooltips` | The Manager table row action buttons display correct Edit and Delete tooltips, aria-labels, and icons. | **PASSED** |
