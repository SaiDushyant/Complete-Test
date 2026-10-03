"""
Financial & Mathematical Assertion Helpers.
Provides standardized, formula-driven mathematical validations for
Balance, Equity, Used Margin, Free Margin, and Margin Level Percentage.
"""

from __future__ import annotations

import math
from typing import Optional, Tuple


def calculate_equity(balance: float, floating_pnl: float, credit: float = 0.0) -> float:
    """Calculate Equity = Balance + Floating PnL + Credit."""
    return balance + floating_pnl + credit


def calculate_free_margin(equity: float, used_margin: float) -> float:
    """Calculate Free Margin = Equity - Used Margin."""
    return equity - used_margin


def calculate_margin_level(equity: float, used_margin: float) -> float:
    """Calculate Margin Level % = (Equity / Used Margin) * 100."""
    if used_margin <= 0:
        return 0.0
    return (equity / used_margin) * 100.0


def assert_equity_calculation(
    balance: float,
    floating_pnl: float,
    actual_equity: float,
    credit: float = 0.0,
    tolerance: float = 0.5,
) -> None:
    """
    Verify the fundamental financial formula:
    Equity = Balance + Floating PnL + Credit
    """
    expected_equity = balance + floating_pnl + credit
    diff = abs(actual_equity - expected_equity)
    if diff > tolerance:
        raise AssertionError(
            f"Equity calculation mismatch:\n"
            f"  Balance:      {balance}\n"
            f"  Floating PnL: {floating_pnl}\n"
            f"  Credit:       {credit}\n"
            f"  Expected:     {expected_equity:.2f}\n"
            f"  Actual:       {actual_equity:.2f}\n"
            f"  Difference:   {diff:.2f} (tolerance: {tolerance})"
        )


def assert_free_margin_calculation(
    equity: float,
    used_margin: float,
    actual_free_margin: float,
    tolerance: float = 0.5,
) -> None:
    """
    Verify the free margin formula:
    Free Margin = Equity - Used Margin
    """
    expected_free_margin = equity - used_margin
    diff = abs(actual_free_margin - expected_free_margin)
    if diff > tolerance:
        raise AssertionError(
            f"Free Margin calculation mismatch:\n"
            f"  Equity:       {equity}\n"
            f"  Used Margin:  {used_margin}\n"
            f"  Expected:     {expected_free_margin:.2f}\n"
            f"  Actual:       {actual_free_margin:.2f}\n"
            f"  Difference:   {diff:.2f} (tolerance: {tolerance})"
        )


def assert_margin_level_percentage(
    equity: float,
    used_margin: float,
    actual_margin_level: float,
    tolerance: float = 1.0,
) -> None:
    """
    Verify the margin level percentage formula:
    Margin Level % = (Equity / Used Margin) * 100
    If Used Margin is 0, Margin Level is typically 0% or undefined / infinite.
    """
    if used_margin <= 0:
        return

    expected_margin_level = (equity / used_margin) * 100.0
    diff = abs(actual_margin_level - expected_margin_level)
    if diff > tolerance:
        raise AssertionError(
            f"Margin Level % calculation mismatch:\n"
            f"  Equity:       {equity}\n"
            f"  Used Margin:  {used_margin}\n"
            f"  Expected:     {expected_margin_level:.2f}%\n"
            f"  Actual:       {actual_margin_level:.2f}%\n"
            f"  Difference:   {diff:.2f}% (tolerance: {tolerance}%)"
        )


def calculate_required_margin(
    lot: float,
    contract_size: float = 100000.0,
    price: float = 1.0,
    leverage: float = 100.0,
) -> float:
    """
    Calculate required margin for an FX/CFD position:
    Required Margin = (Lot * Contract Size * Price) / Leverage
    """
    if leverage <= 0:
        raise ValueError("Leverage must be greater than 0.")
    return (lot * contract_size * price) / leverage


def validate_sl_tp_logic(
    order_type: str,
    open_price: float,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
) -> Tuple[bool, str]:
    """
    Validate the inverted SL/TP mathematical rules:
    - BUY:  SL < Open Price < TP
    - SELL: TP < Open Price < SL

    Returns:
        (is_valid: bool, error_message: str)
    """
    side = order_type.upper()
    if side in ("BUY", "BUY_LIMIT", "BUY_STOP"):
        if stop_loss is not None and stop_loss > 0 and stop_loss >= open_price:
            return False, f"Buy SL ({stop_loss}) must be strictly less than Open Price ({open_price})"
        if take_profit is not None and take_profit > 0 and take_profit <= open_price:
            return False, f"Buy TP ({take_profit}) must be strictly greater than Open Price ({open_price})"
    elif side in ("SELL", "SELL_LIMIT", "SELL_STOP"):
        if stop_loss is not None and stop_loss > 0 and stop_loss <= open_price:
            return False, f"Sell SL ({stop_loss}) must be strictly greater than Open Price ({open_price})"
        if take_profit is not None and take_profit > 0 and take_profit >= open_price:
            return False, f"Sell TP ({take_profit}) must be strictly less than Open Price ({open_price})"

    return True, "Valid"
