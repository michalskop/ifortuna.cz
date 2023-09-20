"""Download current odds from ifortuna.cz and ifortuna.sk."""

import datetime
import os
import pandas as pd
from requests_html import HTMLSession, HTML, AsyncHTMLSession

session = HTMLSession()

# authentization
# the first part is local, the other takes the values from Github secrets
try:
  import secret
  os.environ['PROXY_SERVERS'] = secret.PROXY_SERVERS
except:
  pass

# proxy
proxy_servers = {
  'https': os.environ.get('PROXY_SERVERS')
}

domains = [
  {
    'domain': 'cz',
    'dir0': '/sazeni/politika'
  },
  {
    'domain': 'sk',
    'dir0': '/stavkovanie/politika'
  }
]

for domain in domains:
  url0 = "https://www.ifortuna." + domain['domain'] + domain['dir0']
  url1 = "https://www.ifortuna.cz/bets/ajax/loadmoresport/politika?timeTo=&rateFrom=&rateTo=&date=&pageSize=1000&page=1"

  # get the page
  now = datetime.datetime.now()
  print(url0)
  r0 = session.get(url0, timeout=10, proxies=proxy_servers)
  r1 = session.get(url1, timeout=10, proxies=proxy_servers)

  # competitions
  competitions = []
  competition_ids = []
  divs = r0.html.find('.competition-box')
  try:
    divs.extend(r1.html.find('.competition-box'))
  except:
    pass
  for div in divs:
    competition_id = div.attrs['data-competition-id']
    if competition_id in competition_ids:
      continue
    competition_name = div.attrs['data-competition-name']
    competition_link = div.find('a')[1].attrs['href']
    competitions.append([now, competition_id, competition_name, competition_link])
    competition_ids.append(competition_id)

  # write to file
  df = pd.read_csv('data/ifortuna.' + domain['domain'] + '.csv')
  pd.concat([df, pd.DataFrame(competitions, columns=['date', 'competition_id', 'competition_name', 'competition_link'])]).to_csv('data/ifortuna.' + domain['domain'] + '.csv', index=False)

  # get the odds
  for competition in competitions:
    url = 'https://www.ifortuna.' + domain['domain'] + competition[3]
    print(url)
    r = session.get(url, timeout=10, proxies=proxy_servers)
    tables = r.html.find('.events-table')
    if len(tables) == 1:
      # prepare/read the file
      fname = 'data/' + competition[1] + '.csv'
      if os.path.isfile(fname):
        # Read the CSV file
        df = pd.read_csv(fname)
      else:
        df = pd.DataFrame(columns=['date', 'event_info_number', 'event_name', 'event_link', 'odds', 'datum'])
      
      table = tables[0]
      table = r.html.find('.events-table', first=True)
      tbody = table.find('tbody', first=True)
      trs = tbody.find('tr')
      rows = []
      for tr in trs:
        tds = tr.find('td')
        event_info_number = tr.find('.event-info-number', first=True).text
        event_name = tds[0].attrs['data-value']
        event_link = tds[0].find('a', first=True).attrs['href']
        odds = tds[1].text
        odds2 = tds[2].text
        datum = tds[-1].text
        rows.append([now, event_info_number, event_name, event_link, odds, odds2, datum])
      # write to file
      pd.concat([df, pd.DataFrame(rows, columns=['date', 'event_info_number', 'event_name', 'event_link', 'odds', 'odds2', 'datum'])]).to_csv(fname, index=False)
    else:
      for table in tables:
        # prepare/read the file
        fname = 'data/' + competition[1] + '.v2-1.csv'
        if os.path.isfile(fname):
          # Read the CSV file
          df = pd.read_csv(fname)
        else:
          df = pd.DataFrame(columns=['date', 'event_info_number', 'event_name', 'event_link', 'header1', 'header2', 'odd1', 'odd2', 'datum'])
        
        thead = table.find('thead', first=True)
        header1 = thead.find('th')[1].text
        header2 = thead.find('th')[2].text

        tbody = table.find('tbody', first=True)
        trs = tbody.find('tr')
        rows = []
        for tr in trs:
          tds = tr.find('td')
          event_info_number = tr.find('.event-info-number', first=True).text
          event_name = tds[0].attrs['data-value']
          event_link = tds[0].find('a', first=True).attrs['href']
          odd1 = tds[1].text
          odd2 = tds[2].text
          datum = tds[-1].text
          rows.append([now, event_info_number, event_name, event_link, header1, header2, odd1, odd2, datum])
        # write to file
        pd.concat([df, pd.DataFrame(rows, columns=['date', 'event_info_number', 'event_name', 'event_link', 'header1', 'header2', 'odd1', 'odd2', 'datum'])]).to_csv(fname, index=False)
