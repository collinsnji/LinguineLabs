import random

import pandas as pd
import plotly.express as px
import textstat as ts
import visdcc
from correlator import get_all_correlations, get_correlation, get_vectorization
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from flask import Flask, render_template
from helpers import generate_table, parse_data

# Define functions for the app
def get_data_and_stats(file_path):
  word_count_data = get_vectorization(file_path)
  df_bigrams = get_vectorization(file_path, ngrams_range=(2, 2))
  total_word_count = word_count_data['word_count'].sum()
  df_bigrams = df_bigrams.drop(columns=['word_count'])
  bigram_freq_df = df_bigrams.T
  bigram_freq_df = bigram_freq_df.sum(axis=1)
  bigram_freq_df = bigram_freq_df.T.reset_index()
  bigram_freq_df.columns = ['bigram', 'count']
  bigrams_df = bigram_freq_df.sort_values(by='count', ascending=False)
  with open(file_path, 'r') as f:
    text = f.read()
  
  grade_levels = ['Kindergarten', '1st Grade', '2nd Grade', '3rd Grade', '4th Grade', '5th Grade', '6th Grade', '7th Grade', '8th Grade', '9th Grade', '10th Grade', '11th Grade', '12th Grade', 'College', 'College Graduate']
  stats = {
    'word_count': total_word_count,
    'reading_ease': ts.flesch_reading_ease(text),
    'reading_time': round(ts.reading_time(text, ms_per_char=0.65)),
    'reading_level': grade_levels[min(24, round(abs(ts.automated_readability_index(text))))],
    'text_standard': ts.text_standard(text)
  }
  return word_count_data, bigrams_df, stats

def network_visualization(df, min_count=3):
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


def generate_word_frequency(df):
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
  df.reset_index(inplace=True)
  df = df.rename(columns = {'index': 'section'})
  total_word_count = df['word_count'].sum()
  for col in df.columns:
    if col != 'word_count' and col != 'section':
      df[col] = df[[col, 'word_count']].apply(lambda x: (x[0]/total_word_count) * 100000, axis=1)
  df = df.sort_values(by='word_count', ascending=False)
  return df

def plot_word_frequency(df, words=[]):
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

def plot_word_correlations(df, words=''):
  all_correlations = []
  words = words.split(',')
  words = [word.strip() for word in words]
  if len(words) == 0 or words is None:
    return PreventUpdate
  word_filter = [word for word in words if word in df.columns]
  if len(word_filter) == 0:
    return PreventUpdate
  if len(word_filter) == 1:
    all_correlations = [*get_all_correlations(df, word_filter[0])]
  else:
    all_correlations = [*get_correlation(df, [word_filter[0], word_filter[1]])]
  word_list = []
  correlations_data = {'correlation': [], 'p_value': [], 'is_significant': []}
  for corr in all_correlations:
    word_list.append(corr.word2)
    correlations_data['correlation'].append(corr.correlation)
    correlations_data['p_value'].append(corr.p_value)
    correlations_data['is_significant'].append(corr.is_significant)
  corr_df = pd.DataFrame(columns=word_list)
  corr_data = pd.DataFrame.from_dict(correlations_data)
  correlations_df = pd.concat([corr_df, corr_data], ignore_index=True)
  breakpoint()
  return generate_table(correlations_df.iloc[:, : 10])

# external style sheets
external_stylesheets = [{
  'href': 'https://unpkg.com/spectre.css/dist/spectre.min.css',
  'rel': 'stylesheet'
  },
  {
    'href': 'https://unpkg.com/spectre.css/dist/spectre-exp.min.css',
    'rel': 'stylesheet'
  }, {
    'href': 'https://unpkg.com/spectre.css/dist/spectre-icons.min.css',
    'rel': 'stylesheet'
  },
  {
    'href': 'styles/main.css',
    'rel': 'stylesheet'
  }
]

# Initialize the app
server = Flask(__name__)
app = Dash(server=server, external_stylesheets=external_stylesheets)


# Route other pages
@server.route('/about/')
def about():
  return render_template('about.html')


# Load data and summary stats
# file_path = '/Volumes/Rayla/Projects/SeniorProject/data/example/brave-new-world.txt'
# file_path = '/Volumes/Rayla/Projects/SeniorProject/data/raw/books1/epubtxt/relentless.epub.txt'
# file_path = '/Volumes/Rayla/Projects/SeniorProject/data/example/frankenstein-or-the-modern-prometheus.txt'
file_path = '/Volumes/Rayla/Projects/SeniorProject/data/example/harry-potter-and-the-sorcerers-stone.txt'

# Generate datasets and summary stats
word_count_df, bigrams, stats = get_data_and_stats(file_path)
word_freq_df = generate_word_frequency(word_count_df)
relative_freq_section_df = relative_frequency_by_section(word_count_df)

