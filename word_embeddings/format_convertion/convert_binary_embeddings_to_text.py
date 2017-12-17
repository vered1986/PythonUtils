import codecs
import gensim
import tarfile

from docopt import docopt


def main():
    args = docopt("""Convert an embedding file in a binary format to a textual format.
    
    The input is a binary embedding file, such as the pretrained word2vec embeddings, with a '.bin' extension.
    
    The output is a text file with a '.txt' extension, in which each line is space-separated, 
    the first word being the target word and the rest being the textual representation of its vector.
    
    If create_gzip is True, it also gzips the embeddings and saves the zipped file with a '.txt.gz' extension.
    
    Usage:
        convert_binary_embeddings_to_text.py [--create_gzip] <embedding_file>
        
    Arguments:
        embedding_file  the input embedding file
        
    Options:
        --create_gzip   whether to gzip the textual embeddings
    """)
    embedding_file = args['<embedding_file>']
    print('Loading embeddings file from {}'.format(embedding_file))
    vectors = gensim.models.KeyedVectors.load_word2vec_format(embedding_file, binary=True)

    out_text_file = embedding_file.replace('.bin', '.txt')
    print('Saving textual file to {}'.format(out_text_file))
    with codecs.open(out_text_file, 'w', 'utf-8') as f_out:
        for word in vectors.index2word:
            vector = ' '.join(map(str, list(vectors[word])))
            f_out.write(word + ' ' + vector + '\n')

    if args['--create_gzip']:
        archive_file = out_text_file + '.gz'
        print('Gzipping to {}'.format(archive_file))
        with tarfile.open(archive_file, 'w:gz') as archive:
            archive.add(out_text_file)


if __name__ == '__main__':
    main()