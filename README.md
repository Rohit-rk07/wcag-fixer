# WCAG-Aware Accessibility Fixer

Scan HTML for common WCAG 2.2 failures and apply **safe** auto-fixes. Anything that needs human judgment
(e.g. meaningful alt text) is flagged, or optionally drafted by Claude.

## Rules
| Rule | WCAG | Auto-fix |
|---|---|---|
| `html-lang` | 3.1.1 | adds `lang="en"` |
| `page-title` | 2.4.2 | flag only |
| `img-alt` | 1.1.1 | `alt=""` for obviously decorative images; AI-drafted with `--ai-alt` |
| `form-label` | 1.3.1 / 3.3.2 | `aria-label` from placeholder |
| `empty-name` / `vague-link-text` | 2.4.4 / 4.1.2 | flag only |
| `heading-order` | 1.3.1 | flag only |
| `color-contrast` (inline styles) | 1.4.3 | flag only |

## Usage
```bash
pip install -e ".[dev]"
wcag-fix examples/            # report
wcag-fix site/ --fix          # apply safe fixes in place
wcag-fix site/ --fix --ai-alt # draft alt text with Claude (pip install -e ".[ai]")
wcag-fix site/ --json         # machine-readable; exit code 1 if unfixed issues remain (CI-friendly)
pytest
```

## Limits
Static analysis catches only a fraction of WCAG problems. Always combine with manual and screen-reader testing.

## Roadmap
CSS-file contrast, React/JSX support, GitHub Action, ARIA validity checks.
