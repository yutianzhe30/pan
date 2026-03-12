import scraper
import os

if __name__ == "__main__":
    # Ensure we are in the right directory
    os.chdir("/home/tiyu/Documents/pan")
    print("Processing 080201A...")
    scraper.process_interview("080201A")
    print("Done.")
