from __future__ import print_function

import sys
import codecs
import numpy as np

from docopt import docopt

def main():
    args = docopt("""Convert an embedding file in a textual format (such as the pretrained GloVe embeddings) to a binary format.
    
    The input is a text file with a '.txt' extension, in which each line is space-separated, the first word being the target word
    and the rest being the textual representation of its vector.

    The output is two files, saved in the same directory as the input file:
    1) a binary file containing the word matrix (to load using np.load(file)), saved with the extension 'npy' 
    2) a text file containing the vocabulary (one word per line, in order), saved with the extension 'vocab'
    
    Usage:
        convert_text_embeddings_to_binary.py <embedding_file> 

        <embedding_file> = the input embedding file
    """)

    embedding_file = args['<embedding_file>']
    print('Loading embeddings file from {}'.format(embedding_file))
    wv, words = load_embeddings(embedding_file)

    out_emb_file, out_vocab_file = embedding_file.replace('.txt', ''), embedding_file.replace('.txt', '.vocab')
    print('Saving binary file to {}'.format(out_emb_file))
    np.save(out_emb_file, wv)

    print('Saving vocabulary file to {}'.format(out_vocab_file))
    with codecs.open(out_vocab_file, 'w', 'utf-8') as f_out:
        for word in words:
            f_out.write(word + '\n')


def load_embeddings(file_name):
    """
    Load the pre-trained embeddings from a file
    :param file_name: the embeddings file
    :return: the vocabulary and the word vectors
    """
    with codecs.open(file_name, 'r', 'utf-8') as f_in:
        words, vectors = zip(*[line.strip().split(' ', 1) for line in f_in])
    wv = np.loadtxt(vectors)

    return wv, words


if __name__ == '__main__':
    main()
