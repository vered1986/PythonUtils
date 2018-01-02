import sys
import codecs
import random
import logging

import dynet as dy
import numpy as np

from docopt import docopt
from itertools import count
from collections import defaultdict

LAYERS = 2
HIDDEN_DIM = 50
VOCAB_SIZE = 0
START = '<s>'
END = '</s>'
MAX_ITERS = 100 # Max training iterations
PATIENCE = 10 # How many epochs without improving loss to wait before stopping training
DISPLAY_FREQ = 50 # How often to sample a sentence and display it, during training

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def main():
    args = docopt("""Trains an LSTM-based language model on a text corpus.
        Based on: https://github.com/clab/dynet/blob/5049e5995f169fe1798139e1ca4dc98a7c0c4317/examples/rnnlm/rnnlm.py

        Usage:
            lyrics_lm.py <corpus> <embeddings_file> <embeddings_dim> <model_name>

            Arguments:
                corpus              the input text corpus file.
                embeddings_file     the pre-trained embedding file in a textual format.
                embeddings_dim      the dimension of the pre-trained embeddings. 
                model_name          the model name, used for the model and prediction files.
        """)
    corpus = args['<corpus>']
    embeddings_file = args['<embeddings_file>']
    embeddings_dim = int(args['<embeddings_dim>'])
    model_name = args['<model_name>']

    logger.info('Loading the corpus from: {}'.format(corpus))
    training_corpus = CorpusReader(corpus)
    vocabulary = training_corpus.get_distinct_vocab()
    word2index = {w: i for i, w in enumerate(list(vocabulary))}
    vocab = Vocab(word2index)

    logger.info('Load the pre-trained word embeddings from: {}'.format(embeddings_file))
    wv = load_text_embeddings(embeddings_file, embeddings_dim, vocabulary)

    logger.info('Initializing the model')
    model = dy.ParameterCollection()
    trainer = dy.SimpleSGDTrainer(model)
    lm = RNNLanguageModel(model, LAYERS, embeddings_dim, HIDDEN_DIM, vocab.size(), builder=dy.LSTMBuilder,
                          pretrained_embeddings=wv)

    logger.info('Training...')
    train = list(training_corpus)

    words = loss = 0.0
    previous_loss = np.infty
    num_iters_since_last_improved = 0

    for iter in range(MAX_ITERS):
        random.shuffle(train)
        for i, sent in enumerate(train):

            # Display the current status
            if i % DISPLAY_FREQ == 0:
                trainer.status()
                if words > 0:
                    logger.debug('{}, {}'.format(i, loss / words))

                sample = lm.sample(first=vocab.w2i[START], stop=vocab.w2i[END], nwords=10)
                print(' '.join([vocab.i2w[w] for w in sample]).strip())
                loss = 0.0
                words = 0.0

            words += len(sent)
            isent = [vocab.w2i[w] for w in sent]
            errs = lm.build_lm_graph(isent)

            # Early stopping if the loss stopped improving PATIENCE iterations ago
            loss += errs.scalar_value()
            errs.backward()
            trainer.update()

            if previous_loss > loss:
                num_iters_since_last_improved += 1
            else:
                num_iters_since_last_improved = 0

            previous_loss = loss

            if num_iters_since_last_improved == PATIENCE:
                logger.info('Lost patience, stopping training')
                break

        print('Iteration: {}, loss={}'.format(iter, loss))
        trainer.status()

    logger.info('Done training.')

    model_file = model_name + '.model'
    logger.info('Saving the model to: {}'.format(model_file))
    lm.save_to_disk(model_file)

    logger.info('Loading the saved model from: {}'.format(model_file))
    lm.load_from_disk(model_file)

    logger.info('Sampling a text (in the form of a song):')
    with codecs.open(model_name + '.sample', 'w', 'utf-8') as f_out:
        start_index, end_index = vocab.w2i[START], vocab.w2i[END]
        for i in range(25):
            sample = lm.sample(first=vocab.w2i[START], stop=vocab.w2i[END], nwords=10)
            sentence = ' '.join([vocab.i2w[w] for w in sample if w != start_index and w != end_index]).strip()
            f_out.write(sentence + '\n')
            print(sentence)

            # Line break every five sentences (to simulate songs)
            if i % 5 == 0 and i > 0:
                f_out.write('\n')
                print('\n')

    logger.info('Done!')


class Vocab:
    """
    A class for storing a vocabulary
    """
    def __init__(self, w2i):
        self.w2i = w2i
        self.i2w = {i: w for w, i in w2i.items()}

    def size(self):
        """
        Returns the number of distinct words in the vocabulary
        :return: the number of distinct words in the vocabulary
        """
        return len(self.w2i.keys())


