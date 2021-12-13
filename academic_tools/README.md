## Find papers by keywords in ACL Anthology:

See this [gist](https://gist.github.com/vered1986/8b07f3338598984bacac57fd6f3c519a#file-find_papers_by_keywords-py).

## Zotero to Google Doc

Import a Zotero collection to Google Doc as a report which includes the title, authors, year, venue and notes. 

### Usage:

1. Export a CSV from Zotero (`Export Collection -> CSV`, select `include notes`). 
2. Save it in your Google Drive as "zotero_input". Sort it as you wish. 
3. Create a new Google Doc file and open `Tools -> Script Editor`.  
4. Copy the content of [`zotero_csv_to_google_doc.gs`](zotero_to_google_doc/zotero_csv_to_google_doc.gs) and call `main()`. 


## References

This directory contains a script for automating the creation of bib files and reading lists for NLP publications.

### Requirements

* Python 3
* tqdm
* [textract](http://textract.readthedocs.io/en/latest/installation.html)
* [bibtexparser](https://bibtexparser.readthedocs.io/en/master/)

### Bib File Creation

The script reads all the links and assumes that any link to PDF, BIB or without extension is a publication.
It scrapes information from [ACL anthology](http://aclweb.org/anthology/), [TACL](https://transacl.org/ojs/index.php/tacl/),
[Semantic Scholar](https://www.semanticscholar.org),
and [arXiv](https://arxiv.org), using [https://github.com/nathangrigg/arxiv2bib](arxiv2bib).

#### Usage:

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

The output is a bib file saved under `out_bib_file` (default `references.bib`).

### Managing a Reading List

This script gets a paper pdf and adds it to the reading list, which is saved as a JSON file.
For now, the pdf file needs to be local, so you must download the paper before you add it to the reading list.
The best way to use this script is by adding a context menu option to your file manager 
which allows you to right-click a file and add it to the reading list.
See Linux (Nautilus) instruction below.  

I plan to add a script to view, mark as read, and delete papers from the list (TBD).

#### Usage:

Use `add_to_reading_list.py` to add a PDF file to your reading list:

```
usage: add_to_reading_list.py [-h] [--references_dir REFERENCES_DIR] in_file

positional arguments:
  in_file               a local pdf file of the paper

optional arguments:
  -h, --help            show this help message and exit
  --references_dir REFERENCES_DIR
                        the location of the script (different from the
                        location in which nautilus called the script)
```

`in_file` is the path of the pdf paper, and `references_dir` needs to be set to the execution directory.
The script will ask you to select the reading list file, and attempt to add the file to the reading list.

#### Adding a context menu option:

In Nautilus, follow the instructions in this [link](https://www.howtogeek.com/116807/how-to-easily-add-custom-right-click-options-to-ubuntus-file-manager/), with the following details:

- Action context label: "Add to my Reading List"
- Tooltip: "Add a pdf paper to the reading list"
- Command path: `python [link_to_repo]/add_to_reading_list.py`
- Parameters: `%f`

You should be able to right-click a PDF file, and select `Nautilus Actions actions > Add to my Reading List`. 

#### Limitations:

- This feature is not very-well tested so it is probably buggy as hell. 
- Currently it can only work for papers which are in the ACL anthology. 
- TBD: the local ACL anthology file needs to download an update from time to time.



