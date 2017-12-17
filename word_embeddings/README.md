This directory contains scripts for loading, storing, converting and visualizing word embeddings.

# Format Conversion

## Convert textual format to binary format

The script `convert_text_embeddings_to_binary.py' takes an embedding file in a textual format (such as the pretrained GloVe embeddings), 
and converts it to numpy binary format, for faster loading.
    
The input is a text file with a `.txt` extension, in which each line is space-separated, the first word being the target word
and the rest being the textual representation of its vector.

The output is two files, saved in the same directory as the input file:
1. a binary file containing the word matrix (to load using np.load(file)), saved with the extension `.npy` 
2. a text file containing the vocabulary (one word per line, in order), saved with the extension `.vocab`
    
### Usage:
```
convert_text_embeddings_to_binary.py <embedding_file> 

Arguments:
    embedding_file  the input embedding file
```

The output would be saved under the same directory as `embedding_file', with the extensions `.npy' and `.vocab'. 


## Convert word2vec format to textual format

The script `convert_binary_embeddings_to_text.py' converts an embedding file in a word2vec binary format to a textual format, for readability.
    
The input is a binary embedding file, such as the pretrained word2vec embeddings, with a `.bin` extension.
    
The output is a text file with a `.txt` extension, in which each line is space-separated, the first word being the target word and the rest being the textual representation of its vector.
It is possible to also create a gzipped version (a compressed file with a `.txt.gz` extension) by providing the `create_gzip` optional argument.

### Usage:

```
convert_binary_embeddings_to_text.py [--create_gzip] <embedding_file>
        
Arguments:
        embedding_file  the input embedding file
        
Options:
        --create_gzip   whether to gzip the textual embeddings
```


## Convert textual format to word2vec format

Use the following script from [gensim](https://radimrehurek.com/gensim/):

```
python -m gensim.scripts.glove2word2vec --input embeddings.txt --output embeddings.bin
```


# Visualization

## TSNE

[TSNE](https://lvdmaaten.github.io/tsne/) is a dimensionality reduction algorithm suitable for the visualization of word embeddings. 

The script `tsne.py` loads word embeddings and a specific vocabulary and draws a TSNE graph of the words in the vocabulary. The output is a pdf file.

### Usage:

```
tsne.py <embeddings_file> <pdf_out_file> <vocab_file> <embeddings_dim>

Arguments:
	embeddings_file     the input embedding file
	pdf_out_file        the output PDF file with the TSNE graph
	vocab_file          the words to draw
	embeddings_dim      the embedding dimension
```
