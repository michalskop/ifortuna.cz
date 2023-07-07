"""Create daily averages."""

import numpy as np
import pandas as pd

path = "./"

ccs = ['cz', 'sk']

for cc in ccs:
  meta = pd.read_csv(path + f"data/ifortuna.{cc}.csv")

  # get the unique competition IDs
  competition_ids = meta['competition_id'].unique()

  for competition_id in competition_ids:
    # read the data
    try:
      df = pd.read_csv(path + f"data/{competition_id}.csv")

      # get the dates only
      df['date'] = pd.to_datetime(df['date']).dt.date

      # correct the odds format ("1 066.00" to 1066.0)
      try:
        df['odds'] = df['odds'].str.replace('[^\d.]', '', regex=True).astype(float)
      except:
        pass

      # calculate the averages
      pt = pd.pivot_table(df, values='odds', index=['date'], columns=['event_name'], aggfunc=np.average).reset_index()

      # save the averages
      pt.to_csv(path + f"daily/{competition_id}.csv", index=False)
      
    except:
      print(f"Error: {competition_id}")
      pass

