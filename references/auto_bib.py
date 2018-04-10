"""
This script reads links from a URL or a list of URLs from a text file,
and creates a bib file with bibtex entries for all the papers among the links.
Bib entries are retrieved from ACL anthology, Semantic Scholar,
and arXiv (using https://github.com/nathangrigg/arxiv2bib)
"""

# Command line arguments
import argparse
ap = argparse.ArgumentParser()
ap.add_argument('--in_url', help='the URL from which to scrape references')
ap.add_argument('--in_file', help='a local file containing links to papers')
ap.add_argument('--acl_anthology_file', help='A single .bib file containing most of the records in the ACL Anthology',
                default='http://aclanthology.info/anthology.bib')
ap.add_argument('--out_bib_file', help='Where to save the output (bib file)', default='references.bib')
args = ap.parse_args()

# Log
import logging
logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name
logger.setLevel(logging.DEBUG)

import os
import re
import json
import tqdm
import urllib
import codecs
import textract

from bs4 import BeautifulSoup
from arxiv2bib import arxiv2bib


def main():
    if not (args.in_url or args.in_file):
        raise ValueError('At least one of "in_url" or "in_file" should be set.')

    # Download the ACL anthology bib file
    if not os.path.exists('anthology.bib'):
        logger.info('Downloading ACL anthology bib file from {}'.format(args.acl_anthology_file))
        data = urllib.request.urlopen(args.acl_anthology_file).read().decode('utf-8')
        with codecs.open('anthology.bib', 'w', 'utf-8') as f_out:
            f_out.write(data)

    logger.info('Reading ACL anthology bib file')
    acl_anthology_by_id, acl_anthology_by_title = process_acl_anthology_file()
    logger.info('Read {} entries'.format(len(acl_anthology_by_id)))

    # Read the references
    if args.in_url:
        logger.info('Reading references from {}'.format(args.in_url))
        page = urllib.request.urlopen(args.in_url)
        soup = BeautifulSoup(page, 'html.parser')
        links = [link.get('href') for link in soup.findAll('a')]

    else:
        logger.info('Reading references from {}'.format(args.in_file))
        with codecs.open(args.in_file, 'r', 'utf-8') as f_in:
            links = [line.strip() for line in f_in]

    links = list(set(links))
    logger.info('Found {} links'.format(len(links)))
    references = set()
    for link in links:
        bib = try_get_bib(link, acl_anthology_by_id, acl_anthology_by_title)
        if bib is not None:
            references.add(bib)

    logger.info('Writing bib file to {}'.format(args.out_bib_file))
    with codecs.open(args.out_bib_file, 'w', 'utf-8') as f_out:
        for bib in references:
            f_out.write(bib + '\n\n')


def try_get_bib(url, acl_anthology_by_id, acl_anthology_by_title):
    """
    Gets a URL to a publication and tries to extract a bib entry for it
    Returns None if it fails (e.g. if it's not a publication)
    :param url: the URL to extract a publication from
    :param acl_anthology_by_id: a dictionary of publications by ID (from ACL anthology)
    :param acl_anthology_by_title: a dictionary of publications by title (from ACL anthology)
    :return: the bib entry or None if not found / error occurred
    """
    lowercased_url = url.lower()
    filename = lowercased_url.split('/')[-1]

    # Only try to open papers with extension pdf or bib or without extension
    if '.' in filename and not filename.endswith('.pdf') and not filename.endswith('.bib'):
        return None

    # If ends with bib, read it
    if filename.endswith('.bib'):
        bib_entry = urllib.request.urlopen(url).read().decode('utf-8')
        return bib_entry

    paper_id = filename.replace('.pdf', '')

    # If arXiv URL
    if 'arxiv.org' in lowercased_url:
        results = arxiv2bib([paper_id])

        if len(results) > 0:
            try:
                bib_entry = results[0].bibtex()
            except:
                pass

        if bib_entry:
            return bib_entry

    # If the URL is from the ACL anthology, take it by ID
    if 'aclanthology' in lowercased_url or 'aclweb.org' in lowercased_url:
        bib_entry = acl_anthology_by_id.get(paper_id.upper(), None)

        if bib_entry:
            return bib_entry

    # If the URL is from Semantic Scholar
    if 'semanticscholar.org' in lowercased_url and not lowercased_url.endswith('pdf'):
        bib_entry = get_bib_from_semantic_scholar(url)

        if bib_entry:
            return bib_entry

    # Else: try to read the pdf and find it in the acl anthology by the title
    if lowercased_url.endswith('pdf'):
        bib_entry = get_from_pdf(url, acl_anthology_by_title)

        if bib_entry:
            return bib_entry

    # Didn't find
    logger.warning('Could not find {}'.format(url))
    return None


