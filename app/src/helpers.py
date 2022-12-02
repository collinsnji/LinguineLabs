import pandas as pd
import base64
import io
from dash import html

def parse_data(contents, filename):
  content_type, content_string = contents.split(",")

  decoded = base64.b64decode(content_string)
  try:
    if "csv" in filename:
      df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
  except Exception as e:
    print(e)
    return html.Div(["There was an error processing this file."])
  return df

def generate_table(dataframe, max_rows=10):
  return html.Table([
    html.Thead(
      html.Tr([html.Th(col) for col in dataframe.columns])
    ),
    html.Tbody([
      html.Tr([
          html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
      ]) for i in range(min(len(dataframe), max_rows))
    ])
  ],
  className='table table-hover'
  )


def relative_frequency(*params):
    raw_freq, corpus_size = params
    return (raw_freq/corpus_size) * 1_00_000

def normalize_data_by_section(data_frame):
  groups = []
  for col in data_frame.columns:
    if col not in ['section', 'word_count']:
      group = data_frame.groupby('section').agg({col: 'sum', 'word_count': 'sum' }).apply(lambda x: relative_frequency(*x), axis=1)
      group = group.reset_index()
      group.columns = ['section', col]
      groups.append(group)
  for group in groups[1:]:
    groups[0] = groups[0].merge(group, on='section', how='left')

  normalized_data_by_section = groups[0]
  print('here')
  return normalized_data_by_section