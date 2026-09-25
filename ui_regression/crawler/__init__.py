"""
Generic, Read-Only Playwright Application Crawler Package.
"""

from crawler.crawler import Crawler
from crawler.auth import create_authenticated_context
from crawler.element_extractor import extract_elements

__all__ = ["Crawler", "create_authenticated_context", "extract_elements"]
