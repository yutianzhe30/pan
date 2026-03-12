import os
import re
import requests
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import concurrent.futures
from googletrans import Translator

BASE_URL = "https://www.amantuuh.socanth.cam.ac.uk/"

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def fetch_background_data():
    browse_url = f"{BASE_URL}pages/browse.php"
    r = requests.get(browse_url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table')
    if not table:
        return []
        
    records = []
    
    rows = table.find_all('tr')
    for row in rows[1:]:  # Skip header row
        cols = row.find_all('td')
        if len(cols) >= 8:
            id_text = cols[0].get_text(strip=True)
            interviewee_text = cols[1].get_text(strip=True)
            
            record = {
                "InterviewID": id_text,
                "Interviewee": interviewee_text,
                "Sex": cols[2].get_text(strip=True),
                "Year of Birth": cols[3].get_text(strip=True),
                "Ethnicity": cols[4].get_text(strip=True),
                "Location": cols[5].get_text(strip=True),
                "Interviewed by": cols[6].get_text(strip=True),
                "Year Interviewed": cols[7].get_text(strip=True)
            }
            records.append(record)
            
    return records

def extract_bio(html_content, dir_path):
    soup = BeautifulSoup(html_content, 'html.parser')
    main_div = soup.find('div', {'id': 'main'})
    if not main_div:
        return
        
    # Extract Photo
    img_tag = main_div.find('img')
    if img_tag and 'src' in img_tag.attrs:
        img_url = urljoin(f"{BASE_URL}pages/", img_tag['src'])
        try:
            r_img = requests.get(img_url, timeout=10)
            if r_img.status_code == 200:
                with open(os.path.join(dir_path, 'Photo.jpg'), 'wb') as f:
                    f.write(r_img.content)
        except Exception as e:
            print(f"Failed to download photo {img_url}: {e}")
            
    # Extract BIO text
    text = main_div.get_text(separator='\n', strip=True)
    lines = text.split('\n')
    bio_lines = []
    for line in lines:
        if "Themes for this interview are:" in line:
            break
        if line.strip():
            bio_lines.append(line.strip())
            
    with open(os.path.join(dir_path, 'Biology.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(bio_lines))


def extract_summary_markdown(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    main_div = soup.find('div', {'id': 'main'})
    if not main_div:
        return ""
        
    text = main_div.get_text(separator='\n', strip=True)
    lines = text.split('\n')
    
    start_idx = 0
    for i, line in enumerate(lines):
        if "Themes for this interview are:" in line:
            start_idx = i
            break

    filtered_lines = [line.strip() for line in lines[start_idx:] if line.strip()]
    return '\n\n'.join(filtered_lines).strip()

def extract_transcript_markdown(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    lines = text.split('\n')
    
    if "Sorry, this transcript cannot be found" in text:
        return "NOT_FOUND"
        
    start_idx = -1
    for i, line in enumerate(lines):
        if re.match(r'^Translation:', line.strip(), re.IGNORECASE):
            start_idx = i
            break
            
    if start_idx == -1:
        start_idx = 0
        
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        if re.match(r'^(Website Tips|Back to top)', lines[i].strip(), re.IGNORECASE):
            end_idx = i
            break
            
    filtered_lines = [line.strip() for line in lines[start_idx:end_idx] if line.strip()]
    
    formatted_lines = []
    in_quote = False
    for line in filtered_lines:
        if line.endswith('-'):
            formatted_lines.append('\n' + line + '\n')
            in_quote = True
        else:
            if in_quote and line:
                formatted_lines.append(f"> {line}")
            elif line:
                formatted_lines.append(line)
            
    return '\n\n'.join(formatted_lines).strip()

def process_interview(record):
    interview_id = record['InterviewID']
    interviewee = record['Interviewee']
    
    # Create main dir: Interviewee_InterviewID
    dir_name = f"{interviewee}_{interview_id}".replace(" ", "_").replace("/", "_")
    dir_path = os.path.join(os.getcwd(), dir_name)
    create_dir(dir_path)
    
    # Create backup_html dir
    backup_path = os.path.join(dir_path, "backup_html")
    create_dir(backup_path)
    
    # Save background.json
    with open(os.path.join(dir_path, "background.json"), "w", encoding='utf-8') as f:
        json.dump(record, f, indent=4, ensure_ascii=False)
        
    # 1. Fetch, save, and parse summary
    summary_url = f"{BASE_URL}pages/view_summary.php?Interview={interview_id}"
    try:
        r = requests.get(summary_url, timeout=10)
        r.raise_for_status()
        summary_html = r.text
        
        with open(os.path.join(backup_path, 'summary.html'), 'w', encoding='utf-8') as f:
            f.write(summary_html)
            
        # Extract Biology.txt and Photo.jpg
        extract_bio(summary_html, dir_path)
        
        # Extract Summary_EN.md
        summary_md = extract_summary_markdown(summary_html)
        if summary_md:
            with open(os.path.join(dir_path, 'Summary_EN.md'), 'w', encoding='utf-8') as f:
                f.write(summary_md)
                
    except Exception as e:
        print(f"[{interview_id}] Failed to download/process summary: {e}")
        return
        
    person_matches = re.findall(r'Person=(\d+)', summary_html)
    if not person_matches:
        print(f"[{interview_id}] Could not find Person ID in summary")
        return
        
    person_id = person_matches[0]
    
    # 2. Fetch transcripts
    langs = {'EN': 'transcript_en', 'M': 'transcript_m'}
    transcripts = {}
    
    for lang, prefix in langs.items():
        url = f"{BASE_URL}pages/view_transcript.php?Interview={interview_id}&Person={person_id}&Transcript_Lang={lang}"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                html_text = r.text
                
                with open(os.path.join(backup_path, f'{prefix}.html'), 'w', encoding='utf-8') as f:
                    f.write(html_text)
                    
                md_text = extract_transcript_markdown(html_text)
                transcripts[lang] = md_text
                
                if md_text and md_text != "NOT_FOUND":
                    with open(os.path.join(dir_path, f'{prefix}.md'), 'w', encoding='utf-8') as f:
                        f.write(md_text)
            else:
                transcripts[lang] = "NOT_FOUND"
        except Exception as e:
            print(f"[{interview_id}] Error getting {lang} transcript: {e}")
            transcripts[lang] = "NOT_FOUND"
            
    # 4. If Mongolian is meaningful but English is missing, translate it
    m_text = transcripts.get('M')
    en_text = transcripts.get('EN')
    if m_text and m_text != "NOT_FOUND" and en_text == "NOT_FOUND":
        print(f"[{interview_id}] English missing, translating Mongolian to English...")
        try:
            translator = Translator()
            chunks = m_text.split('\n\n')
            translated_chunks = []
            current_chunk = ""
            for chunk in chunks:
                if len(current_chunk) + len(chunk) < 4500:
                    current_chunk += chunk + "\n\n"
                else:
                    if current_chunk.strip():
                        translated_chunks.append(translator.translate(current_chunk.strip(), src='mn', dest='en').text)
                    current_chunk = chunk + "\n\n"
            if current_chunk.strip():
                translated_chunks.append(translator.translate(current_chunk.strip(), src='mn', dest='en').text)
                
            translated_text = "\n\n".join(translated_chunks)
            
            with open(os.path.join(dir_path, 'transcript_en.md'), 'w', encoding='utf-8') as f:
                f.write("# Translated by AI\n\n" + translated_text)
                
        except Exception as e:
            print(f"[{interview_id}] Translation failed: {e}")

    print(f"[{interview_id}] Successfully processed.")

def main():
    print("Fetching interview metadata from browse.php...")
    records = fetch_background_data()
    print(f"Found {len(records)} interviews. Starting crawler...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_interview, records)
        
    print("Crawling complete.")

if __name__ == '__main__':
    main()
