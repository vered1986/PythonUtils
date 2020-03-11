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

from bs4 import BeautifulSoup
from arxiv2bib import arxiv2bib
from urllib.parse import urljoin

from common import get_from_pdf, normalize_title, process_acl_anthology_file


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
        links = filter(None, [link.get('href') for link in soup.findAll('a')])

        # Resolve relative URLs
        links = [link if 'www' in link or 'http' in link else urljoin(args.in_url, link) for link in links]

    else:
        logger.info('Reading references from {}'.format(args.in_file))
        with codecs.open(args.in_file, 'r', 'utf-8') as f_in:
            links = [line.strip() for line in f_in]

    links = list(set(links))
    logger.info('Found {} links'.format(len(links)))

    # Save references as a dictionary with the normalized title as a key,
    # to prevent duplicate entries (i.e. especially from bib and paper links)
    references = {}
    for link in links:
        result = try_get_bib(link, acl_anthology_by_id, acl_anthology_by_title)
        if result is not None:
            bib, title = result
            references[title] = bib

    logger.info('Writing bib file to {}'.format(args.out_bib_file))
    with codecs.open(args.out_bib_file, 'w', 'utf-8') as f_out:
        for bib in references.values():
            f_out.write(bib + '\n\n')


def try_get_bib(url, acl_anthology_by_id, acl_anthology_by_title):
    """
    Gets a URL to a publication and tries to extract a bib entry for it
    Returns None if it fails (e.g. if it's not a publication)
    :param url: the URL to extract a publication from
    :param acl_anthology_by_id: a dictionary of publications by ID (from ACL anthology)
    :param acl_anthology_by_title: a dictionary of publications by title (from ACL anthology)
    :return: a tuple of (bib entry, tuple) or None if not found / error occurred
    """
    lowercased_url = url.lower()
    filename = lowercased_url.split('/')[-1]

    # Only try to open papers with extension pdf or bib or without extension
    if '.' in filename and not filename.endswith('.pdf') and not filename.endswith('.bib'):
        return None

    # If ends with bib, read it
    if filename.endswith('.bib'):
        bib_entry = urllib.request.urlopen(url).read().decode('utf-8')
        title = get_title_from_bib_entry(bib_entry)
        return (bib_entry, title)

    paper_id = filename.replace('.pdf', '')

    # Paper from TACL
    if 'transacl.org' in lowercased_url or 'tacl' in lowercased_url:
        result = get_bib_from_tacl(paper_id)

        if result is not None:
            try:
                bib_entry, title = result
                title = normalize_title(title)
                return (bib_entry, title)
            except:
                pass


    # If arXiv URL, get paper details from arXiv
    if 'arxiv.org' in lowercased_url:
        results = arxiv2bib([paper_id])

        if len(results) > 0:
            try:
                result = results[0]
                title = normalize_title(result.title)

                # First, try searching for the title in the ACL anthology. If the paper
                # was published in a *CL conference, it should be cited from there and not from arXiv
                bib_entry = acl_anthology_by_title.get(title, None)

                # Not found in ACL - take from arXiv
                if bib_entry is None:
                    bib_entry = result.bibtex()
            except:
                pass

        if bib_entry:
            return (bib_entry, title)

    # If the URL is from the ACL anthology, take it by ID
    if 'aclanthology' in lowercased_url or 'aclweb.org' in lowercased_url:
        bib_entry = acl_anthology_by_id.get(paper_id.upper(), None)

        if bib_entry:
            title = get_title_from_bib_entry(bib_entry)
            return (bib_entry, title)

    # If the URL is from Semantic Scholar
    if 'semanticscholar.org' in lowercased_url and not lowercased_url.endswith('pdf'):
        result = get_bib_from_semantic_scholar(url)

        if result is not None:
            try:
                semantic_scholar_bib_entry, title = result
                title = normalize_title(title)

                # First, try searching for the title in the ACL anthology. If the paper
                # was published in a *CL conference, it should be cited from there and not from Semantic Scholar
                bib_entry = acl_anthology_by_title.get(title, None)

                # Not found in ACL - take from Semantic Scholar
                if bib_entry is None:
                    bib_entry = semantic_scholar_bib_entry

                return (bib_entry, title)
            except:
                pass

    # Else: try to read the pdf and find it in the acl anthology by the title
    if lowercased_url.endswith('pdf'):

        # Download the file to a temporary file
        data = urllib.request.urlopen(url).read()
        with open('temp.pdf', 'wb') as f_out:
            f_out.write(data)

        result = get_from_pdf('temp.pdf', acl_anthology_by_title)

        if result is not None:
            bib_entry, title = result
            title = normalize_title(title)
            return (bib_entry, title)

    # Didn't find
    logger.warning('Could not find {}'.format(url))
    return None


def get_bib_from_tacl(paper_id):
    """
    Gets a TACL paper page and returns a bib entry
    :param paper_id: TACL paper ID
    :return: a tuple of (bib entry, title) or None if not found / error occurred
    """
    url = 'https://transacl.org/ojs/index.php/tacl/rt/captureCite/{id}/0/BibtexCitationPlugin'.format(id=paper_id)

    try:
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        bib_entry = soup.find('pre').string
        title = soup.find('h3').string

    except:
        return None

    return bib_entry, title


def get_bib_from_semantic_scholar(url):
    """
    Gets a Semantic Scholar paper page and returns a bib entry
    :param url: the URL of the Semantic Scholar paper page
    :return: a tuple of (bib entry, title) or None if not found / error occurred
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
            year=info['@graph'][1]['datePublished'],
            conf=info['@graph'][1]['publication']
        )

    except:
        return None

    return (bib_entry, info['@graph'][1]['headline'])


def get_title_from_bib_entry(bib_entry):
    """
    Gets a bib entry in a textual format and returns the paper title
    :param bib_entry:
    :return: the title or None if not found
    """
    title = None

    # Make one line and lowercase
    bib_entry_text = re.sub('\s+', ' ', bib_entry.lower())

    # Find the title
    match = re.search('\stitle\s*=\s*[{{"]([^"}}]+)[}}"]', bib_entry_text)

    if match:
        title = match.group(1)

    if title is not None:
        title = normalize_title(title)

    return title


if __name__ == '__main__':
    main()