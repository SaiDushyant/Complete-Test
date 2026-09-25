"""
Trade Terminal Trading Dashboard Page Object.
Encapsulates all dashboard overview elements: summary cards (Account Status, User Account,
Balance, Free Margin), Balance chart, Monthly P/L period toggles, Symbol Order Count, and Performance Stats.
Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

from typing import Dict, List, Optional

from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("trading_dashboard_page")


class TradingDashboardPage(BasePage):
    """Page object for Trade Terminal main dashboard workspace."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Dashboard outer layout
        self.dashboard_container: Locator = page.locator(".dashboard-container, #dashboard, main, body")
        self.overview_panel: Locator = page.locator("#exampleTabsIconOnex")

        # 1. Welcome Banner
        self.welcome_header: Locator = self.overview_panel.locator("h3.customh3top")
        self.welcome_name: Locator = self.overview_panel.locator("h3.customh3top span.name")

        # 2. Top Summary Metric Cards
        self.account_status_card: Locator = self.overview_panel.locator(".user-status:has(h2:has-text('Account Status'))")
        self.account_status_text: Locator = self.overview_panel.locator(".vstatus")
        self.account_status_badge: Locator = self.overview_panel.locator(".vstatus img.btn-image")

        self.account_token_card: Locator = self.overview_panel.locator(".user-status:has(h2:has-text('User Account'))")
        self.account_token: Locator = self.overview_panel.locator(".secrets")

        self.balance_card: Locator = self.overview_panel.locator(".user-status.balance_img")
        self.balance_currency: Locator = self.balance_card.locator(".userCurrencySymbol")
        self.balance_value: Locator = self.balance_card.locator(".balance")

        self.free_margin_card: Locator = self.overview_panel.locator(".user-status.freemargin_img")
        self.free_margin_currency: Locator = self.free_margin_card.locator(".userCurrencySymbol")
        self.free_margin_value: Locator = self.free_margin_card.locator(".fund")

        # 3. Total Balance Chart Card
        self.balance_chart_card: Locator = self.overview_panel.locator(".balance-chart-card")
        self.balance_chart_canvas: Locator = self.balance_chart_card.locator("canvas.balance-chart-canvas")
        self.legend_balance: Locator = self.balance_chart_card.locator("[data-stat='legendBalance']")
        self.legend_fund: Locator = self.balance_chart_card.locator("[data-stat='legendFund']")

        # 4. Monthly P/L Header & Period Toggle Controls
        self.monthly_pnl_card: Locator = self.overview_panel.locator(".monthly-pnl-card")
        self.monthly_pnl_canvas: Locator = self.monthly_pnl_card.locator("canvas.monthly-pnl-canvas")
        self.pnl_header: Locator = self.overview_panel.locator(".monthly-pnl-header")
        self.pnl_card_title: Locator = self.overview_panel.locator("h2[data-stat='pnlCardTitle']")
        self.pnl_period_toggle: Locator = self.overview_panel.locator(".pnl-period-toggle")
        self.daily_button: Locator = self.overview_panel.locator("button.pnl-period-btn[data-period='daily']")
        self.weekly_button: Locator = self.overview_panel.locator("button.pnl-period-btn[data-period='weekly']")
        self.monthly_button: Locator = self.overview_panel.locator("button.pnl-period-btn[data-period='monthly']")
        self.period_buttons: Locator = self.overview_panel.locator("button.pnl-period-btn")

        # 5. Symbol Order Count (Most Traded)
        self.most_traded_card: Locator = self.overview_panel.locator(".most-traded-card")
        self.most_traded_donut_svg: Locator = self.most_traded_card.locator("svg.most-traded-donut")
        self.most_traded_donut_circles: Locator = self.most_traded_donut_svg.locator("circle")
        self.most_traded_table: Locator = self.most_traded_card.locator(".most-traded-table")
        self.most_traded_rows: Locator = self.most_traded_table.locator("tbody.most-traded-list tr")

        # 6. Performance Stats Card
        self.perf_stats_card: Locator = self.overview_panel.locator(".perf-stats-card")
        self.perf_stat_avg_win: Locator = self.perf_stats_card.locator("[data-stat='avgWin']")
        self.perf_stat_avg_loss: Locator = self.perf_stats_card.locator("[data-stat='avgLoss']")
        self.perf_stat_profit_factor: Locator = self.perf_stats_card.locator("[data-stat='profitFactor']")
        self.perf_stat_best_trade: Locator = self.perf_stats_card.locator("[data-stat='bestTrade']")
        self.perf_stat_win_ratio: Locator = self.perf_stats_card.locator("[data-stat='winRatio']")
        self.perf_stat_risk_reward: Locator = self.perf_stats_card.locator("[data-stat='riskReward']")
        self.perf_stat_max_drawdown: Locator = self.perf_stats_card.locator("[data-stat='maxDrawdown']")
        self.perf_stat_closed_trades: Locator = self.perf_stats_card.locator("[data-stat='closedTrades']")

        # General navigation tabs (preserved)
        self.watchlist_panel: Locator = page.locator(".watchlist-panel, .watchlist-container, #watchlist")
        self.order_ticket_button: Locator = page.locator(
            "button:has-text('New Order'), .btn-order, [data-action='new-order']"
        )
        self.positions_tab: Locator = page.locator(".positions-tab, a:has-text('Positions'), [data-tab='positions']")
        self.user_menu: Locator = page.locator(".user-profile, .user-menu, [data-dropdown='user-menu']")

    def navigate(self, url: Optional[str] = None) -> None:
        """Navigate to Trade Terminal dashboard endpoint."""
        target_url = url or f"{settings.trade_terminal.base_url.rstrip('/')}/dashboard/"
        logger.info(f"Navigating to Trade Terminal dashboard: {target_url}")
        self.goto(target_url)
        self.overview_panel.wait_for(state="visible", timeout=settings.browser.timeout)
        self.pnl_header.wait_for(state="visible", timeout=settings.browser.timeout)

    def is_dashboard_displayed(self) -> bool:
        """Verify dashboard interface presence."""
        return self.overview_panel.first.is_visible()

    # --- P/L Toggle Methods ---
    def are_pnl_period_buttons_displayed(self) -> bool:
        """Verify that all three PnL period buttons (daily, weekly, monthly) are visible."""
        return (
            self.daily_button.first.is_visible()
            and self.weekly_button.first.is_visible()
            and self.monthly_button.first.is_visible()
        )

    def select_period(self, period: str) -> None:
        """Click the specified PnL period button ('daily', 'weekly', or 'monthly')."""
        period_clean = period.strip().lower()
        logger.info(f"Selecting PnL period: {period_clean}")
        if period_clean == "daily":
            self.daily_button.first.click()
        elif period_clean == "weekly":
            self.weekly_button.first.click()
        elif period_clean == "monthly":
            self.monthly_button.first.click()
        else:
            raise ValueError(f"Invalid period '{period}'. Expected 'daily', 'weekly', or 'monthly'.")

    def get_card_title(self) -> str:
        """Retrieve the current PnL card header title text."""
        return self.pnl_card_title.first.inner_text().strip()

    def is_period_active(self, period: str) -> bool:
        """Check if the given period button currently holds the 'active' class."""
        period_clean = period.strip().lower()
        btn = {
            "daily": self.daily_button,
            "weekly": self.weekly_button,
            "monthly": self.monthly_button,
        }.get(period_clean)

        if not btn:
            raise ValueError(f"Unknown period: {period}")

        classes = btn.first.get_attribute("class") or ""
        return "active" in classes.split()

    def get_active_period(self) -> Optional[str]:
        """Return the period key ('daily', 'weekly', or 'monthly') of the currently active button."""
        for period in ["daily", "weekly", "monthly"]:
            if self.is_period_active(period):
                return period
        return None

    # --- Summary Card Getters ---
    def get_balance_value(self) -> str:
        """Return the numeric text in the balance card."""
        return self.balance_value.first.inner_text().strip()

    def get_free_margin_value(self) -> str:
        """Return the numeric text in the free margin card."""
        return self.free_margin_value.first.inner_text().strip()

    def get_account_status(self) -> str:
        """Return the verification status text."""
        return self.account_status_text.first.inner_text().strip()

    def get_account_token(self) -> str:
        """Return the active account secret token."""
        return self.account_token.first.inner_text().strip()

    # --- Performance Stats Getter ---
    def get_performance_stats(self) -> Dict[str, str]:
        """Collect all 8 performance stats into a dictionary."""
        return {
            "avg_win": self.perf_stat_avg_win.first.inner_text().strip(),
            "avg_loss": self.perf_stat_avg_loss.first.inner_text().strip(),
            "profit_factor": self.perf_stat_profit_factor.first.inner_text().strip(),
            "best_trade": self.perf_stat_best_trade.first.inner_text().strip(),
            "win_ratio": self.perf_stat_win_ratio.first.inner_text().strip(),
            "risk_reward": self.perf_stat_risk_reward.first.inner_text().strip(),
            "max_drawdown": self.perf_stat_max_drawdown.first.inner_text().strip(),
            "closed_trades": self.perf_stat_closed_trades.first.inner_text().strip(),
        }

    # --- Most Traded Symbols Getter ---
    def get_most_traded_symbols(self) -> List[str]:
        """Extract all symbol names currently listed in the Most Traded table."""
        count = self.most_traded_rows.count()
        symbols = []
        for i in range(count):
            sym_cell = self.most_traded_rows.nth(i).locator(".most-traded-symbol")
            if sym_cell.is_visible():
                symbols.append(sym_cell.inner_text().strip())
        return symbols

    # --- General Dashboard Actions ---
    def open_order_entry(self) -> None:
        """Open the order entry / ticket modal or panel."""
        if self.order_ticket_button.first.is_visible():
            self.order_ticket_button.first.click()

    def select_positions_tab(self) -> None:
        """Switch view to Positions tab."""
        if self.positions_tab.first.is_visible():
            self.positions_tab.first.click()
