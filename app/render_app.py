# pyright: reportMissingImports=false

from dash import dcc, html
from helpers import generate_table
from app_functions import plot_word_frequency, network_visualization, plot_word_correlations

def RunApplication(AppData):
  # Get data
  word_count_df, bigrams, stats = AppData['word_count_df'], AppData['bigrams'], AppData['stats']
  word_freq_df = AppData['word_freq_df']
  relative_freq_section_df = AppData['relative_freq_section_df']

  # App layout
  return html.Div(className='main-content', children=[
    html.Div(className='stats-bar shadow panel', children=[
      html.Div(className='panel-header', children=[
        html.Div(className='panel-title', children=['Summary Stats'])
      ]),
      html.Div(className='stats-container shadow-line', children=[
        html.Div(className='file-name', children=[
          html.Div(className='stat__value', children=[
            html.H4(className='stat-value', children=[stats['filename']])
          ])]
        )
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
              *map(lambda w: html.Span(className='top__word chip', children=[w]), [w for w in stats['top_10_words']]),
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
              html.Button(className='btn', id='search-word-frequency-button', n_clicks=0, children='View Trend'),
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
      html.Div(className='network-analysis panel shadow', children=[
        html.Div(className='panel-header', children=[
          html.Div(className='panel-title', children=['Centrality Analysis']),
        ]),
        network_visualization(df=bigrams, min_count=2)
      ]),
      html.Div(className='column correlation-table panel shadow', children=[
        html.Div(className='panel-header', children=[
          html.Div(className='panel-title', children=['Word Correlations']),
          html.Div(className='search-word-correlation input-group', children=[
            dcc.Input(className='form-input', id='search-word-correlation-input', type='text', value=''),
            html.Button(className='btn', id='search-word-correlation-button', n_clicks=0, children='Get Correlations'),
          ])
        ]),
        html.Div(className='panel-body', children=[
          html.Div(
            id='word-correlation-table',
            children=plot_word_correlations(word_count_df)
          )
        ])
      ])
    ]),
  ])
