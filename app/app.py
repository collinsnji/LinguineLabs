# pyright: reportMissingImports=false
import os

from dash import Dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_loading_spinners as dls
from flask import Flask, render_template
from helpers import write_file
from render_app import RunApplication
from collections import defaultdict
from app_functions import *

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
server = Flask(__name__, static_folder='assets')
app = Dash(server=server, external_stylesheets=external_stylesheets)
app.title = 'Linguine - Text Analysis App'
AppData = defaultdict(lambda: None)

# Route other pages
@server.route('/about/')
def about():
  return render_template('about.html')

@server.route('/interpretation/')
def interpretation():
  return render_template('interpretation.html')

# Define app callbacks for initial load
@app.callback(
  Output('linguine-app', 'children'),
  [Input('upload-data', 'filename'), Input('upload-data', 'contents')]
)
def save_file(filename, contents):
  # @FIXME: upload the file to a better location. S3 bucket?
  UPLOAD_DIRECTORY = '/tmp/uploads'
  if filename is None or contents is None:
    raise PreventUpdate
  else:
    if filename.endswith('.txt'):
      write_file(UPLOAD_DIRECTORY, filename, contents)
    else:
      raise PreventUpdate
  file__path = os.path.join(UPLOAD_DIRECTORY, filename)
  word_count_df, bigrams, stats = get_data_and_stats(file__path)
  word_freq_df = generate_word_frequency(word_count_df, stats)
  relative_freq_section_df = relative_frequency_by_section(word_count_df)
  stats['filename'] = filename.lower().split('.')[0]
  stats['top_10_words'] = [word_freq_df['Word'].iloc[i] for i in range(10)]
  AppData['word_count_df'] = word_count_df
  AppData['bigrams'] = bigrams
  AppData['stats'] = stats
  AppData['word_freq_df'] = word_freq_df
  AppData['relative_freq_section_df'] = relative_freq_section_df
  return RunApplication(AppData)

@app.callback(
    Output('word-frequency', 'figure'),
    Input('search-word-frequency-button', 'n_clicks'),
    State('search-word-frequency-input', 'value')
  )
def update_word_frequency_plot(n_clicks, words):
  """Update word frequency plot

  Args:
    n_clicks (int): Number of clicks on the button
    words (str): Words to search for

  Returns:
    dash.figure: Plotly figure
  """
  relative_freq_section_df = AppData['relative_freq_section_df']
  words = [] if len(words.strip()) == 0 else words.split(',')
  fig = plot_word_frequency(relative_freq_section_df, words)
  return fig

@app.callback(
  Output('word-correlation-table', 'children'),
  Input('search-word-correlation-button', 'n_clicks'),
  State('search-word-correlation-input', 'value')
)
def update_word_correlation_table(n_clicks, word):
  """Update the word correlation table

  Args:
    n_clicks (int): Number of clicks
    word (str): Word to search for

  Returns:
    html: Table with word correlation
  """
  word_count_df = AppData['word_count_df']
  word = word.strip()
  table = plot_word_correlations(word_count_df, word)
  return table

# Main app layout
app.layout = html.Div(children=[
  html.Div(className='container px-0', children=[
    html.Div(className='navbar __navbar', children=[
      html.Div(className='navbar-section', children=[
        html.A(className='btn btn-link header-link', href='/', children='Home'),
        html.A(className='btn btn-link header-link', href='/about', children='About'),
        html.A(className='btn btn-link header-link', href='/interpretation', children='Interpretation'),
      ]),
      html.Div(className='navbar-center', children=[
        html.H2(className='navbar-brand mr-2 logo', children='Linguine Labs'),
      ]),
      html.Div(className='navbar-section', children=[
        html.Div(className='input-group input-inline', children=[
          html.A(className='btn btn-link header-link', href='//github.com/collinsnji/LinguineLabs', children='GitHub')
        ])
      ])
    ]),
    html.Div(className='file-upload', children=[
      dcc.Upload(id='upload-data',
        className='file-upload__input',
        children=html.Div(['Drag and drop or click to select a file to upload.']),
        multiple=False
      ),
    ]),
    dls.Bars(
      html.Div(id='linguine-app', children=[]),
      fullscreen=True,
      show_initially=False
    )
  ])
])

# Run the app
if __name__ == '__main__':
  app.run_server(debug=False, threaded=True)