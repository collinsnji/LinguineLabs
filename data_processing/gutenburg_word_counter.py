import os
import subprocess

import pandas as pd
from tqdm import tqdm

tqdm.pandas()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__).split('data_processing')[0])
data_path = f"{ROOT_DIR}/data/raw/project_gutenberg_data/"

def count_tokens(file_name):
  if os.path.exists(f"{data_path}{file_name}"):
    try:
      with open(data_path + file_name) as f:
        count = 0
        for line in f:
          if len(line.split()) > 1:
            _, token_count = line.split()
            count += int(token_count)
    except Exception as e:
      print("An exception occurred for file: ", file_name)
      count = None
    return count
  return None

def process_gutenberg_corpus():
  df_path = f"{ROOT_DIR}/data/processed/gutenberg_corpus.csv"
  df = pd.read_csv(df_path)
  df['word_count'] = df[f'id'].progress_apply(lambda x: count_tokens(f"{x}_counts.txt"))
  df.to_csv(f"{ROOT_DIR}/data/processed/gutenberg_corpus_wc.csv", index=False)

if __name__ == '__main__':
  process_gutenberg_corpus()