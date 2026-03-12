import os
import re
import requests
from bs4 import BeautifulSoup
import concurrent.futures

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def extract_markdown(html_content, start_pattern):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator='\n\n', strip=True)
    lines = text.split('\n')
    
    start_idx = -1
    for i, line in enumerate(lines):
        if re.match(start_pattern, line.strip(), re.IGNORECASE):
            start_idx = i
            break
            
    if start_idx == -1:
        # Fallback if pattern not found
        start_idx = 0
        
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        if re.match(r'^(Website Tips|Back to top)', line.strip(), re.IGNORECASE):
            end_idx = i
            break
            
    filtered_text = '\n'.join([line for line in lines[start_idx:end_idx] if line.strip()])
    return filtered_text

def process_interview(interview_id):
    dir_path = os.path.join('/home/tiyu/Documents/pan', interview_id)
    create_dir(dir_path)
    
    # 1. Fetch, save, and parse summary
    summary_url = f"https://www.amantuuh.socanth.cam.ac.uk/pages/view_summary.php?Interview={interview_id}"
    try:
        r = requests.get(summary_url, timeout=10)
        r.raise_for_status()
        summary_html = r.text
        with open(os.path.join(dir_path, 'summary.html'), 'w', encoding='utf-8') as f:
            f.write(summary_html)
            
        summary_md = extract_markdown(summary_html, r'^Summary of')
        with open(os.path.join(dir_path, 'summary.md'), 'w', encoding='utf-8') as f:
            f.write(summary_md)
            
    except Exception as e:
        print(f"[{interview_id}] Failed to download/process summary: {e}")
        return
        
    # Find Person ID
    person_matches = re.findall(r'Person=(\d+)', summary_html)
    if not person_matches:
        print(f"[{interview_id}] Could not find Person ID in summary")
        return
        
    # Assume first Person ID is the main interviewee
    person_id = person_matches[0]
    
    # 2. Fetch transcripts
    langs = {'EN': 'transcript_en', 'M': 'transcript_m'}
    for lang, prefix in langs.items():
        url = f"https://www.amantuuh.socanth.cam.ac.uk/pages/view_transcript.php?Interview={interview_id}&Person={person_id}&Transcript_Lang={lang}"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                html_text = r.text
                with open(os.path.join(dir_path, f'{prefix}.html'), 'w', encoding='utf-8') as f:
                    f.write(html_text)
                    
                md_text = extract_markdown(html_text, r'^Translation:')
                with open(os.path.join(dir_path, f'{prefix}.md'), 'w', encoding='utf-8') as f:
                    f.write(md_text)
            else:
                print(f"[{interview_id}] Failed to get {lang} transcript (Status {r.status_code})")
        except Exception as e:
            print(f"[{interview_id}] Error getting {lang} transcript: {e}")
            
    print(f"[{interview_id}] Successfully processed.")

def main():
    # Load IDs from the interviews page
    try:
        with open('/tmp/interviews.html', 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        r = requests.get("https://www.amantuuh.socanth.cam.ac.uk/pages/view_interviewer.php?ID=004&interviewer=Erdenetuya")
        text = r.text
        
    matches = re.findall(r'view_summary\.php\?Interview=([A-Za-z0-9]+)', text)
    matches += re.findall(r'view_transcript\.php\?Interview=([A-Za-z0-9]+)', text)
    unique_ids = sorted(list(set(matches)))
    
    print(f"Found {len(unique_ids)} interview IDs. Starting crawler...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_interview, unique_ids)
        
    print("Crawling complete.")

if __name__ == '__main__':
    main()
