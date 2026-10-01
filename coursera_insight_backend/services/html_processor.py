from bs4 import BeautifulSoup

def extract_html_text(html: str) -> str:
    """Remove scripts/styles/tags and return readable text from HTML content."""
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style"]):
        element.decompose()

    return " ".join(soup.get_text(separator=" ").split())
