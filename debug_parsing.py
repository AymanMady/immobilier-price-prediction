
import sys
from pathlib import Path
import re

# Ajouter src au path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / 'src'))

from src.scraping.voursa import parse_listing_page
from src.scraping.common import fetch

url = "https://voursa.com/FR/categories/real_estate/ads/نيمرو-ف-اغنودرت-للبيع--332e"
print(f"Fetching {url}...")
html = fetch(url)
print(f"HTML length: {len(html)}")

data = parse_listing_page(html, url)
print("Data extracted:")
print(f"Surface: {data.get('surface_m2')}")
print(f"Description: {data.get('description')}")

# Debug regex locally
desc = data.get('description', '')
if desc:
    print(f"Testing regex on description: '{desc}'")
    match = re.search(r'(\d+)\s*(m²|m2|mètre|superficie|m|م)', desc, re.I)
    if match:
        print(f"Match found: {match.groups()}")
    else:
        print("No match found in description.")

# Also test on raw html text content just in case
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'lxml')
text_content = soup.get_text()
# print(f"Text content sample: {text_content[:500]}")
match_text = re.search(r'(\d+)\s*(m²|m2|mètre|superficie|m|م)', text_content, re.I)
if match_text:
    print(f"Match found in text_content: {match_text.groups()}")
else:
    print("No match found in text_content.")
