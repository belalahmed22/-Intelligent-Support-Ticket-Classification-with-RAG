import re


def preprocess_text(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"http\S+|www\.\S+", " ", value)
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()
