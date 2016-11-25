# utils for ifortuna.cz scraper
from lxml import html, etree
import re
import requests

import settings

def scrape_dir(fdir):
    url = settings.fortuna_url + fdir + settings.fortuna_params
    r = requests.get(url)
    data = []
    if r.status_code == 200:
        new_text = r.text.replace('<?xml version="1.0" encoding="utf-8"?>\r\n','')
        domtree = html.fromstring(new_text)

        divs = domtree.xpath('//div[@class="gradient_table"]')
        for div in divs:
            try:
                group = {}
                group['identifier'] = re.search('bet-table-holder-(\d{1,})',div.xpath('@id')[0]).group(1)
                group['title'] = ''.join(div.xpath('div/h3')[0].itertext()).strip()
                print(group['title'])
                try:
                    group['title_comment'] = div.xpath('div/p')[0].text
                except:
                    group['title_comment'] = ""
                group['title_bet'] = div.xpath('div/div/table/thead/tr[@class="header-row"]/th[@class="col_title_info"]/a')[0].text.strip()
                print(group['title_bet'])

                ths = div.xpath('div/div/table/thead/tr[@class="header-row"]/th[@class="col_bet"]')
                group['bets'] = []
                for th in ths:
                    if len(th.xpath('span')) > 0:
                        group['bets'].append(th.xpath('span')[0].text.strip())
                    else:
                        group['bets'].append(th.xpath('a')[0].text.strip())

                trs = div.xpath('div/div/table/tbody/tr')
                rows = []
                for tr in trs:
                    item = {}
                    try:
                        item['title'] = tr.xpath('td[@class="col_title"]/div/span/a')[0].text.strip()
                        try:
                            item['title'] += " " + tr.xpath('td[@class="col_title"]/div/span/span/span')[0].text.strip()
                        except:
                            nothing = None
                        item['bets'] = []
                        item['identifier'] = tr.xpath('td[@class="col_title"]/div/span/span')[0].text.strip()
                        ass = tr.xpath('td[@class="col_bet "]/a')
                        for a in ass:
                            item['bets'].append("".join(a.itertext()).strip())
                        item['date_bet'] = ''.join(tr.xpath('td[@class="col_date sorted_column"]/span')[0].itertext()).strip()
                        rows.append(item)
                    except:
                        nothing = None
                group['rows'] = rows
                data.append(group)
            except:
                nothing = None
    return data

if __name__ == "__main__":
    # test:
    fdirs = ['basketbal','volejbal','fotbal','hokej','tenis-muzi','tenis-zeny','hazena','ameircky-fotbal','ragby','zabava']
    for fdir in fdirs:
        data = scrape_dir(fdir)
        print(data)
