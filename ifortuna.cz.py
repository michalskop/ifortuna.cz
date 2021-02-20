""" Scraper for ifortuna.cz"""

import csv
import datetime
from lxml import html, etree
import requests

now = datetime.datetime.utcnow().isoformat()

url_base = "https://www.ifortuna.cz/bets/ajax/loadmoresport/"
url_dir = "politika"
url_params = "page="

header = ['date', 'market_title', 'title', 'identifier', 'odd_name', 'value']
competition_header = ['id', 'name', 'sport_id', 'sport', 'created_at']


def _update_competition(competition):
    update = True
    with open("./competitions.csv") as f:   
        dr = csv.DictReader(f) 
        for row in dr:
            ro = row
            del ro['created_at']
            if ro['id'] == competition['id']:
                update = False
    with open("./competitions.csv", "a") as f: 
        if update:
            dw = csv.DictWriter(f, competition_header)
            competition['created_at'] = datetime.datetime.now().isoformat()
            dw.writerow(competition)
            with open("data/" + competition['id'] + ".csv", "w") as fout:
                dw = csv.DictWriter(fout, header)
                dw.writeheader()
            

i = 0
next = True
while next:
    url = url_base + url_dir + "?" + url_params + str(i)
    r = requests.get(url)

    if len(r.text) > 100:

        domtree = html.fromstring(r.text)

        sections = domtree.xpath('//section[@class="competition-box"]')

        for section in sections:
            competition = {
                "name": section.attrib['data-competition'],
                "id": section.attrib['data-id'],
                "sport_id": section.attrib['data-sport-id'],
                "sport": section.attrib['data-sport']
            }
            _update_competition(competition)
            # print(competition)
        
            event_lists = section.xpath('div[@class="events-list"]')
            for event_list in event_lists:
                market_lists = event_list.xpath('div[@class="markets-list"]')
                for market_list in market_lists:
                    # market_list.attrib['']
                    tables = market_list.xpath('./div/table')
                    for table in tables:
                        # title
                        title = table.xpath('./thead/tr/th/span[@class="market-sub-name"]')[0].text.strip()
                        # odd names
                        odd_names_el = table.xpath('./thead/tr/th/span[@class="odds-name"]')
                        odd_names = []
                        for odd_name in odd_names_el:
                            odd_names.append(odd_name.text.strip())
                        # data
                        trs = table.xpath('./tbody/tr')
                        items = []
                        for tr in trs:
                            item = {'odds': []}
                            item['title'] = tr.xpath('./td[@class="col-title"]')[0].attrib['data-value']
                            item['identifier'] = tr.xpath('./td[@class="col-title"]/span/span[@class="event-info-number"]')[0].text.strip()
                            tds = tr.xpath('./td[@class="col-odds"]')
                            for td in tds:
                                a = td.xpath('./a')[0]
                                item['odds'].append({
                                    'info': a.attrib['data-info'],
                                    'value': a.attrib['data-value']
                                })
                            item['date'] = tr.xpath('./td[@class="col-date"]')[0].attrib['data-value']
                            items.append(item)
                        with open("data/" + competition['id'] + ".csv", "a") as fout:
                            dw = csv.DictWriter(fout, header)
                            for item in items:
                                index = 0
                                for odd in item['odds']:
                                    it = {
                                        'date': now,
                                        'market_title': title,
                                        'title': item['title'],
                                        'identifier': item['identifier'],
                                        'odd_name': odd_names[index],
                                        'value': odd['value']
                                    }
                                    dw.writerow(it)
                                    index += 1

                    
        i += 1
        print(i)

    else:
        next = False
