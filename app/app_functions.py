# pyright: reportMissingImports=false
import random

import pandas as pd
import plotly.express as px
import textstat as ts
import visdcc
from correlator import get_all_correlations, get_vectorization
from collections import defaultdict
from helpers import generate_table


# Define functions for the app
def get_data_and_stats(file_path):
  """Reads in the data and returns a dataframe and a dictionary of stats

  Args:
    file_path (str): The path to the raw data

  Returns:
    tuple: A tuple containing the dataframes and the stats dictionary (df, bigram_df, stats)
  """
  word_count_data = get_vectorization(file_path)
  df_bigrams = get_vectorization(file_path, ngrams_range=(2, 2))
  total_word_count = word_count_data['word_count'].sum()
  df_bigrams = df_bigrams.drop(columns=['word_count'])
  bigram_freq_df = df_bigrams.T
  bigram_freq_df = bigram_freq_df.sum(axis=1)
  bigram_freq_df = bigram_freq_df.T.reset_index()
  bigram_freq_df.columns = ['bigram', 'count']
  bigrams_df = bigram_freq_df.sort_values(by='count', ascending=False)
  with open(file_path, 'r', encoding='utf8', errors='ignore') as f:
    text = f.read()
  
  grade_levels = ['Kindergarten', '1st Grade', '2nd Grade', '3rd Grade', 
    '4th Grade', '5th Grade', '6th Grade', '7th Grade', '8th Grade', 
    '9th Grade', '10th Grade', '11th Grade', '12th Grade', 'College', 'College Graduate']
  stats = {
    'word_count': total_word_count,
    'reading_ease': ts.flesch_reading_ease(text),
    'reading_time': round(ts.reading_time(text, ms_per_char=0.65)),
    'reading_level': grade_levels[min(24, round(abs(ts.automated_readability_index(text))))],
    'text_standard': ts.text_standard(text)
  }
  return word_count_data, bigrams_df, stats

def network_visualization(df, min_count=3):
  """Creates a network visualization of the bigrams

  Args:
    df (pd.DataFrame): The bigram dataframe
    min_count (int, optional): Minimum number of connections required to plot. Defaults to 3.

  Returns:
    visdcc.Network: The network visualization
  """
  with pd.option_context('mode.chained_assignment', None):
    df = df[df['count']>min_count]
    df.reset_index(inplace=True, drop=True)
    df[['source', 'target']] = df['bigram'].str.split(' ', expand=True)
    df = df.drop(columns=['bigram'])
    df = df[['source', 'target', 'count']]
  node_list = list(set(df['source'].values.tolist() + df['target'].values.tolist()))
  nodes = [{'id': node, 'label': node, 'shape': 'dot', 'size': 7 } for _, node in enumerate(node_list)]
  edges = [{
    'id': f'{row["source"]}__{row["target"]}',
    'from': row['source'], 'to': row['target'],
    'width': row['count']*0.5}
  for _, row in df.iterrows()]
  return visdcc.Network(
    id = 'net', 
    data = {'nodes': nodes, 'edges': edges},
    options = dict(height= '400px', width= '100%'))


def generate_word_frequency(df, stats):
  """Generates the word frequency data with relative frequencies
  
  Args:
    df (pd.DataFrame): The word frequency dataframe
    stats (dict): The stats dictionary
  
  Returns:
    pd.DataFrame: The word frequency data
  """
  word_freq_df = df.drop(columns=['word_count'])
  word_freq_df = df.sum(axis=0)
  word_freq_df = word_freq_df.T.reset_index()
  word_freq_df.columns = ['Word', 'Count']
  word_freq_df = word_freq_df.sort_values(by='Count', ascending=False)
  word_freq_df = word_freq_df[1:] # drop the word_count row
  word_freq_df.columns = ['Word', 'Count']
  word_freq_df['Relative'] = word_freq_df['Count'].apply(lambda v: round((v/stats['word_count'] * 100000), 3))
  return word_freq_df

def relative_frequency_by_section(df):
  """Generates the relative frequency by section data

  Args:
    df (pd.DataFrame): The word frequency dataframe
  
  Returns:
    pd.DataFrame: The relative frequency by section data
  """
  df.reset_index(inplace=True)
  df = df.rename(columns = {'index': 'section'})
  total_word_count = df['word_count'].sum()
  for col in df.columns:
    if col != 'word_count' and col != 'section':
      df[col] = df[[col, 'word_count']].apply(lambda x: (x[0]/total_word_count) * 100000, axis=1)
  df = df.sort_values(by='word_count', ascending=False)
  return df

def plot_word_frequency(df, words=[]):
  """Plots the word frequency data

  Args:
    df (pd.DataFrame): The word frequency dataframe
    words (list, optional): The words to highlight. Defaults to [].
  
  Returns:
    plotly.express.line: The word frequency plot
  """
  cols = random.sample(df.columns.tolist(), 5)
  if len(words) == 0 or words is None:
    df = df[['section', *cols]]
  else:
    word_filter = [word for word in words if word in df.columns]
    if len(word_filter) == 0:
      df = df[['section', *cols]]
    df = df[['section', *word_filter]]
  with pd.option_context('mode.chained_assignment', None):
    df.section = df.section.astype(int)
    df.sort_values(by='section', ascending=True, inplace=True)
  fig = px.line(df, 
    x='section',
    y=df.columns[1:],
    line_shape='spline',
    template='simple_white',
    markers=True)
  fig.update_xaxes(title_text='Segment')
  fig.update_yaxes(title_text='Relative Frequency')
  fig.update_xaxes(tickmode='linear')
  return fig

def plot_word_correlations(df, word=''):
  """Plots the word correlations for the first 10 words

  Args:
    df (pd.DataFrame): The word frequency dataframe
    word (str, optional): The word to plot. Defaults to ''.
  
  Returns:
    plotly.html: The word correlation table
  """
  all_correlations = []
  word = word.strip()
  if len(word) == 0 or word is None or word == '':
    word = random.sample(df.columns.tolist(), 1)[0]
  if len(word) > 0 and word not in df.columns:
    word = random.sample(df.columns.tolist(), 1)[0]
  all_correlations = [*get_all_correlations(df, word)]
  word_list = []
  correlations_data = defaultdict(list)
  for corr in all_correlations:
    word_list.append(corr.word2)
    correlations_data['correlation'].append(round(corr.correlation, 3))
    correlations_data['p_value'].append(round(corr.p_value, 3))
    # correlations_data['is_significant'].append(corr.is_significant)
  correlations_df = pd.DataFrame.from_dict(correlations_data, orient='index', columns=word_list)
  with pd.option_context('mode.chained_assignment', None):
    correlations_df.reset_index(inplace=True)
    correlations_df = correlations_df.rename(columns={'level_0': 'statistic'})
  return generate_table(correlations_df.iloc[:, :11])
