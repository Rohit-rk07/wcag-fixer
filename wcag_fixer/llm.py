"""Optional: draft alt text with Claude. Needs `pip install anthropic` and ANTHROPIC_API_KEY."""


def make_alt_provider(model: str = "claude-sonnet-4-5"):
    import anthropic
    client = anthropic.Anthropic()

    def provider(img):
        ctx = f"src={img.get('src')!r}; nearby text: {img.parent.get_text(' ', strip=True)[:200]!r}"
        msg = client.messages.create(
            model=model, max_tokens=60,
            messages=[{"role": "user", "content":
                       "Write concise alt text (max 125 chars, no 'image of') for this <img>. "
                       "Reply with only the alt text, or EMPTY if decorative.\n" + ctx}])
        text = msg.content[0].text.strip()
        return "" if text == "EMPTY" else text
    return provider
