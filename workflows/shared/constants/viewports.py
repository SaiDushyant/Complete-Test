"""
Responsive Viewport Specifications.
Standardized across DOM Regression Crawler and Behavioral Workflow Testing.
"""

from typing import Dict

# Standard responsive breakpoint viewports (height standardized to 900px)
VIEWPORTS: Dict[str, Dict[str, int]] = {
    "sm": {"width": 640, "height": 900},    # Mobile landscape / Small tablets
    "md": {"width": 768, "height": 900},    # Tablets / Portrait iPads
    "lg": {"width": 1024, "height": 900},   # Small laptops / Desktop standard
    "xl": {"width": 1280, "height": 900},   # Standard HD desktop (Default)
    "2xl": {"width": 1536, "height": 900},  # Large widescreen displays
}

DEFAULT_VIEWPORT_NAME = "xl"
DEFAULT_VIEWPORT = VIEWPORTS[DEFAULT_VIEWPORT_NAME]
