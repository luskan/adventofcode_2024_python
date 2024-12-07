def verify_result(actual, expected, part):
    """Verify if the actual result matches the expected result."""
    if expected is None:
        return "❓ (no expected result)"

    if actual == expected:
        print(f"✅ {actual}")
    else:
        print(f"Part {part} failed")
        print(f"❌ Got: {actual}, Expected: {expected}")
        exit(1)