class CorpusReader:
    """
    A class for reading and processing a text corpus
    """
    def __init__(self, fname):
        self.fname = fname

    def get_distinct_vocab(self):
        """
        Returns all the distinct words in the corpus
        :return: all the distinct words in the corpus
        """
        return list(set([w for sent in self.__iter__() for w in sent]))

    def __iter__(self):
        """
        Iterate over sentences from the corpus
        :return: the next sentence
        """
        for line in file(self.fname):
            line = line.strip().lower().split()

            # Only return non-empty lines. Append start and end symbols.
            if len(line) > 0:
                yield [START] + line + [END]


class RNNLanguageModel:
    """
    An RNN Language Model
    """
    def __init__(self, model, layers, input_dim, hidden_dim, vocab_size, builder=dy.SimpleRNNBuilder,
                 pretrained_embeddings=None):
        """
        Initializes an RNN language model.
        :param model: Dynet ParameterCollection object
        :param layers: the number of RNN layers
        :param input_dim: the input dimension (= word embedding dimension)
        :param hidden_dim: the hidden dimension (of the RNN)
        :param vocab_size: the size of the vocabulary
        :param builder: the RNN builder
        :param pretrained_embeddings: optional - pre-trained embedding vectors to initialize the lookup table
        """
        self.model = model
        self.builder = builder(layers, input_dim, hidden_dim, model)

        if pretrained_embeddings is not None:
            self.lookup = model.lookup_parameters_from_numpy(pretrained_embeddings)
        else:
            self.lookup = model.add_lookup_parameters((vocab_size, input_dim))

        self.R = model.add_parameters((vocab_size, hidden_dim))
        self.bias = model.add_parameters((vocab_size))

    def save_to_disk(self, filename):
        """
        Saves the language model to the disk
        """
        self.model.save(filename)

    def load_from_disk(self, filename):
        """
        Loads the language model from the disk
        """
        self.model.populate(filename)

    def build_lm_graph(self, sent):
        dy.renew_cg()
        init_state = self.builder.initial_state()

        R = dy.parameter(self.R)
        bias = dy.parameter(self.bias)
        errs = []  # will hold expressions
        state = init_state

        for (cw, nw) in zip(sent, sent[1:]):
            # assume word is already a word-id
            x_t = dy.lookup(self.lookup, int(cw))
            state = state.add_input(x_t)
            y_t = state.output()
            r_t = bias + (R * y_t)
            err = dy.pickneglogsoftmax(r_t, int(nw))
            errs.append(err)

        nerr = dy.esum(errs) if len(errs) > 0 else dy.scalarInput(0)
        return nerr

    def predict_next_word(self, sentence):
        dy.renew_cg()
        init_state = self.builder.initial_state()
        R = dy.parameter(self.R)
        bias = dy.parameter(self.bias)
        state = init_state
        for cw in sentence:
            # assume word is already a word-id
            x_t = dy.lookup(self.lookup, int(cw))
            state = state.add_input(x_t)
        y_t = state.output()
        r_t = bias + (R * y_t)
        prob = dy.softmax(r_t)
        return prob

    def sample(self, first=1, nwords=0, stop=-1):
        res = [first]
        dy.renew_cg()
        state = self.builder.initial_state()

        R = dy.parameter(self.R)
        bias = dy.parameter(self.bias)
        cw = first
        while True:
            x_t = dy.lookup(self.lookup, cw)
            state = state.add_input(x_t)
            y_t = state.output()
            r_t = bias + (R * y_t)
            ydist = dy.softmax(r_t)
            dist = ydist.vec_value()
            rnd = random.random()
            for i, p in enumerate(dist):
                rnd -= p
                if rnd <= 0: break
            res.append(i)
            cw = i
            if cw == stop: break
            if nwords and len(res) > nwords: break
        return res


def load_text_embeddings(embeddings_file, dim, vocabulary):
    """
    Load textual word embeddings (e.g. pretrained GloVe)
    :param embeddings_file: the embedding file in textual format
    :param dim: the embeddings dimension
    :param vocabulary: the specific words to load
    :return: the word vectors
    """
    with codecs.open(embeddings_file, 'r', 'utf-8') as f_in:
        lines = [line.strip().split(' ', 1) for line in f_in]
        lines = [line for line in lines if len(line) == 2]

    vectors = { word : np.fromstring(vector, sep=' ') for (word, vector) in lines if len(vector.split()) == dim }

    # Add a random vector for each OOV word
    unknown_words = set(vocabulary).difference(set(vectors.keys()))
    vectors.update({ word : np.random.random_sample((1, dim)) for word in unknown_words})

    wv = np.vstack([vectors[word] for word in vocabulary])
    return wv


if __name__ == '__main__':
    main()