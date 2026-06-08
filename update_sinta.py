#!/usr/bin/env python3
"""
Script to update SINTA profile data in research.html
Fetches latest data from SINTA 3 and updates the HTML file
"""

import re
import sys
from datetime import datetime
from html import escape

try:
    import sinta
except ImportError:
    print("Installing sinta-scraper...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sinta-scraper"])
    import sinta

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
IPR_URL_TEMPLATE = 'https://sinta.kemdiktisaintek.go.id/authors/profile/{}/?view=iprs'

import time

def fetch_sinta_data(author_id):
    """Fetch author data from SINTA with retries and better diagnostics"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"Fetching SINTA data for author ID: {author_id}... (Attempt {attempt + 1}/{max_retries})")
            
            # Add explicit timeout and headers
            author_data = sinta.author(author_id)
            
            # Debug: Print what we received
            print(f"DEBUG: Received data type: {type(author_data)}")
            print(f"DEBUG: Received data: {author_data}")
            
            # Handle case where sinta.author() returns a list
            if isinstance(author_data, list):
                if len(author_data) == 0:
                    print("Warning: Empty list returned from SINTA")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print("Error: No author data returned from SINTA after all retries")
                        sys.exit(1)
                author_data = author_data[0]
            
            if not author_data:
                print("Warning: None/empty data returned from SINTA")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print("Error: No author data returned from SINTA after all retries")
                    sys.exit(1)
            
            print("✓ Successfully fetched SINTA data")
            return author_data
            
        except Exception as e:
            print(f"Error fetching SINTA data on attempt {attempt + 1}: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print("Error: Failed to fetch SINTA data after all retries")
                sys.exit(1)

def generate_profile_card(data):
    """Generate the SINTA profile card HTML"""
    
    name = data.get('name', 'N/A')
    sinta_id = data.get('id', SINTA_ID)
    
    # Get affiliation info
    affiliation = data.get('affiliation', {})
    affiliation_name = affiliation.get('name', 'N/A')
    affiliation_id = affiliation.get('id', '')
    
    # Get department
    department = data.get('department', 'N/A')
    
    # Get articles/citations
    articles = data.get('articles', {})
    articles_scopus = articles.get('scopus', 0)
    articles_scholar = articles.get('scholar', 0)
    
    citations = data.get('citations', {})
    citations_scopus = citations.get('scopus', 0)
    citations_scholar = citations.get('scholar', 0)
    
    # Get indices
    h_index = data.get('h-index', {})
    h_index_scopus = h_index.get('scopus', 0)
    
    i10_index = data.get('i10-index', {})
    i10_index_scopus = i10_index.get('scopus', 0)
    
    # Get score
    score = data.get('score', {})
    score_overall = score.get('overall', 0)
    score_3years = score.get('3_years', 0)
    
    # Get subjects
    subjects = data.get('subjects', [])
    subjects_html = ''.join([f'<span class="subject-tag">{subject}</span>' for subject in subjects])
    
    # Get URL
    url = data.get('url', f'https://sinta.kemdiktisaintek.go.id/authors/profile/{sinta_id}')
    
    profile_card = f"""                    <!-- SINTA 3 Profile Card -->
                    <div class="sinta-profile">
                        <h3>{name}</h3>
                        <div class="sinta-affiliation">
                            <strong>Affiliation:</strong> <a href="https://sinta.kemdiktisaintek.go.id/affiliations/profile/{affiliation_id}" target="_blank">{affiliation_name}</a><br>
                            <strong>Department:</strong> {department}
                        </div>
                        <div class="sinta-id">
                            <strong>SINTA ID:</strong> {sinta_id} <span style="opacity: 0.7; font-size: 0.85rem;">(Updated: {datetime.now().strftime('%Y-%m-%d')})</span>
                        </div>
                        
                        <div class="sinta-metrics">
                            <div class="metric-item">
                                <div class="metric-label">Articles (Scopus)</div>
                                <div class="metric-value">{articles_scopus}</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-label">Citations (Scopus)</div>
                                <div class="metric-value">{citations_scopus}</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-label">H-Index</div>
                                <div class="metric-value">{h_index_scopus}</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-label">i10-Index</div>
                                <div class="metric-value">{i10_index_scopus}</div>
                            </div>
                        </div>

                        <div class="sinta-score">
                            <div class="sinta-score-title">SINTA Score</div>
                            <div class="score-grid">
                                <div class="score-item">
                                    <span>Overall:</span>
                                    <strong>{score_overall}</strong>
                                </div>
                                <div class="score-item">
                                    <span>3-Year:</span>
                                    <strong>{score_3years}</strong>
                                </div>
                            </div>
                        </div>

                        <div class="sinta-score-title">Research Subjects</div>
                        <div class="sinta-subjects">
                            {subjects_html}
                        </div>
                        
                        <a href="{url}" target="_blank" class="sinta-link">View Full SINTA Profile →</a>
                    </div>
