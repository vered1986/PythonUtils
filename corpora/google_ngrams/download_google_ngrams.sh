#!/bin/bash

declare -a letters=(a b c d e f g h i j k l m n o p q r s t u v w x y z)
declare -a ns=(2 3 4 5)

# 1-grams
for letter in "${letters[@]}"
do
    wget -nc http://storage.googleapis.com/books/ngrams/books/googlebooks-eng-all-1gram-20120701-${letter}.gz &
done
wait

# n-grams for n > 1
for n in "${ns[@]}"
do
    for first in "${letters[@]}"
    do
        for second in "${letters[@]}"
        do
            wget -nc http://storage.googleapis.com/books/ngrams/books/googlebooks-eng-all-${n}gram-20120701-${first}${second}.gz &
        done
    done
    wait
done

# Unzip
for letter in "${letters[@]}"
do
    echo "gunzip googlebooks-eng-all-1gram-20120701-${letter}.gz &"
    gunzip -f googlebooks-eng-all-1gram-20120701-${letter}.gz &
done
        
for n in "${ns[@]}"
do
    for first in "${letters[@]}"
    do
        for second in "${letters[@]}"
        do
            echo "gunzip googlebooks-eng-all-${n}gram-20120701-${first}${second}.gz &"
            gunzip -f googlebooks-eng-all-${n}gram-20120701-${first}${second}.gz &
        done
        wait
    done
done


# The Google ngrams file is tab separated, containing: ngram, year, match_count, and volume_count.
# We will aggregate all the occurences   

# Unigrams
for letter in "${letters[@]}"
do
    (
    echo "aggregating googlebooks-eng-all-1gram-20120701-${letter}"
    awk -F $'\t' 'BEGIN { OFS = FS } { a[tolower($1)]+=$3; } END {for (ngram in a) print ngram, a[ngram]}' googlebooks-eng-all-1gram-20120701-${letter} | grep -P "^[[:alpha:]]+\t[0-9]+$" | sort > googlebooks-eng-all-1gram-20120701-${letter}_filtered;
    ) &
done
wait

# Bigrams
for first in "${letters[@]}"
do
    for second in "${letters[@]}"
    do
    (
    echo "aggregating googlebooks-eng-all-2gram-20120701-${first}${second}"
    awk -F $'\t' 'BEGIN { OFS = FS } { a[tolower($1)]+=$3; } END {for (ngram in a) print ngram, a[ngram]}' googlebooks-eng-all-2gram-20120701-${first}${second} | grep -P "^[[:alpha:]]+ [[:alpha:]]+\t[0-9]+$" | sort > googlebooks-eng-all-2gram-20120701-${first}${second}_filtered;
    ) &
    done
    wait
done

# Trigrams
for first in "${letters[@]}"
do
    for second in "${letters[@]}"
    do
    (
    echo "aggregating googlebooks-eng-all-3gram-20120701-${first}${second}"
    awk -F $'\t' 'BEGIN { OFS = FS } { a[tolower($1)]+=$3; } END {for (ngram in a) print ngram, a[ngram]}' googlebooks-eng-all-3gram-20120701-${first}${second} | grep -P "^[[:alpha:]]+ [[:alpha:]]+ [[:alpha:]]+\t[0-9]+$" | sort > googlebooks-eng-all-3gram-20120701-${first}${second}_filtered;
    ) &
    done
    wait
done

# 4-grams
for first in "${letters[@]}"
do
    for second in "${letters[@]}"
    do
    (
    echo "aggregating googlebooks-eng-all-4gram-20120701-${first}${second}"
    awk -F $'\t' 'BEGIN { OFS = FS } { a[tolower($1)]+=$3; } END {for (ngram in a) print ngram, a[ngram]}' googlebooks-eng-all-4gram-20120701-${first}${second} | grep -P "^[[:alpha:]]+ [[:alpha:]]+ [[:alpha:]]+ [[:alpha:]]+\t[0-9]+$" | sort > googlebooks-eng-all-4gram-20120701-${first}${second}_filtered;
    ) &
    done
    wait
done

# 5-grams
for first in "${letters[@]}"
do
    for second in "${letters[@]}"
    do
    (
    echo "aggregating googlebooks-eng-all-5gram-20120701-${first}${second}"
    awk -F $'\t' 'BEGIN { OFS = FS } { a[tolower($1)]+=$3; } END {for (ngram in a) print ngram, a[ngram]}' googlebooks-eng-all-5gram-20120701-${first}${second} | grep -P "^[[:alpha:]]+ [[:alpha:]]+ [[:alpha:]]+ [[:alpha:]]+ [[:alpha:]]+\t[0-9]+$" | sort > googlebooks-eng-all-5gram-20120701-${first}${second}_filtered;
    ) &
    done
    wait
done
