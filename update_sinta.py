#!/usr/bin/env python3
"""
Script to update SINTA profile data in publications.html
Fetches latest data directly from SINTA website
"""

import re
import sys
from datetime import datetime
from html import escape
import time

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing beautifulsoup4...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
    from bs4 import BeautifulSoup

# Your SINTA ID
SINTA_ID = 6775330
SINTA_URL = f'https://sinta.kemdiktisaintek.go.id/authors/profile/{SINTA_ID}'
IPR_URL = f'https://sinta.kemdiktisaintek.go.id/authors/profile/{SINTA_ID}/?view=iprs'

def fetch_sinta_profile():
    """Fetch author profile data directly from SINTA website"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"Fetching SINTA profile from {SINTA_URL}... (Attempt {attempt + 1}/{max_retries})")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(SINTA_URL, timeout=30, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract profile information
            profile_data = extract_profile_data(soup)
            
            if profile_data:
                print("✓ Successfully fetched SINTA profile data")
                return profile_data
            else:
                print("Warning: Could not extract profile data from page")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return None
            
        except Exception as e:
            print(f"Error fetching SINTA profile on attempt {attempt + 1}: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                return None

def extract_profile_data(soup):
    """Extract profile data from BeautifulSoup object"""
    try:
        data = {}
        
        # Try to extract name
        name_elem = soup.find('h1', class_='profile-name') or soup.find('h1')
        data['name'] = name_elem.get_text(strip=True) if name_elem else 'N/A'
        
        # Try to extract affiliation
        affiliation_elem = soup.find('div', class_='affiliation') or soup.find('span', class_='affiliation')
        data['affiliation'] = affiliation_elem.get_text(strip=True) if affiliation_elem else 'N/A'
        
        # Extract metrics from the page
        metrics = {}
        
        # Look for h-index
        h_index_elem = soup.find(string=re.compile(r'H-Index', re.I))
        if h_index_elem:
            parent = h_index_elem.parent
            value = parent.find_next(class_='metric-value')
            metrics['h_index'] = value.get_text(strip=True) if value else '0'
        
        # Look for i10-index
        i10_elem = soup.find(string=re.compile(r'i10-Index', re.I))
        if i10_elem:
            parent = i10_elem.parent
            value = parent.find_next(class_='metric-value')
            metrics['i10_index'] = value.get_text(strip=True) if value else '0'
        
        # Look for articles count
        articles_elem = soup.find(string=re.compile(r'Articles', re.I))
        if articles_elem:
            parent = articles_elem.parent
            value = parent.find_next(class_='metric-value')
            metrics['articles'] = value.get_text(strip=True) if value else '0'
        
        # Look for citations
        citations_elem = soup.find(string=re.compile(r'Citations', re.I))
        if citations_elem:
            parent = citations_elem.parent
            value = parent.find_next(class_='metric-value')
            metrics['citations'] = value.get_text(strip=True) if value else '0'
        
        data['metrics'] = metrics
        data['id'] = SINTA_ID
        data['url'] = SINTA_URL
        
        return data if data.get('name') != 'N/A' else None
        
    except Exception as e:
        print(f"Error extracting profile data: {e}")
        return None

def generate_profile_card(data):
    """Generate the SINTA profile card HTML"""
    
    name = data.get('name', 'N/A')
    affiliation = data.get('affiliation', 'N/A')
    metrics = data.get('metrics', {})
    sinta_id = data.get('id', SINTA_ID)
    url = data.get('url', SINTA_URL)
    
    h_index = metrics.get('h_index', '0')
    i10_index = metrics.get('i10_index', '0')
    articles = metrics.get('articles', '0')
    citations = metrics.get('citations', '0')
    
    profile_card = f"""                    <!-- SINTA 3 Profile Card -->
                    <div class="sinta-profile">
                        <h3>{name}</h3>
                        <div class="sinta-affiliation">
                            <strong>Affiliation:</strong> {affiliation}
                        </div>
                        <div class="sinta-id">
                            <strong>SINTA ID:</strong> {sinta_id} <span style="opacity: 0.7; font-size: 0.85rem;">(Updated: {datetime.now().strftime('%Y-%m-%d')})</span>
                        </div>
                        
                        <div class="sinta-metrics">
                            <div class="metric-item">
                                <div class="metric-label">Articles</div>
                                <div class="metric-value">{articles}</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-label">Citations</div>
                                <div class="metric-value">{citations}</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-label">H-Index</div>
                                <div class="metric-value">{h_index}</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-label">i10-Index</div>
                                <div class="metric-value">{i10_index}</div>
                            </div>
                        </div>
                        
                        <a href="{url}" target="_blank" class="sinta-link">View Full SINTA Profile →</a>
                    </div>
