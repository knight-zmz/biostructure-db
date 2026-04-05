def parse_header(text: str) -> dict:
    result = {}
    for line in text.strip().splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        result[k.strip().lower()] = v.strip()

    # 故意写错：应该是 entry_id，这里却写成 entry
    return {
        "entry_id": result.get("entry_id"),
        "method": result.get("method")
    }
