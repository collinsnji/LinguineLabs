import os

import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from tqdm import tqdm
tqdm.pandas()

THERAPY_WORD_LIST = ['trauma', 'traumatic', 'traumatized', 'traumatizing', 'ptsd', 'depression', 'great depression', 'depressed', 'suicidal', 'depressing', 'anxiety', 'ocd', 'obsessive compulsive disorder', 'schizophrenia', 'bipolar', 'bipolar disorder', 'psychosis', 'psychotic', 'shell shock']

def process_file(file_name):
    THERAPY_WORDS = {word: 0 for word in THERAPY_WORD_LIST}
    vectorizer = CountVectorizer(
        stop_words='english',
        strip_accents='ascii',
        lowercase=True,
        ngram_range=(1, 3),
    )
    with open(file_name) as f:
        corpus = f.readlines()
        corpus = [x.strip() for x in corpus]
    try:
        vectorizer.fit_transform(THERAPY_WORDS.keys())
        term_freq_vector = vectorizer.transform(corpus)

        word_list = vectorizer.get_feature_names_out()
        count_list = term_freq_vector.toarray().sum(axis=0)
        vocab = dict(zip(word_list, count_list))
    except ValueError:
        vocab = {}
    for k, v in THERAPY_WORDS.items():
        THERAPY_WORDS[k] = vocab[k] if k in vocab else v
    return THERAPY_WORDS

def count_occurrences():
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__).split('data_processing')[0])
    raw_dataset_path = f"{ROOT_DIR}/data/raw/books1/epubtxt" 
    df = pd.read_csv(f"{ROOT_DIR}/data/metadata/year_published.csv")
    # file_names = df["filename"].values[:10]
    # results = [process_file(f'{raw_dataset_path}/{file}') for file in file_names]
    process_line = lambda file_name: pd.Series(process_file(f'{raw_dataset_path}/{file_name}'))
    df[[*THERAPY_WORD_LIST]] = df["filename"].progress_apply(process_line)
    df.to_csv(f"{ROOT_DIR}/data/processed/book_corpus.csv", index=False)

if __name__ == "__main__":
    count_occurrences()
