#!/usr/bin/env bash
corpus_dir=$1

# Clone the WikiExtractor repository
git clone https://github.com/attardi/wikiextractor.git;

echo "Downloading the Wikipedia dump from January 2018";
wget -O $corpus_dir/wiki_dump.bz2 https://dumps.wikimedia.org/enwiki/20180101/enwiki-20180101-pages-meta-current.xml.bz2;

# Extract text from the Wiki dump
echo "Extracting text";
mkdir -p $corpus_dir/text;
python wikiextractor/WikiExtractor.py --processes 20 -o $corpus_dir/text/ $corpus_dir/wiki_dump.bz2;
cat $corpus_dir/text/*/* > $corpus_dir/wiki_text;

# Tokenize - split to 20 processes
echo "Splitting corpus";
split -nl/20 -d $corpus_dir/wiki_text $corpus_dir/wiki_text"_";
mkdir -p $corpus_dir/tokenized;

echo "Tokenize corpus";
for x in {00..19}
do
( python tokenize_corpus.py $corpus_dir/wiki_text"_a"$x $corpus_dir/tokenized/ ) &
done
wait

echo "Merging files";
cat $corpus_dir/tokenized/* > $corpus_dir/wiki_tokenized;

echo "Removing temp files";
rm $corpus_dir/text/*/* $corpus_dir/tokenized/* $corpus_dir/wiki_text"_a"*;

echo "Finished preprocessing corpus, the processed corpus is available at: $corpus_dir/wiki_tokenized";
