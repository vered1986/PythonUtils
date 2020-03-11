"""
This script gets a paper pdf and adds it to the reading list
"""

# Command line arguments
import argparse
ap = argparse.ArgumentParser()
ap.add_argument('in_file', help='a local pdf file of the paper')
ap.add_argument('--references_dir',
                help='the location of the script (different from the location in which nautilus called the script)',
                default='/home/vered/git/PythonUtils/references/')
args = ap.parse_args()

import re
import os
import sys
import json
import codecs
import easygui
import bibtexparser

# Log
import logging
logging.basicConfig(level=logging.DEBUG,
                    handlers=[logging.StreamHandler(),
                              logging.FileHandler(os.path.join(args.references_dir, 'log.txt'))])
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

from common import get_from_pdf, normalize_title, process_acl_anthology_file, extract_authors


def main():
    if not args.in_file.lower().endswith('pdf'):
        logger.error('Sorry, I can only read PDF files!')
        easygui.msgbox('Sorry, I can only read PDF files!', title='Error')
        return

    # Choose the reading list
    reading_list = easygui.fileopenbox(msg='Please Choose the Reading List')

    try:
        if reading_list is not None:

            # Download the ACL anthology bib file
            acl_anthology_file = os.path.join(args.references_dir, 'anthology.bib')
            if not os.path.exists(acl_anthology_file):
                data = urllib.request.urlopen(args.acl_anthology_file).read().decode('utf-8')
                with codecs.open(acl_anthology_file, 'w', 'utf-8') as f_out:
                    f_out.write(data)

            logger.info('Reading ACL anthology bib file')
            acl_anthology_by_id, acl_anthology_by_title = process_acl_anthology_file(filename=acl_anthology_file,
                                                                                     show_progress=False)
            logger.info('Read {} entries'.format(len(acl_anthology_by_id)))

            result = get_from_pdf(args.in_file, acl_anthology_by_title)

            if result is None:
                logger.error('Sorry, I could not get the bib info for this paper.')
                easygui.msgbox('Sorry, I could not get the bib info for this paper.', title='Error')
            else:
                bib_entry, title = result
                add_to_reading_list(reading_list, bib_entry, title)
                easygui.msgbox('Successfully added the following paper to the reading list: "{}"'.format(title),
                               title='Success')

    except:
        easygui.msgbox('Failed adding paper to the reading list. {}'.format(sys.exc_info()[0]), title='Error')
        logger.error('Failed adding paper to the reading list. {}'.format(sys.exc_info()[0]))


def add_to_reading_list(reading_list_file, bib_entry, title):
    """
    Adds a paper to the reading list
    :param reading_list_file: a json file with the reading list
    :param bib_entry: the bib entry of the paper to add to the list
    :param title: the title of the paper to add to the list
    """
    with codecs.open(reading_list_file, 'r', 'utf-8') as f_in:
        reading_list = json.load(f_in)

    parser = BibTexParser()
    parser.customization = convert_to_unicode
    bib_entry_object = bibtexparser.loads(bib_entry, parser).entries[0]
    authors = extract_authors(bib_entry_object)
    url = bib_entry_object.get('url', '')

    curr_entry = ReadingListEntry(args.in_file, title, authors, url).__dict__

    if curr_entry not in reading_list:
        reading_list.append(curr_entry)

    with codecs.open(reading_list_file, 'w', 'utf-8') as f_out:
        json.dump(reading_list, f_out, ensure_ascii=False)


class ReadingListEntry():
    """
    A paper entry in the reading list
    """
    def __init__(self, local_file, title, authors, url=None):
        self.local_file = local_file
        self.url = url
        self.title = title
        self.authors = authors
        self.read = False
        self.summary = ''

    def get_title(self):
        return self.title

    def set_title(self, title):
        self.title = title

    def get_read(self):
        return self.read

    def set_read(self, read):
        self.read = read

    def get_summary(self):
        return self.summary

    def set_summary(self, summary):
        self.summary = summary


if __name__ == '__main__':
    main()