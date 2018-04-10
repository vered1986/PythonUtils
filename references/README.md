This directory contains a script for automating the creation of bib files for NLP publications.

# Requirements

* Python 3
* tqdm
* [textract](http://textract.readthedocs.io/en/latest/installation.html)

# Usage:

Use `auto_bib.py` to create the bib:

```
usage: auto_bib.py [-h] [--in_url IN_URL] [--in_file IN_FILE]
                   [--acl_anthology_file ACL_ANTHOLOGY_FILE]
                   [--out_bib_file OUT_BIB_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --in_url IN_URL       the URL from which to scrape references
  --in_file IN_FILE     a local file containing links to papers
  --acl_anthology_file ACL_ANTHOLOGY_FILE
                        A single .bib file containing most of the records in
                        the ACL Anthology
  --out_bib_file OUT_BIB_FILE
                        Where to save the output (bib file)
```

You must provide either a URL from which to scrape the publication links (e.g. `auto_bib.py --in_url https://nlp.stanford.edu/projects/snli/`)
or a text file in which each line is a URL (e.g. `auto_bib.py --in_file reading_list.txt`).

The script reads all the links and assumes that any link to PDF, BIB or without extension is a publication.
It scrapes information from [ACL anthology](http://aclweb.org/anthology/), [Semantic Scholar](https://www.semanticscholar.org),
and [arXiv](https://arxiv.org), using [https://github.com/nathangrigg/arxiv2bib](arxiv2bib).

The output is a bib file saved under `out_bib_file` (default `references.bib`).
