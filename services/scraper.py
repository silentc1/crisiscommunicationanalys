import requests
from bs4 import BeautifulSoup
from typing import Optional
from .utils import limit_word_count

def extract_text_from_url(url: str) -> Optional[str]:
    try:
        print(f"\n=== Web Scraping Processing ===")
        print(f"URL: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        print(f"Response Status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove only script and style elements
        for element in soup(['script', 'style']):
            element.decompose()
        
        # Get main content
        main_content = (
            soup.find('article') or 
            soup.find('main') or 
            soup.find('div', class_=['content', 'article', 'story']) or
            soup.find('div', {'role': 'main'}) or
            soup.body
        )
        
        if main_content:
            text = main_content.get_text()
        else:
            text = soup.get_text()
        
        # Basic text cleanup
        lines = (line.strip() for line in text.splitlines())
        text = ' '.join(line for line in lines if line)
        
        limited_text = limit_word_count(text)
        
        print(f"Original Text Length: {len(text.split())} words")
        print(f"Limited Text Length: {len(limited_text.split())} words")
        
        return limited_text

    except Exception as e:
        print(f"Error scraping URL: {str(e)}")
        return None
