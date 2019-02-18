# Command line arguments
import argparse
ap = argparse.ArgumentParser()
ap.add_argument('corpus', help='The corpus file')
args = ap.parse_args()

import spacy
import codecs
import logging

logger = logging.getLogger(__name__)


def main():
    """
    Gets a Wikipedia corpus (converted to text using WikiExtractor) and tokenizes it.
    """
    nlp = spacy.load('en', disable=['parser'])
    nlp.add_pipe(nlp.create_pipe('sentencizer'))

    with codecs.open(args.corpus, 'r', 'utf-8') as f_in:
        with codecs.open(args.corpus + '_tokenized', 'w', 'utf-8', buffering=0) as f_out:
            try:
                for paragraph in f_in:

                    # Skip empty lines
                    paragraph = paragraph.replace('<doc', '').replace('</doc', '').strip()
                    if len(paragraph) == 0:
                        continue

                    parsed_par = nlp(paragraph)

                    # Tokenize each sentence separately
                    for sent in parsed_par.sents:
                        tokens = [t.text.lower() for t in sent]
                        if len(tokens) > 3:
                            f_out.write(' '.join(tokens) + '\n')

            except Exception as err:
                logger.error(err)


if __name__ == '__main__':
    main()