"""
    return profile_card

def fetch_ipr_data(author_id):
    """Fetch IPR page content from SINTA."""
    url = IPR_URL_TEMPLATE.format(author_id)
    try:
        print(f"Fetching SINTA IPR page: {url}...")
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; SINTA-Profile-Updater/1.0)'
        })
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching SINTA IPR page: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    body = soup.body or soup

    candidates = []
    keywords = ['iprs', 'hak kekayaan', 'paten', 'patent', 'trademark', 'copyright', 'hak intelektual']
    for elem in body.find_all(['section', 'article', 'div', 'main'], recursive=True):
        text = elem.get_text(separator=' ', strip=True)
        if not text:
            continue
        low = text.lower()
        if any(keyword in low for keyword in keywords):
            candidates.append((len(text), elem))

    if candidates:
        candidates.sort(reverse=True, key=lambda item: item[0])
        best = candidates[0][1]
    else:
        best = body

    # Remove script/style tags from the extracted HTML fragment
    for tag in best(['script', 'style']):
        tag.extract()

    text = best.get_text(separator='\n', strip=True)
    lines = [line for line in (line.strip() for line in text.splitlines()) if line]
    lines = lines[:60]
    entries_html = ''.join(f'<div class="ipr-entry-detail"><p>{escape(line)}</p></div>' for line in lines)

    if not entries_html:
        entries_html = '<div class="ipr-entry-detail"><p>No IPR details were found on the SINTA IPR page.</p></div>'

    return entries_html


def generate_ipr_section(ipr_html, author_id):
    """Generate the SINTA IPR section HTML."""
    url = IPR_URL_TEMPLATE.format(author_id)
    if not ipr_html:
        ipr_html = '<div class="ipr-entry-detail"><p>The monthly IPR update could not retrieve content from the SINTA IPR page. Please check the page or run the script again.</p></div>'

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    return f"""                    <!-- SINTA IPR Content -->
                    <div id="sinta-ipr-content" class="ipr-section">
                        <div class="ipr-entry">
                            <div class="ipr-entry-title">IPR details from SINTA</div>
                            <div class="ipr-entry-detail">The information below is sourced from your SINTA IPR view. For the full page, open the link below.</div>
                        </div>
                        {ipr_html}
                        <div class="ipr-note">Updated from the SINTA IPR page: <a href="{url}" target="_blank" rel="noopener">{url}</a></div>
                        <div class="ipr-note">Last updated: {timestamp}</div>
                    </div>
                    <!-- END SINTA IPR Content -->
"""


def update_html_file(html_file, profile_card, ipr_section):
    """Update the HTML file with new SINTA profile and IPR content."""
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
        sys.exit(1)


def main():
    """Main function"""
    print("=" * 60)
    print("SINTA 3 Profile Updater")
    print("=" * 60)

    # Fetch SINTA data
    sinta_data = fetch_sinta_data(SINTA_ID)
    profile_card = generate_profile_card(sinta_data)

    # Fetch IPR page content
    ipr_html = fetch_ipr_data(SINTA_ID)
    ipr_section = generate_ipr_section(ipr_html, SINTA_ID)

    # Update HTML file
    html_file = 'publications.html'
    success = update_html_file(html_file, profile_card, ipr_section)

    if success:
        print("=" * 60)
        print(f"✓ Update completed successfully!")
        print("=" * 60)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
