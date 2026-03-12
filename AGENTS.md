
## Who are you

You are a web crawler for all interviews under:
https://www.amantuuh.socanth.cam.ac.uk/pages/browse.php

## What you need to do
I use Intervieewe + Interview ID as the main identifier for each interview.
For example
"Altangerel_080201A"
1. visit [https://www.amantuuh.socanth.cam.ac.uk/pages/browse.php], locate the main table "Main project interviews", you can get InterviewID and Interviewee here. Also other information e.g Sex, Year of Birth, Ethnicity, Location, Interviewed by, Year Interviewed, record them in JSON format in a file named `background.json`.
2. Create a folder in format "Interviewee_Interview ID",create a subfolder "backup_html" in each
3. Record the json in name "background.json"

4. visit [https://www.amantuuh.socanth.cam.ac.uk/pages/view_summary.php?Interview=080201A](Adjust InterviewID),save the html file as summary.html under "backup_html"
5. Extract BIO (first part of main div, consist of name, a photo, Basic Information, Additional Information), put BIO in `Biology.txt` line by line, and save the pic as `Photo.jpg` in the current interview folder.
6. Extract "Summary of Interview" from the html file, put it as "Summary_EN.md". Only extract the main text part, e.g., starting from "Summary of" (or "Summary of\n\nInterview 080201A") and stopping right before "To read a full...". Include the "Themes" and "Alternative keywords" sections.

7. Click the hyper link or just orgnizie the link to get transcript be aware transcript has two languages, English and Mongolian:
[https://www.amantuuh.socanth.cam.ac.uk/pages/view_transcript.php?Interview=080201A&Person=990001&Transcript_Lang=EN]
[https://www.amantuuh.socanth.cam.ac.uk/pages/view_transcript.php?Interview=080201A&Person=990001&Transcript_Lang=M]
Save the html file as transcript_en.html and transcript_m.html under the folder "backup_html".
You can find also interview transcript in text format in the website, usually start with "Translation"
Put it them as markdown files  "transcript_en.md" and "transcript_m.md" respectively. Only extract the main text part, e.g., starting from "Translation:" (or "Translation:\n\nThe Oral History of Twentieth Century Mongolia") and stopping before boilerplates like "Website Tips" or "Back to top".

## Suggests:
Adjust scraper.py use some functions to extract the text part e.g.
- Parse Summary.html and extract summary text
- Parse transcript_en.html and extract transcript text

## Things to be aware of
1. When put html context into markdown, new line in markdown wont trigger a "new line", add addtional new line or paragraph seperator if needed
2. When parsing interview text, text start with “xxx -" indicates a new speaker speaking, then use quote for interview contest until another "xxx -"  or text end is found. Text normally ends with " Back to top" or other english text, just stop there.
3. when "Sorry, this transcript cannot be found" it means the transcript is not available. just do not keep parsing anymore
4. if you find the mongolian transcript is meaningful, but english one is missing, then try translate it, starting with header "Translated by AI"