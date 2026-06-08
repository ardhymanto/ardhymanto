#!/usr/bin/env python3
"""
Diagnostic script to inspect SINTA profile page structure
"""

import requests
from bs4 import BeautifulSoup

SINTA_ID = 6775330
SINTA_URL = f'https://sinta.kemdiktisaintek.go.id/authors/profile/{SINTA_ID}'

try:
    import requests
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
    from bs4 import BeautifulSoup

print(f"Fetching {SINTA_URL}...")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(SINTA_URL, timeout=30, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print("\n" + "="*80)
    print("PAGE TITLE")
    print("="*80)
    print(soup.title.string if soup.title else "No title found")
    
    print("\n" + "="*80)
    print("ALL H1, H2, H3 ELEMENTS (Headers/Names)")
    print("="*80)
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4']):
        print(f"{tag.name}: {tag.get_text(strip=True)[:100]}")
    
    print("\n" + "="*80)
    print("ALL DIVS WITH CLASS ATTRIBUTES (First 20)")
    print("="*80)
    divs = soup.find_all('div', class_=True)
    for i, div in enumerate(divs[:20]):
        classes = ' '.join(div.get('class', []))
        text = div.get_text(strip=True)[:80]
        print(f"{i+1}. class='{classes}' | text: {text}")
    
    print("\n" + "="*80)
    print("ALL NUMBERS/METRICS VISIBLE ON PAGE")
    print("="*80)
    # Look for common metric patterns
    for elem in soup.find_all(['span', 'div', 'h5', 'h4', 'p']):
        text = elem.get_text(strip=True)
        # Check if it's a number or contains metric keywords
        if (text.isdigit() or any(word in text.lower() for word in ['h-index', 'citations', 'articles', 'publications', 'scopus', 'score'])):
            print(f"  {elem.name} (class='{' '.join(elem.get('class', []))}'):  {text}")
    
    print("\n" + "="*80)
    print("CHECKING FOR COMMON CLASS NAMES")
    print("="*80)
    
    common_classes = ['metrics', 'profile', 'card', 'stats', 'index', 'badge', 'score', 'affiliation']
    for class_name in common_classes:
        found = soup.find_all(class_=class_name)
        if found:
            print(f"\n✓ Found {len(found)} elements with class '{class_name}'")
            for elem in found[:3]:
                print(f"   {elem.name}: {elem.get_text(strip=True)[:100]}")
    
    print("\n" + "="*80)
    print("FULL HTML (First 5000 characters)")
    print("="*80)
    print(soup.prettify()[:5000])
    
    # Save full HTML for inspection
    with open('sinta_debug.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("\n✓ Full HTML saved to 'sinta_debug.html'")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
