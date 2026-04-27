def parse_tags(raw: str) -> list[str]:
    """
    Parse a comma-separated tag string into a clean, deduplicated list.

    Rules:
    - split on commas
    - strip whitespace from each token
    - lowercase
    - drop empty string
    - deduplicate, preserving first-seen order
    """

    seen = set()
    result = []

    for token in raw.split(","):
        tag = token.strip().lower()
        if tag and tag not in seen:
            seen.add(tag)
            result.append(tag)

    return result
