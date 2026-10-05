import argparse, json, sys, pathlib
from .core import analyze

EXTS = {".html", ".htm"}


def main(argv=None):
    p = argparse.ArgumentParser(prog="wcag-fix", description="Scan HTML for WCAG issues and apply safe fixes.")
    p.add_argument("paths", nargs="+")
    p.add_argument("--fix", action="store_true", help="write safe fixes back to files")
    p.add_argument("--ai-alt", action="store_true", help="draft alt text with Claude (needs ANTHROPIC_API_KEY)")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)

    provider = None
    if a.ai_alt:
        from .llm import make_alt_provider
        provider = make_alt_provider()

    files = []
    for s in a.paths:
        path = pathlib.Path(s)
        files += [f for f in path.rglob("*") if f.suffix in EXTS] if path.is_dir() else [path]

    report, remaining = {}, 0
    for f in files:
        issues, new = analyze(f.read_text(encoding="utf-8"), fix=a.fix, alt_provider=provider)
        if a.fix:
            f.write_text(new, encoding="utf-8")
        report[str(f)] = [i.__dict__ for i in issues]
        remaining += sum(not i.fixed for i in issues)

    if a.json:
        print(json.dumps(report, indent=2))
    else:
        for f, issues in report.items():
            print(f"\n{f}")
            for i in issues:
                mark = "FIXED" if i["fixed"] else "ISSUE"
                print(f"  [{mark}] WCAG {i['wcag']} ({i['level']}) {i['rule']}: {i['message']}\n          {i['snippet']}")
    return 1 if remaining else 0


if __name__ == "__main__":
    sys.exit(main())
