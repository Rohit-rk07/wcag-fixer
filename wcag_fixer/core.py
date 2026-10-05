from bs4 import BeautifulSoup
from . import rules


def analyze(html: str, fix: bool = False, alt_provider=None):
    """Return (issues, new_html)."""
    soup = BeautifulSoup(html, "html.parser")
    issues = []
    for rule in rules.RULES:
        issues += rule(soup, fix, alt_provider) if rule is rules.check_img_alt else rule(soup, fix)
    return issues, str(soup)
