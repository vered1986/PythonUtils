# Corpora

This directory contains scripts for downloading and handling corpora.

## Google Ngrams

The Google Ngrams corpus [(Michel et al., 2011)](http://science.sciencemag.org/content/331/6014/176) consists of n-grams 
from `n = 1 ... 5` and the number of occurrences in books, for n-grams that appeared over 40 times in the whole corpus. 

The directory `google_ngrams` contains a bash script for downloading the corpus. Since the corpus reports the number of occurrences
of an n-gram *in a given year*, we also aggregate the counts. Downloading the corpus is done by calling:

```
download_google_ngrams.sh
```

Notice that it takes several hours (8-10). 

The directory also includes a script for searching an n-gram occurrence in the corpus:

```
usage: get_frequency.py [-h] corpus_dir target_ngram

positional arguments:
  corpus_dir    The corpus directory
  target_ngram  The (tokenized) ngram to search for

optional arguments:
  -h, --help    show this help message and exit
```


## Wikipedia

The `wikipedia` directory contains a bash script for downloading a dump of wikipedia (specifically, as an example, the dump from January 2018):

```
download_corpus.sh out_corpus_dir
```

You can also tokenize the corpus using Spacy by calling:

```
usage: tokenize_corpus.py [-h] corpus

positional arguments:
  corpus      The corpus file

optional arguments:
  -h, --help  show this help message and exit
```

This will create a file with the same name as the corpus file and a prefix `_tokenized`. 
