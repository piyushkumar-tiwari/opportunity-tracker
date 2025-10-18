import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
import json
import traceback
import time

# --- CONFIGURATION ---
STATE_FILE = "seen_jobs.json"
REQUEST_TIMEOUT = 15
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# --- MODEL 4: THE AI FILTER ---
def is_job_relevant(title):
    """Uses the Gemini AI to check if a job is relevant based on title."""
    try:
        api_key = os.environ["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are a research assistant for a student in robotics.
        My specific interests are: "Reinforcement Learning", "RL", and "Robotics".
        
        Based *only* on the job title, is this job relevant to these *specific* interests?
        
        Answer with a single word: YES or NO.
        
        TITLE: {title}
        """
        
        response = model.generate_content(prompt)
        answer = response.text.strip().upper()
        
        if "YES" in answer:
            print(f"AI Check: YES - '{title}'")
            return True
        else:
            print(f"AI Check: NO - '{title}'")
            return False
            
    except Exception as e:
        print(f"Error checking AI: {e}")
        return False

# --- MODEL 3: THE SCRAPERS (ALL SIMPLE REQUESTS) ---

def scrape_eth_zurich():
    """Scrapes job postings from ETH Zurich."""
    url = "https://jobs.ethz.ch/site/index?text=&group=2&group=3"
    print(f"Scraping ETH Zurich...")
    found_jobs = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status() 
        soup = BeautifulSoup(response.text, 'html.parser')
        job_links = soup.find_all('a', attrs={'data-cy': 'job-list-item-link'})
        for link in job_links:
            title_elem = link.find('div', attrs={'data-cy': 'job-list-item-title'})
            if title_elem:
                title = title_elem.text.strip()
                href = link.get('href')
                full_link = f"https://jobs.ethz.ch{href}" if href.startswith('/') else href
                found_jobs.append({'title': title, 'link': full_link, 'source': 'ETH Zurich'})
    except Exception as e:
        print(f"Error scraping ETH Zurich: {e}")
    return found_jobs

def scrape_cambridge():
    """Scrapes job postings from University of Cambridge."""
    url = "https://www.jobs.cam.ac.uk/job/?listing_type=research"
    print(f"Scraping Cambridge...")
    found_jobs = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all('div', class_='card')
        for card in job_cards:
            h3_elem = card.find('h3')
            if h3_elem:
                title_element = h3_elem.find('a')
                if title_element:
                    title = title_element.text.strip()
                    href = title_element.get('href')
                    full_link = f"https://www.jobs.cam.ac.uk{href}" if href.startswith('/') else href
                    found_jobs.append({'title': title, 'link': full_link, 'source': 'Cambridge'})
    except Exception as e:
        print(f"Error scraping Cambridge: {e}")
    return found_jobs

def scrape_ucl():
    """Scrapes research jobs from UCL London. (FIXED)"""
    url = "https://www.ucl.ac.uk/work-at-ucl/search-jobs?collection=job-opportunities-beta&query=research&profile=job-opportunities-beta&sort=advertdatestring"
    print(f"Scraping UCL London...")
    found_jobs = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Corrected selector
        job_cards = soup.find_all('div', class_='sf-search-result__content')
        for card in job_cards:
            h3_elem = card.find('h3')
            if h3_elem:
                title_element = h3_elem.find('a')
                if title_element:
                    title = title_element.text.strip()
                    href = title_element.get('href')
                    full_link = href # UCL uses absolute links
                    found_jobs.append({'title': title, 'link': full_link, 'source': 'UCL'})
    except Exception as e:
        print(f"Error scraping UCL: {e}")
    return found_jobs

def scrape_tu_munich():
    """Scrapes academic staff jobs from TU Munich."""
    url = "https://portal.mytum.de/jobs/wissenschaftler"
    print(f"Scraping TU Munich...")
    found_jobs = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        job_items = soup.find_all('div', class_='job-item')
        for item in job_items:
            span_elem = item.find('span', class_='job-item-header')
            if span_elem:
                title_element = span_elem.find('a')
                if title_element:
                    title = title_element.text.strip()
                    href = title_element.get('href')
                    full_link = f"https://portal.mytum.de{href}" if href.startswith('/') else href
                    found_jobs.append({'title': title, 'link': full_link, 'source': 'TU Munich'})
    except Exception as e:
        print(f"Error scraping TU Munich: {e}")
    return found_jobs
    
def scrape_max_planck():
    """Scrapes PhD and Postdoc jobs from Max Planck Institutes."""
    url = "https://www.mpg.de/jobboard?group=phd&group=postdoc"
    print(f"Scraping Max Planck Institutes...")
    found_jobs = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        job_items = soup.find_all('div', class_='job')
        for item in job_items:
            h3_elem = item.find('h3')
            if h3_elem:
                title_element = h3_elem.find('a')
                if title_element:
                    title = title_element.text.strip()
                    href = title_element.get('href')
                    full_link = f"https://www.mpg.de{href}" if href.startswith('/') else href
                    found_jobs.append({'title': title, 'link': full_link, 'source': 'Max Planck'})
    except Exception as e:
        print(f"Error scraping Max Planck: {e}")
    return found_jobs

def scrape_mila():
    """Scrapes jobs from Mila. (FIXED)"""
    url = "https://mila.quebec/en/careers/" # Corrected URL
    print(f"Scraping Mila...")
    found_jobs = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Corrected selector
        job_items = soup.find_all('div', class_='career-card')
        for item in job_items:
            h3_elem = item.find('h3')
            if h3_elem:
                title = h3_elem.text.strip()
                href_elem = item.find('a')
                if href_elem:
                    href = href_elem.get('href')
                    found_jobs.append({'title': title, 'link': href, 'source': 'Mila'})
    except Exception as e:
        print(f"Error scraping Mila: {e}")
    return found_jobs

def scrape_vector_institute():
    """Scrapes careers from Vector Institute. (FIXED)"""
    url = "https://vectorinstitute.ai/job-board/" # Corrected URL
    print(f"Scraping Vector Institute...")
    found_jobs = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Corrected selector
        job_items = soup.find_all('div', class_='job-board-card')
        for item in job_items:
            h3_elem = item.find('h3')
            if h3_elem:
                title = h3_elem.text.strip()
                href_elem = item.find('a')
                if href_elem:
                    href = href_elem.get('href')
                    found_jobs.append({'title': title, 'link': href, 'source': 'Vector Institute'})
    except Exception as e:
        print(f"Error scraping Vector Institute: {e}")
    return found_jobs

def scrape_uc_berkeley():
    """Scrapes UC Berkeley. (FIXED - Now a simple scraper)"""
    url = "https://bcal.berkeley.edu/jobs" # Corrected URL
    print(f"Scraping UC Berkeley...")
    found_jobs = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Corrected selector
        job_items = soup.find_all('div', class_='views-row')
        for item in job_items:
            h3_elem = item.find('h3', class_='job-title')
            if h3_elem:
                title_element = h3_elem.find('a')
                if title_element:
                    title = title_element.text.strip()
                    href = title_element.get('href')
                    full_link = f"https://bcal.berkeley.edu{href}" if href.startswith('/') else href
                    found_jobs.append({'title': title, 'link': full_link, 'source': 'UC Berkeley'})
    except Exception as e:
        print(f"Error scraping UC Berkeley: {e}")
    return found_jobs

# --- STATE MANAGEMENT ---
def load_seen_jobs():
    try:
        with open(STATE_FILE, 'r') as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_seen_jobs(seen_jobs):
    with open(STATE_FILE, 'w') as f:
        json.dump(list(seen_jobs), f, indent=2)

# --- MAIN SCRIPT LOGIC ---
def main():
    seen_jobs = load_seen_jobs()
    all_current_jobs = []

    print("=" * 60)
    print("--- STARTING JOB SCRAPING ---")
    print("=" * 60)
    
    # Run all scrapers (UofT removed, Berkeley moved)
    all_current_jobs.extend(scrape_eth_zurich())
    all_current_jobs.extend(scrape_cambridge())
    all_current_jobs.extend(scrape_ucl())
    all_current_jobs.extend(scrape_tu_munich())
    all_current_jobs.extend(scrape_max_planck())
    all_current_jobs.extend(scrape_mila())
    all_current_jobs.extend(scrape_vector_institute())
    all_current_jobs.extend(scrape_uc_berkeley())
    
    print(f"\nFound {len(all_current_jobs)} jobs total across all sites")
    
    new_relevant_jobs = []
    newly_seen_links = []
    
    # Filter for new and relevant jobs
    print("\n--- FILTERING JOBS ---")
    for idx, job in enumerate(all_current_jobs, 1):
        if job['link'] not in seen_jobs:
            print(f"\n[{idx}/{len(all_current_jobs)}] NEW: {job['title'][:60]}... ({job['source']})")
            
            if is_job_relevant(job['title']):
                new_relevant_jobs.append(job)
                
            newly_seen_links.append(job['link'])
            
    # Prepare email output
    print("\n" + "=" * 60)
    email_body = ""
    if new_relevant_jobs:
        print(f"Found {len(new_relevant_jobs)} RELEVANT jobs!")
        email_body = "New AI-filtered job openings found:\n\n"
        for job in new_relevant_jobs:
            email_body += f"- {job['title']}\n  Source: {job['source']}\n  {job['link']}\n\n"
        print(email_body)
    else:
        print("No new relevant jobs found.")
        
    # Save output for GitHub Action
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            email_body_for_action = email_body.replace("\n", "%0A")
            print(f"new_jobs_email_body={email_body_for_action}", file=f)
    else:
        print("Not in GitHub Actions, skipping output.")
        
    # Save the new state
    if newly_seen_links:
        seen_jobs.update(newly_seen_links)
        save_seen_jobs(seen_jobs)
        print(f"Updated seen_jobs.json with {len(newly_seen_links)} new links")
    
    print("=" * 60)

if __name__ == "__main__":
    main()