import re
import os
import codecs
import logging


# Command line arguments
import argparse
ap = argparse.ArgumentParser()
ap.add_argument('corpus_dir', help='The corpus directory')
ap.add_argument('target_ngram', help='The (tokenized) ngram to search for')
args = ap.parse_args()

logger = logging.getLogger(__name__)


def main():
    """
    Search for an n-gram count in Google N-grams.
    """
    return get_occurences_in_corpus(args.target_ngram, args.corpus_dir)


def get_occurences_in_corpus(target_ngram, google_ngram_dir):
    """
    Gets a tokenized ngram and return its frequency in Google Ngrams. 
    """
    target_ngram = target_ngram.lower()
    n = len(target_ngram.split())
    
    if n > 5 or n < 1:
        raise ValueError('n must be between 1 and 5')
        
    prefix = target_ngram[0] if n == 1 else target_ngram[:2]
    curr_ngram_file = f'{google_ngram_dir}/googlebooks-eng-all-{n}gram-20120701-{prefix}_aggregated'
    
    # No file for this prefix
    if not os.path.exists(curr_ngram_file):
        logger.warning(f'file {curr_ngram_file} does not exist')
        return 0
        
    # The Google ngrams file is tab separated, containing: ngram and count.
    with codecs.open(curr_ngram_file, 'r', 'utf-8') as f_in:
        for line in f_in:
            try:
                ngram, count = line.lower().strip().split('\t')
            
                # Found ngram - return count
                if ngram == target_ngram:
                    return int(count)
                # No ngram found (file is sorted)
                elif re.match('^[a-z]+$', ngram.lower()) and ngram > target_ngram:
                    return 0
            except:
                pass
                
    return 0


if __name__ == '__main__':
    main()

