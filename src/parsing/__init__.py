from bs4 import BeautifulSoup

__all__ = ['get_paragraphs']


def get_paragraphs(html: str) -> list[str]:
    soup = BeautifulSoup(html, 'html.parser')
    paragraphs = soup.select('p')

    return [p.text for p in paragraphs]