"""
    return profile_card

def fetch_ipr_data():
    """Fetch IPR page content from SINTA"""
    try:
        print(f"Fetching SINTA IPR page: {IPR_URL}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(IPR_URL, timeout=30, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style tags
        for tag in soup(['script', 'style']):
            tag.decompose()
        
        # Try to find IPR content
        ipr_content = soup.find('div', class_='ipr-content') or soup.find('section', class_='ipr')
        
        if ipr_content:
            text = ipr_content.get_text(separator='\n', strip=True)
            lines = [line for line in (line.strip() for line in text.splitlines()) if line]
            lines = lines[:30]  # Limit to first 30 lines
            entries_html = ''.join(f'<div class="ipr-entry-detail"><p>{escape(line)}</p></div>' for line in lines)
            print("✓ Successfully fetched SINTA IPR data")
            return entries_html
        else:
            print("⚠ No IPR content found on page")
            return None
            
    except Exception as e:
        print(f"Error fetching SINTA IPR page: {e}")
        return None

def generate_ipr_section(ipr_html):
    """Generate the SINTA IPR section HTML"""
    if not ipr_html:
        ipr_html = '<div class="ipr-entry-detail"><p>No IPR data available at this time. Please visit the SINTA IPR page for more details.</p></div>'
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    return f"""                    <!-- SINTA IPR Content -->
                    <div id="sinta-ipr-content" class="ipr-section">
                        <div class="ipr-entry">
                            <div class="ipr-entry-title">IPR details from SINTA</div>
                        </div>
                        {ipr_html}
                        <div class="ipr-note">View full IPR details: <a href="{IPR_URL}" target="_blank" rel="noopener">SINTA IPR Page</a></div>
                        <div class="ipr-note">Last updated: {timestamp}</div>
                    </div>
                    <!-- END SINTA IPR Content -->
"""

def update_html_file(html_file, profile_card, ipr_section):
    """Update the HTML file with new SINTA profile and IPR content"""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update profile card
        profile_pattern = r'<!--\s*SINTA 3 Profile Card\s*-->.*?<!--\s*END SINTA 3 Profile Card\s*-->'
        if not re.search(profile_pattern, content, re.DOTALL):
            print(f"✗ Could not find SINTA profile card block in {html_file}")
            return False
        content = re.sub(
            profile_pattern,
            profile_card,
            content,
            flags=re.DOTALL
        )

        # Update IPR section
        ipr_pattern = r'<!--\s*SINTA IPR Content\s*-->.*?<!--\s*END SINTA IPR Content\s*-->'
        if not re.search(ipr_pattern, content, re.DOTALL):
            print(f"✗ Could not find SINTA IPR content block in {html_file}")
            return False
        content = re.sub(
            ipr_pattern,
            ipr_section,
            content,
            flags=re.DOTALL
        )

        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✓ Successfully updated {html_file}")
        return True

    except Exception as e:
        print(f"Error updating HTML file: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("SINTA 3 Profile Updater")
    print("=" * 60)

    # Fetch SINTA data
    profile_data = fetch_sinta_profile()
    if not profile_data:
        print("✗ Failed to fetch SINTA profile data")
        sys.exit(1)
    
    profile_card = generate_profile_card(profile_data)

    # Fetch IPR page content
    ipr_html = fetch_ipr_data()
    ipr_section = generate_ipr_section(ipr_html)

    # Update HTML file
    html_file = 'publications.html'
    success = update_html_file(html_file, profile_card, ipr_section)

    if success:
        print("=" * 60)
        print("✓ Update completed successfully!")
        print("=" * 60)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
