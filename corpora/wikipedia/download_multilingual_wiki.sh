#!/bin/bash

declare -a langs=("en" "fr" "de" "es" "ja" "ru" "it" "zh" "pt" "ar" "fa" "pl" "nl" "id" "uk" "he" "sv" "cs" "ko" "vi" "ca" "no" "fi" "hu" "tr" "el" "th" "hi" "bn")

for lang in "${langs[@]}"
do
	url="https://dumps.wikimedia.org/${lang}wiki/20210920";
	filename="${lang}wiki-20210920-pages-articles-multistream.xml.bz2";
	curl ${url}/${filename} -o ${filename};
	python -m wikiextractor.WikiExtractor ${filename};
	cat text/*/* > ${lang}_wiki;
	tar -zcvf ${lang}_wiki.tar.gz ${lang}_wiki;
	rm -r text;
	rm ${filename};
	rm ${lang}_wiki;
done
