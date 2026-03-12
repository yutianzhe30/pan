import os
import re
import requests
from bs4 import BeautifulSoup
import concurrent.futures
from googletrans import Translator

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def extract_markdown(html_content, start_pattern):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    lines = text.split('\n')
    
    # 2. Check if transcript not found
    if "Sorry, this transcript cannot be found" in text:
        return "NOT_FOUND"
        
    start_idx = -1
    for i, line in enumerate(lines):
        if re.match(start_pattern, line.strip(), re.IGNORECASE):
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
    
    # 1. Enforce new lines and quotes
    formatted_lines = []
    in_quote = False
    for line in filtered_lines:
        if line.endswith('-'):
            # It indicates a new speaker
            formatted_lines.append('\n' + line + '\n')
            in_quote = True
        else:
            if in_quote and line:
                formatted_lines.append(f"> {line}")
            elif line:
                formatted_lines.append(line)
            
    return '\n\n'.join(formatted_lines).strip()

def process_interview(interview_id):
    dir_path = os.path.join(os.getcwd(), interview_id)
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
        if summary_md != "NOT_FOUND":
            with open(os.path.join(dir_path, 'summary.md'), 'w', encoding='utf-8') as f:
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
        url = f"https://www.amantuuh.socanth.cam.ac.uk/pages/view_transcript.php?Interview={interview_id}&Person={person_id}&Transcript_Lang={lang}"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                html_text = r.text
                with open(os.path.join(dir_path, f'{prefix}.html'), 'w', encoding='utf-8') as f:
                    f.write(html_text)
                    
                md_text = extract_markdown(html_text, r'^Translation:')
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
            # Split by blocks to avoid exceeding text length limitations and maintain formatting
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
