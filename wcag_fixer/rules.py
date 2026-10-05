"""WCAG-aware rules. Each rule returns Issues and may apply a safe auto-fix."""
from dataclasses import dataclass
from bs4 import Tag
import re


@dataclass
class Issue:
    rule: str
    wcag: str
    level: str
    message: str
    snippet: str
    fixed: bool = False


def _snip(tag: Tag) -> str:
    return str(tag)[:100]


def check_lang(soup, fix):
    html = soup.find("html")
    if html is not None and not html.get("lang"):
        issue = Issue("html-lang", "3.1.1", "A", "<html> is missing a lang attribute", "<html>")
        if fix:
            html["lang"] = "en"
            issue.fixed = True
        return [issue]
    return []


def check_title(soup, fix):
    if soup.find("html") is not None and not (soup.title and soup.title.get_text(strip=True)):
        return [Issue("page-title", "2.4.2", "A", "Page has no <title>", "<head>")]
    return []


def check_img_alt(soup, fix, alt_provider=None):
    out = []
    for img in soup.find_all("img"):
        if img.get("alt") is None:
            issue = Issue("img-alt", "1.1.1", "A", "Image missing alt text", _snip(img))
            if fix:
                alt = alt_provider(img) if alt_provider else None
                if alt is None and re.search(r"(spacer|divider|bg|decor)", img.get("src", ""), re.I):
                    alt = ""  # clearly decorative; anything else needs a human (or --ai-alt)
                if alt is not None:
                    img["alt"] = alt
                    issue.fixed = True
            out.append(issue)
    return out


def check_form_labels(soup, fix):
    out = []
    labelled = {l.get("for") for l in soup.find_all("label") if l.get("for")}
    for el in soup.find_all(["input", "select", "textarea"]):
        if el.name == "input" and el.get("type") in ("hidden", "submit", "button", "reset", "image"):
            continue
        if el.get("aria-label") or el.get("aria-labelledby") or el.find_parent("label"):
            continue
        if el.get("id") in labelled:
            continue
        issue = Issue("form-label", "1.3.1 / 3.3.2", "A", "Form control has no accessible label", _snip(el))
        if fix and el.get("placeholder"):
            el["aria-label"] = el["placeholder"]
            issue.fixed = True
        out.append(issue)
    return out


def check_links_buttons(soup, fix):
    out = []
    for el in soup.find_all(["a", "button"]):
        if el.name == "a" and not el.get("href"):
            continue
        text = el.get_text(strip=True)
        has_img_alt = any(i.get("alt") for i in el.find_all("img"))
        if not (text or el.get("aria-label") or el.get("aria-labelledby") or has_img_alt or el.get("title")):
            out.append(Issue("empty-name", "2.4.4 / 4.1.2", "A",
                             f"<{el.name}> has no accessible name", _snip(el)))
        elif text.lower() in {"click here", "here", "read more", "more"}:
            out.append(Issue("vague-link-text", "2.4.4", "A", "Link text is not descriptive", _snip(el)))
    return out


def check_headings(soup, fix):
    out, prev = [], 0
    for h in soup.find_all(re.compile(r"^h[1-6]$")):
        lvl = int(h.name[1])
        if prev and lvl > prev + 1:
            out.append(Issue("heading-order", "1.3.1", "A",
                             f"Heading level jumps from h{prev} to h{lvl}", _snip(h)))
        prev = lvl
    return out


def _hex_to_rgb(v):
    v = v.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) != 6:
        return None
    try:
        return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def _lum(rgb):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = map(ch, rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg, bg):
    l1, l2 = sorted((_lum(fg), _lum(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def check_contrast(soup, fix):
    out = []
    for el in soup.find_all(style=True):
        st = {k.strip().lower(): v.strip()
              for k, v in (p.split(":", 1) for p in el["style"].split(";") if ":" in p)}
        fg, bg = _hex_to_rgb(st.get("color", "")), _hex_to_rgb(st.get("background-color", ""))
        if fg and bg:
            r = contrast_ratio(fg, bg)
            if r < 4.5:
                out.append(Issue("color-contrast", "1.4.3", "AA",
                                 f"Contrast ratio {r:.2f}:1 is below 4.5:1", _snip(el)))
    return out


RULES = [check_lang, check_title, check_img_alt, check_form_labels,
         check_links_buttons, check_headings, check_contrast]
