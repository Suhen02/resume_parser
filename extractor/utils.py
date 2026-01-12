import re

def clean_text(text: str) -> str:
    text = re.sub(r'[•●▪]', '-', text)

    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n', text)

    return text.strip()
