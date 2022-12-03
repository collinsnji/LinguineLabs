# pyright: reportMissingImports=false

import base64
import os
from dash import html

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

def write_file(upload_dir, filename, contents):
  if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)
  data = contents.encode('utf8').split(b';base64,')[1]
  with open(os.path.join(upload_dir, filename), 'wb') as f:
    f.write(base64.decodebytes(data))
