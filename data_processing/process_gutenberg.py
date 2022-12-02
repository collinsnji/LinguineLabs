import os

import pandas as pd
from tqdm import tqdm

tqdm.pandas()

THERAPY_WORD_LIST = ['trauma', 'traumatic', 'traumatized', 'traumatizing', 'ptsd', 'depression', 'great depression', 'depressed', 'suicidal', 'depressing', 'anxiety', 'ocd', 'obsessive compulsive disorder', 'schizophrenia', 'bipolar', 'bipolar disorder', 'psychosis', 'psychotic', 'shell shock']
ROOT_DIR = os.path.dirname(os.path.abspath(__file__).split('data_processing')[0])
data_path = f"{ROOT_DIR}/data/metadata/SPGC-metadata-2018-07-18.csv"
token_path = f"{ROOT_DIR}/data/raw/project_gutenberg_data"

def read_data(data_path):
    df = pd.read_csv(data_path)
    df = df[df['authoryearofbirth'].notna() & df['authoryearofdeath'].notna()]
    df = df[df.language == "['en']"]
    df['year_published'] = df['authoryearofbirth'].astype(int) + 25
    return df
def process_file(file_name):
    THERAPY_WORDS = {word: 0 for word in THERAPY_WORD_LIST}
    try:
        f = pd.read_csv(f'{file_name}_counts.txt', sep='\t', header=None, lineterminator='\n', names=['word','count'])
        vocab = dict(zip(f['word'], f['count']))
        for k, v in THERAPY_WORDS.items():
            THERAPY_WORDS[k] = vocab[k] if k in vocab else v
    except FileNotFoundError:
        return THERAPY_WORDS
    return THERAPY_WORDS

def process_gutenberg():
    df = read_data(data_path)
    process_line = lambda file_name: pd.Series(process_file(f'{token_path}/{file_name}'))
    df[[*THERAPY_WORD_LIST]] = df["id"].progress_apply(process_line)
    df.to_csv(f"{ROOT_DIR}/data/processed/gutenberg.csv")

if __name__ == "__main__":
    process_gutenberg()