# Callback functions
@app.callback(
  Output('word-frequency', 'figure'),
  Input('search-word-frequency-button', 'n_clicks'),
  State('search-word-frequency-input', 'value')
)
def update_word_frequency_plot(n_clicks, words):
  words = [] if len(words.strip()) == 0 else words.split(',')
  fig = plot_word_frequency(relative_freq_section_df, words)
  return fig


# App layout
app.layout = html.Div(children=[
  html.Div(className='container px-0', children=[
    html.Div(className='navbar __navbar', children=[
      html.Div(className='navbar-section', children=[
        html.A(className='btn btn-link header-link', href='#', children='Home'),
        html.A(className='btn btn-link header-link', href='/about', children='About'),
        html.A(className='btn btn-link header-link', href='/contact', children='Contact'),
      ]),
      html.Div(className='navbar-center', children=[
        html.H2(className='navbar-brand mr-2 logo', children='Linguine Labs'),
      ]),
      html.Div(className='navbar-section', children=[
        html.Div(className='input-group input-inline', children=[
          html.A(className='btn btn-link header-link', href='//github.com/collinsnji/linguine', children='GitHub')
        ])
      ])
    ]),
    html.Div(className='main-content', children=[
      html.Div(className='stats-bar shadow panel', children=[
        html.Div(className='panel-header', children=[
          html.Div(className='panel-title', children=['Summary Stats'])
        ]),
        html.Div(className='stats-container shadow-line', children=[
          html.Div(className='word-count', children=[
            html.Div(className='stat__value', children=[
              html.H3(className='stat-value', children=[stats['word_count']]),
              html.Span(className='stat__description', children=[
                'Word Count'
              ])
            ])]
          )
        ]),
        html.Div(className='stats-container shadow-line', children=[
          html.Div(className='top-words', children=[
            html.Div(className='stat__value', children=[
              html.P(className='stat-value', children=[
                *map(lambda w: html.Span(className='top__word chip', children=[w]), ['word 1', 'word 2', 'word 3']),
                # [html.Span(className='top__word chip', children=[f'{word}']) for word in ['word 1', 'word 2', 'word 3']]
              ]),
              html.Span(className='stat__description', children=[
                'Top Words in Corpus'
              ])
            ])]
          )
        ]),
        html.Div(className='stats-container shadow-line', children=[
          html.Div(className='reading-ease', children=[
            html.Div(className='stat__value', children=[
              html.H3(className='stat-value', children=[stats['reading_ease']]),
              html.Span(className='stat__description', children=[
                'Reading Ease'
              ])
            ])]
          )
        ]),
        html.Div(className='stats-container shadow-line', children=[
          html.Div(className='reading-level', children=[
            html.Div(className='stat__value', children=[
              html.H3(className='stat-value', children=[stats['reading_level']]),
              html.Span(className='stat__description', children=[
                'Reading Level'
              ])
            ])]
          )
        ]),
        html.Div(className='stats-container shadow-line', children=[
          html.Div(className='reading-time', children=[
            html.Div(className='stat__value', children=[
              html.H3(className='stat-value', children=[stats['reading_time']]),
              html.Span(className='stat__description', children=[
                'Reading Time'
              ])
            ])]
          )
        ]),
      ]),
      html.Div(className='dashboard-items', children=[
        html.Div(className='columns content-space', children=[
          html.Div(className='column col-4 shadow panel word-count-table', children=[
            html.Div(className='panel-header', children=[
              html.Div(className='panel-title', children=['Word Frequency Analysis'])
            ]),
            html.Div(className='panel-body', children=[
              generate_table(word_freq_df, max_rows=100),
            ])
          ]),
          html.Div(className='column col-6 flex-grow-1 shadow panel', children=[
            html.Div(className='panel-header', children=[
              html.Div(className='panel-title', children=['Word Trends']),
              html.Div(className='search-word-frequency input-group', children=[
                dcc.Input(className='form-input', id='search-word-frequency-input', type='text', value=''),
                html.Button(className='btn', id='search-word-frequency-button', n_clicks=0, children='Plot'),
              ])
            ]),
            html.Div(className='panel-body', children=[
                dcc.Graph(
                  id='word-frequency',
                  figure=plot_word_frequency(relative_freq_section_df)
                )
            ])
          ]),
        ]),
        html.Div(className='network-analysis shadow', children=[
          network_visualization(df=bigrams, min_count=2)
        ]),
        html.Div(className='correlation-table shadow', children=[
          html.Div(className='search-word-correlation input-group', children=[
            dcc.Input(className='form-input', id='search-word-correlation-input', type='text', value=''),
            html.Button(className='btn', id='search-word-correlation-button', n_clicks=0, children='Get Correlations'),
          ])
          # generate_table(plot_word_correlations(word_count_df, 'harry'), max_rows=100)
        ])
      ]),
    ]),
  ])
])


if __name__ == '__main__':
  app.run_server(debug=False, threaded=True)