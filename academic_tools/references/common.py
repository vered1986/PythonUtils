import re
import tqdm
import urllib
import codecs
import textract


def normalize_title(title):
    """
    Lower-cases, trims, and removes any non alphanumeric character in the title
    :param title: the original paper title
    :return: the normalized title
    """
    return re.sub('\s+', ' ', re.sub('[\W_]+', ' ', title.lower()))


def get_from_pdf(filename, acl_anthology_by_title):
    """
    Reads a paper from a pdf, extracts its title and searches for it in the ACL anthology
    :param filename: the pdf file name
    :param acl_anthology_by_title: a dictionary of paper titles to bib entries
    :return: the bib entry or None if not found / error occurred
    """
    try:
        # Get the "title" - first line in the file
        text = textract.process(filename).decode('utf-8')

        # Search for it in the ACL anthology
        title = text.split('\n')[0]
        bib_entry = acl_anthology_by_title.get(normalize_title(title), None)
    except:
        return None

    if bib_entry is not None:
        return (bib_entry, title)

    else:
        return None


def process_acl_anthology_file(filename='anthology.bib', show_progress=True):
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

    with codecs.open(filename, 'r', 'utf-8') as f_in:
        lines = tqdm.tqdm(f_in) if show_progress else f_in
        for line in lines:
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


def extract_authors(bib_entry):
    """
    Get author names from a bib entry
    :param bib_entry: the bibtexparser bib entry
    :return: a readable string of author names
    """
    authors = bib_entry['author'].replace('\n', ' ')

    # Split by and, and save in the format: first (initial) last name
    authors_list = [author.strip()
                    if ',' not in author
                    else ' '.join(author.strip().split(', ')[1:] + [author.split(', ')[0]])
                    for author in authors.split(' and ')]

    return authors_list

