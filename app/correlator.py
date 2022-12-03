import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import re
import os
from scipy.stats import pearsonr
from collections import namedtuple

def create_sections(text, section_size):
  """Divide a text into sections of equal length
  
  Args:
    text (str): The text to divide
    section_size (int): The size of each section
    
  Yields:
    str: A section of the text
    
  Example:
    >>> for section in create_sections('This is a test', 2):
    >>>   print(section)
  """
  # Credit: https://stackoverflow.com/a/22571421/6544244
  chunk_size = len(text)//section_size
  if len(text) % section_size: chunk_size += 1
  iterator = iter(text)
  for _ in range(section_size):
      accumulator = list()
      for _ in range(chunk_size):
          try: accumulator.append(next(iterator))
          except StopIteration: break
      yield ''.join(accumulator)

def get_vectorization(file_name, max_features=5000, expanded_stop_words=True, ngrams_range=(1, 1)):
  """Get the vectorization of a file

  Args:
      file_name (str): The name of the file to vectorize
      max_features (int, optional): The maximum number of features to use. Defaults to 5000.
      expanded_stop_words (bool, optional): Whether to use the expanded stop words list. Defaults to True.
      ngrams_range (tuple, optional): The range of ngrams to use. Defaults to (1, 1).
  
  Returns:
      pd.DataFrame: The vectorized dataframe
  
  Example:
      >>> df = get_vectorization('data/dataset.txt')
      >>> df.head()
  """
  stop_words = 'english'
  if expanded_stop_words:
    if os.path.exists('stopwords.txt'):
      with open('stopwords.txt', 'r') as f:
        stop_words = f.read().splitlines()
        stop_words = list(set([word.lower() for word in stop_words]))
        stop_words = ENGLISH_STOP_WORDS.union(stop_words)
  
  if type(ngrams_range) == tuple and len(ngrams_range) == 2:
    ngrams_range = ngrams_range
  else:
    raise ValueError("ngram_range must be a tuple of length 2")
  vectorizer = CountVectorizer(
    stop_words=stop_words,
    strip_accents='ascii',
    lowercase=True,
    decode_error='ignore',
    ngram_range=ngrams_range,
    max_features = max_features,
    preprocessor=lambda x: re.sub(r'_|\d+', '', x.lower()).lower()
  )
  with open(file_name) as f:
    corpus = f.read()
    corpus = list(create_sections(corpus, 10))
  try:
    feature_matrix = vectorizer.fit(corpus)
    feature_vector = feature_matrix.transform(corpus)
    word_list = vectorizer.get_feature_names_out()
    frequency = feature_vector.toarray()
    sections = [f'{i}' for i in range(1, len(corpus) + 1)]
    df = pd.DataFrame(frequency, columns=word_list, index=sections)
    section_lengths = [len(section.split(" ")) for section in corpus]
    df['word_count'] = pd.Series(section_lengths, index=df.index)
    return df
  except ValueError as e:
    print(f"Error with {file_name}")
    raise e


def get_correlation(dataframe: pd.DataFrame, word_list: list) -> namedtuple:
  """Get the correlation between two words
  
  Args:
    dataframe (pandas.Dataframe): A dataframe with the columns being the words
    word_list (list): A list of two words
  
  Raises:
    TypeError: If dataframe is not a pandas DataFrame
    ValueError: If word_list is not a list of two words
  
  Returns:
    Correlation: A namedtuple with the following fields:
      word1 (str): The first word
      word2 (str): The second word
      correlation (float): The correlation between the two words
      p_value (float): The p-value of the correlation
      is_significant (bool): Whether or not the correlation is significant
  Example:
    >>> get_correlation(df, ['cancer', 'breast'])
    >>> Correlation(word1='cancer', word2='breast', correlation=0.99 p_value=0.0, is_significant=True)
  """
  if not isinstance(dataframe, pd.DataFrame):
    raise TypeError("dataframe must be a pandas DataFrame")
  for word in word_list:
    if word not in dataframe.columns:
      raise ValueError(f"'{word}' not in dataframe")
  if len(word_list) != 2:
      raise ValueError("word_list must be of length 2")
  word1, word2 = word_list

  Correlation = namedtuple('Correlation', ['word1', 'word2', 'correlation', 'p_value', 'is_significant'])
  col1 = dataframe[word1].astype('int').to_numpy()
  col2 = dataframe[word2].astype('int').to_numpy()
  correlation, p_value = pearsonr(col1, col2)
  is_significant = p_value < 0.05
  return Correlation(word1, word2, correlation, p_value, is_significant)

def get_all_correlations(dataframe, word):
  """Get all correlations for a given word

  Args:
      dataframe (pandas.Dataframe): A dataframe with the columns being the words
      word (str): The word to get correlations for

  Raises:
      TypeError: If dataframe is not a pandas DataFrame
      ValueError: If word is not in the dataframe

  Returns:
      Correlation: A namedtuple with the following fields:
        word1 (str): The first word
        word2 (str): The second word
        correlation (float): The correlation between the two words
        p_value (float): The p-value of the correlation
        is_significant (bool): Whether or not the correlation is significant
  Example:
      >>> get_all_correlations(df, 'cancer')
      >>> Correlation(word1='cancer', word2='breast', correlation=0.99 p_value=0.0, is_significant=True)
  """
  if not isinstance(dataframe, pd.DataFrame):
    raise TypeError("dataframe must be a pandas DataFrame")
  if word not in dataframe.columns:
    raise ValueError(f"'{word}' not in dataframe")
  correlations = []
  for col in dataframe.columns:
    if col == word:
      continue
    correlations.append(get_correlation(dataframe, [word, col]))
  # sort by p-value, where lower is better
  correlations.sort(key=lambda x: x.p_value)
  return correlations

if __name__ == "__main__":
  f = "/tmp/frankenstein-or-the-modern-prometheus.txt"
  df = get_vectorization(f, max_features=None)
  print(get_correlation(df, ['man', 'father']))

