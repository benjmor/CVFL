from bs4 import BeautifulSoup
from get_all_final_places_urls import get_all_final_places_urls
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service
from tabroom_login import login_to_tabroom
from tabroom_login import login_to_tabroom
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.chrome import ChromeDriverManager
import argparse
import csv
import os
import re
import time


def extract_event_abbreviation(event_name):
    """Convert event name to abbreviation."""
    abbreviation_map = {
        "Congress": "CON",
        "Lincoln Douglas": "LD",
        "Parliamentary": "PAR",
        "Policy": "PD",
        "Presiding Officer": "PO",
        "Public Forum": "PF",
        "Declamation": "DEC",
        "Dramatic Interpretation": "DI",
        "Duo Interpretation": "DUO",
        "Humorous Interpretation": "HI",
        "Improv": "IMP",
        "Informative Speaking": "INFO",
        "International Extemporaneous": "IX",
        "National Extemporaneous": "NX",
        "Original Advocacy": "OA",
        "Original Oratory": "OO",
        "Original Prose/Poetry": "OPP",
        "Original ProsePoetry": "OPP",
        "Program Oral Interpretation": "POI",
    }
    return abbreviation_map.get(event_name, event_name[:3].upper())


def parse_debate_html(html_file, event_name):
    """
    Parse an HTML page with debate competition tables and extract competitor info.
    Returns a CSV with student/entry name and school, ordered by placement priority.
    Tables are processed in order - first table has highest priority.
    """
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Find all tables
    tables = soup.find_all("table")

    entries = []

    event_shortname = extract_event_abbreviation(event_name)

    # Process each table in order (first table = highest priority)
    rank = 1
    for table in tables:
        tbody = table.find("tbody")
        if not tbody:
            continue

        rows = tbody.find_all("tr")

        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 3:
                # Extract entry name (2nd column) and school (3rd column)
                entry_name = cells[1].get_text(strip=True)
                school = cells[2].get_text(strip=True)

                if entry_name and school:
                    entries.append([event_shortname, rank, entry_name, school])
            rank += 1
    return entries


def download_html(browser, url):
    """Download HTML content from a URL and save to a local file."""
    browser.get(url)

    # sleep for 1 second
    time.sleep(1)

    # Extract event name from URL for filename
    match = re.search(r"result_id=(\d+)", url)
    event_id = match.group(1) if match else "unknown"
    filename = f"event_{event_id}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(browser.page_source)
    return filename


if __name__ == "__main__":
    # Set up argument parser for the tournament IDs
    parser = argparse.ArgumentParser(
        description="Scrape final places URLs for specified tournaments."
    )
    parser.add_argument(
        "--debate_tournament_id",
        type=str,
        help="The ID of the debate tournament",
        default="36575",
    )  # 36575 for CVFL Debate 2026
    parser.add_argument(
        "--speech_tournament_id",
        type=str,
        help="The ID of the speech tournament",
        default="32305",
    )  # "32305" for CVFL 2025
    # Add arguments for Tabroom username and password
    parser.add_argument(
        "--tabroom_username",
        type=str,
        help="Tabroom username",
        # required=True,
        default="redbeardben@gmail.com",
    )
    parser.add_argument(
        "--tabroom_password",
        type=str,
        help="Tabroom password",
        required=True,
    )

    args = parser.parse_args()
    debate_tournament_id = args.debate_tournament_id
    speech_tournament_id = args.speech_tournament_id

    ##### Set up browser to scrape Tabroom results #####
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run without opening a browser window

    browser = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    login_to_tabroom(
        browser,
        args.tabroom_username,
        args.tabroom_password,
    )
    ##################################################

    base_url = f"https://www.tabroom.com/index/tourn/results/index.mhtml?tourn_id="
    final_places_urls = []
    if debate_tournament_id:
        final_places_urls.extend(
            get_all_final_places_urls(browser, base_url + debate_tournament_id)
        )
    if speech_tournament_id:
        final_places_urls.extend(
            get_all_final_places_urls(browser, base_url + speech_tournament_id)
        )
    ##################################################
    all_results = []
    for event_name, url in final_places_urls:
        print(f"Processing {url}")
        html_file = download_html(browser, url)
        if html_file:
            # Find the event abbreviation in the HTML file, looking for the <h4> header that contains the event abbreviation and then "Results"
            with open(html_file, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
            headers = soup.find_all("h4")
            header = None
            for h in headers:
                if "Results" in h.get_text() and "Event Results" not in h.get_text():
                    header = h
                    break

            results = parse_debate_html(html_file, event_name)
            all_results.extend(results)
            # Delete the HTML file after processing
            os.remove(html_file)

    # Write to CSV
    with open("final_places.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Event", "Rank", "Entry Name", "School"])  # Header
        writer.writerows(all_results)

    print("Done! Results saved to final_places.csv. Copy these to the raw dump.")
