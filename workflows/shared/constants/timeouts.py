"""
Standard Timeout Constants (in milliseconds) across all workflow tests.
"""

# Instant / Micro-wait
TIMEOUT_INSTANT = 500

# Short interactions (clicks, state transitions, dialog close)
TIMEOUT_SHORT = 5000

# Medium interactions (form submissions, API responses, modal openings)
TIMEOUT_DEFAULT = 15000

# Long interactions (heavy table loading, chart render, complex navigations)
TIMEOUT_LONG = 30000

# Full page navigation timeout
TIMEOUT_PAGE_LOAD = 60000

# Network idle polling timeout
TIMEOUT_NETWORK_IDLE = 10000
