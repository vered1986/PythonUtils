import matplotlib

matplotlib.use('Agg')

import gzip
import codecs
import logging
import numpy as np
import matplotlib.pyplot as plt

from docopt import docopt
from sklearn.decomposition import PCA

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def main():
    args = docopt("""Draws a 2d graph of the given list of words and word embeddings, using
        Principal component analysis (PCA). 

        Usage:
            pca.py <embeddings_file> <pdf_out_file> <vocab_file> <embeddings_dim>

        Arguments:
            embeddings_file     the input embedding file
            pdf_out_file        the output PDF file with the TSNE graph
            vocab_file          the words to draw
            embeddings_dim      the embedding dimension
        """)
    embeddings_file = args['<embeddings_file>']
    out_file = args['<pdf_out_file>']
    vocab_file = args['<vocab_file>']
    embeddings_dim = int(args['<embeddings_dim>'])

    with codecs.open(vocab_file, 'r', 'utf-8') as f_in:
        vocab = set([line.strip() for line in f_in])

    logger.info('Reading the embeddings from {}...'.format(embeddings_file))
    wv, vocabulary = load_embeddings(embeddings_file, embeddings_dim, vocab)

    logger.info('Computing PCA...')
    pca = PCA(n_components=2)
    np.set_printoptions(suppress=True)
    Y = pca.fit_transform(wv)

    logger.info('Saving the output file to {}...'.format(out_file))
    fig = matplotlib.pyplot.figure(figsize=(48, 42))
    ax = plt.axes()
    ax.scatter(Y[:, 0], Y[:, 1])
    for label, x, y in zip(vocabulary, Y[:, 0], Y[:, 1]):
        ax.annotate(label, xy=(x, y), xytext=(0, 0), textcoords='offset points', fontsize=8)

    fig.savefig(out_file + '.pdf', format='pdf', dpi=2000)

    logger.info('Done!')


def load_embeddings(embedding_file, dim, vocab=None):
    """
    Load the word embeddings of specific words.
    :param embedding_file: the embedding file in gzipped textual format
    :param dim: the embeddings dimension
    :param vocab: the words to load vectors for
    :return: the word vectors and list of words
    """
    with gzip.open(embedding_file, 'rb') as f_in:
        lines = [line.decode('utf-8').strip().split(' ', 1) for line in f_in]
        lines = [line for line in lines if len(line) == 2]

    words, vectors = zip(*[(word, vector) for (word, vector) in lines if len(vector.split()) == dim
                           and (vocab is None or word in vocab)])
    wv = np.loadtxt(vectors)
    return wv, words


if __name__ == '__main__':
    main()
