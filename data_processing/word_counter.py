import os
import subprocess

import pandas as pd
from tqdm import tqdm

tqdm.pandas()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__).split('data_processing')[0])
data_path = f"{ROOT_DIR}/data/raw/books1/epubtxt/"

def count_words(file_name):
    try:
        count = int(subprocess.check_output(['wc', '-w', data_path + file_name]).split()[0])
    except FileNotFoundError:
        count = None
    return count

def process_book_corpus():
    df_path = f"{ROOT_DIR}/data/processed/book_corpus.csv"
    df = pd.read_csv(df_path)
    df['word_count'] = df['filename'].progress_apply(count_words)
    df.to_csv(f"{ROOT_DIR}/data/processed/book_corpus_wc.csv")

if __name__ == '__main__':
    process_book_corpus()