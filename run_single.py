import scraper
import os

if __name__ == "__main__":
    # Ensure we are in the right directory
    os.chdir("/home/tiyu/Documents/pan")
    print("Processing 080201A...")
    record = {
        "InterviewID": "080201A",
        "Interviewee": "Altangerel",
        "Sex": "m",
        "Year of Birth": "1944",
        "Ethnicity": "Buriad",
        "Location": "Selenge",
        "Interviewed by": "Erdenetuya",
        "Year Interviewed": "2008-02-26"
    }
    scraper.process_interview(record)
    print("Done.")
