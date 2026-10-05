from wcag_fixer.core import analyze
from wcag_fixer.rules import contrast_ratio


def test_detects_core_issues():
    r = {i.rule for i in analyze(open("examples/bad.html").read())[0]}
    assert {"html-lang", "page-title", "img-alt", "form-label", "empty-name",
            "vague-link-text", "heading-order", "color-contrast"} <= r


def test_fix_applies_safe_changes():
    _, new = analyze(open("examples/bad.html").read(), fix=True)
    assert 'lang="en"' in new
    assert 'aria-label="Search"' in new
    assert 'src="spacer.gif" alt=""' in new or 'alt="" src="spacer.gif"' in new
    assert '<img src="shoe.jpg"/>' in new  # meaningful image is NOT guessed


def test_contrast_math():
    assert round(contrast_ratio((0, 0, 0), (255, 255, 255))) == 21


def test_clean_page():
    ok = '<html lang="en"><head><title>x</title></head><body><h1>a</h1><img src="a.png" alt="a"></body></html>'
    assert analyze(ok)[0] == []
