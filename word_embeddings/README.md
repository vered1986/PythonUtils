This directory contains scripts for loading and storing pretrained word embeddings.

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
