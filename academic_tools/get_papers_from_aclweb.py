"""
This script finds papers in the ACL anthology based on key words
"""
import os
import re
import json
import tqdm
import urllib
import logging
import argparse

import pandas as pd
from bs4 import BeautifulSoup
from xml.sax.saxutils import unescape

logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--keywords', help='list of key words separated by semicolon')
    ap.add_argument('--year', help='publication year')
    ap.add_argument('--out_file', help='CSV file to save the results')
    args = ap.parse_args()
    
    keywords = args.keywords.lower().split(";")

    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent' : user_agent}

    # Find the relevant events
    try:
        req = urllib.request.Request("https://aclanthology.org/events/", None, headers)
        response = urllib.request.urlopen(req)
        html = response.read()
        soup = BeautifulSoup(html, features="lxml")
        events = [li.find('a') for li in soup.findAll('li')]
        events = {acr(event.text): event["href"] for event in events if args.year in event.text}
    except:
        events = {}

    # Find the relevant papers
    relevant_papers = []
    for event_name, event_url in events.items():
        if event_name is None: continue
        print(event_name)
        req = urllib.request.Request("https://aclanthology.org/" + event_url, None, headers)
        response = urllib.request.urlopen(req)
        html = response.read()
        soup = BeautifulSoup(html, features="lxml")
        papers = soup.findAll('span', {"class": "d-block"})
        links = list(soup.findAll('a'))
        
        for i, link in tqdm.tqdm(enumerate(links)):
            # Paper title
            if f"/{args.year}." in link["href"]:
                title = link.text
                url = "https://aclanthology.org/" + link["href"]
                j = i + 2
                authors = []
                while "people" in links[j]["href"]:
                    authors.append(links[j].text)
                    j += 1
                    
                authors = ", ".join(authors)
            
                if any([keyword in title.lower() for keyword in keywords]):
                    relevant_papers.append((title, authors, " ".join((event_name, args.year)), url))
    
    relevant_papers = list(set(relevant_papers))
    df = pd.DataFrame(relevant_papers, columns =['Title', 'Authors', 'Venue', 'URL'])
    df.to_csv(args.out_file)

    

def acr(event):
    event = event.replace("(", "").replace(")", "")
    if "Annual Meeting of the Association for Computational Linguistics" in event:
        return "ACL"
    if "North American Chapter of the Association for Computational Linguistics" in event:
        return "NAACL"
    if "European Chapter of the Association for Computational Linguistics" in event:
        return "EACL"
    if "Asian Chapter of the Association for Computational Linguistics" in event:
        return "AACL"
    if "International Conference on Computational Linguistics" in event:
        return "COLING"
    if "Conference on Computational Natural Language Learning" in event:
        return "CoNLL"
    if "Joint Conference on Lexical and Computational Semantics" in event:
        return "*SEM"
    if "Findings of the Association for Computational Linguistics" in event:
        return "Findings of ACL" 
    else:
        return None
    

if __name__ == '__main__':
    main()