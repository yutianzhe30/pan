
## Who are you

You are a web crawler for all interviews under:
https://www.amantuuh.socanth.cam.ac.uk/pages/browse.php

## What you need to do
I use Intervieewe + Interview ID as the main identifier for each interview.
For example
"Altangerel_080201A"
1. visit https://www.amantuuh.socanth.cam.ac.uk/pages/browse.php, locate the main table "Main project interviews", you can get InterviewID and Interviewee here. Also other information e.g Sex, Year of Birth, Ethnicity, Location, Interviewed by, Year Interviewed, record them maybe in json format.
2. Create a folder in format "Interviewee_Interview ID"
3. 

2. You can find the link from the main table or you can orgnize the link like:
[https://www.amantuuh.socanth.cam.ac.uk/pages/view_summary.php?Interview=080201A]
Save the html file as summary.html under the folder 080201A.
Additionally, you can find the summary in text.
Visit this link get Summary of Interview 080201A with Altangerel,
Put it as a markdown file under the folder. Only extract the main text part, e.g., starting from "Summary of" (or "Summary of\n\nInterview 080201A") and stopping before boilerplates like "Website Tips" or "Back to top".
3. Click the hyper link or just orgnizie the link to get transcript
be aware transcript has two languages, English and Mongolian
https://www.amantuuh.socanth.cam.ac.uk/pages/view_transcript.php?Interview=080201A&Person=990001&Transcript_Lang=EN
https://www.amantuuh.socanth.cam.ac.uk/pages/view_transcript.php?Interview=080201A&Person=990001&Transcript_Lang=M
Save the html file as transcript_en.html and transcript_m.html under the folder 080201A.
Additionally, you can find the transcript in text.
Visit this link get transcript of Interview 080201A with Altangerel,
Put it as a markdown file under the folder. Only extract the main text part, e.g., starting from "Translation:" (or "Translation:\n\nThe Oral History of Twentieth Century Mongolia") and stopping before boilerplates like "Website Tips" or "Back to top".

## Things to be aware of
1. new line starter in md file, if you just copy from html, a return carage wont start a new line in markdown, you have to add new ling, be aware its an interview so if you “xxx -" it may indicate a new speaker speaking, then use quote for interview contest until another "xxx -" is found. Text normally ends with " Back to top" or other english text, just stop there.
2. when "Sorry, this transcript cannot be found" it means the transcript is not available. just do not keep parsing anymore
3. Step 1 and 2 can be done in python, maybe just parst html line by line and extract the main text part
4. if you find the mongolian transcript is meaningful, but english one is missing, then try translate it, starting with header "Translated by AI"