def process_acl_anthology_file():
    """
    Reads the single ACL anthology bib entries file and saves it as
    a dictionary of title -> bib entry. Titles are lower-cased and trimmed (e.g.
    only a single space separates each word), and punctuation is removed
    (to normalize and facilitate the search).
    :return: a dictionary of bib entries by ID and by title
    """
    entries_by_id, entries_by_title = {}, {}
    title_pattern = re.compile('\s*title\s*=\s*"([^"]+)"')
    entry_pattern = re.compile('\s*@InProceedings{([^,]+),')
    entry = []
    id, normalized_title = None, None

    with codecs.open('anthology.bib', 'r', 'utf-8') as f_in:
        for line in tqdm.tqdm(f_in):
            line = line.strip()

            match = entry_pattern.match(line)

            # Beginning of bib entry
            if match:
                entry = [line]
                normalized_title = None
                id = match.group(1).upper()

            # End of bib entry
            elif line == '}':
                entry.append('}')
                entry_text = '\n'.join(entry)

                if normalized_title is not None:
                    entries_by_title[normalized_title] = entry_text

                if id is not None:
                    entries_by_id[id] = entry_text

                entry, normalized_title, id = [], None, None

            else:
                match = title_pattern.match(line)

                # Title
                if match:
                    normalized_title = normalize_title(match.group(1))

                entry.append(line)

    return entries_by_id, entries_by_title


def normalize_title(title):
    """
    Lower-cases, trims, and removes any non alphanumeric character in the title
    :param title: the original paper title
    :return: the normalized title
    """
    return re.sub('\s+', ' ', re.sub('[\W_]+', ' ', title.lower()))


def get_bib_from_semantic_scholar(url):
    """
    Gets a Semantic Scholar paper page and returns a bib entry
    :param url: the URL of the Semantic Scholar paper page
    :return: the bib entry or None if not found / error occurred
    """
    try:
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')

        # Get the JSON paper info
        info = soup.find('script', {'class': 'schema-data'}).string
        info = json.loads(info)

        bib_entry = '@InProceedings{{{id},\n\ttitle={{{title}}},\n\tauthor={{{authors}}},\n\tbooktitle={{{conf}}},\n\tyear={{{year}}}\n}}'.format(
            id=info['@graph'][1]['author'][0]['name'].split()[-1] + info['@graph'][1]['datePublished'] +
               info['@graph'][1]['headline'].split()[0],
            title=info['@graph'][1]['headline'],
            authors=' and '.join([author['name'] for author in info['@graph'][1]['author']]),
            conf=info['@graph'][1]['datePublished'],
            year=info['@graph'][1]['publication']
        )

    except:
        bib_entry = None

    return bib_entry


def get_from_pdf(url, acl_anthology_by_title):
    """
    Reads a paper from a pdf, extracts its title and searches for it in the ACL anthology
    :param url: the URL of the pdf file
    :param acl_anthology_by_title: a dictionary of paper titles to bib entries
    :return: the bib entry or None if not found / error occurred
    """
    try:

        # Download the file to a temporary file
        data = urllib.request.urlopen(url).read()
        with open('temp.pdf', 'wb') as f_out:
            f_out.write(data)

        # Get the "title" - first line in the file
        text = textract.process('temp.pdf').decode('utf-8')

        # Search for it in the ACL anthology
        title = text.split('\n')[0]
        bib_entry = acl_anthology_by_title.get(normalize_title(title), None)
    except:
        bib_entry = None

    return bib_entry


if __name__ == '__main__':
    main()