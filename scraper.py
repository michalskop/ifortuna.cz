# scrapes odds from ifortuna.cz and updates github datapackages

import csv
import datapackage #v0.8.3
import datetime
import json
import git
import os

import ifortuna_cz_scraper_utils as utils
import settings

data_path = "data/" # from this script to data

# repo settings
repo = git.Repo(settings.git_dir)
git_ssh_identity_file = settings.ssh_file
o = repo.remotes.origin
git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file

total_groups = 0
for fdir in settings.fortuna_dirs:
    data = utils.scrape_dir(fdir)
    date = datetime.datetime.utcnow().isoformat()
    for group in data:
        # load or create datapackage
        try:
            # load datapackage
            datapackage_url = settings.project_url + data_path + group['identifier']  +"/datapackage.json"
            dp = datapackage.DataPackage(datapackage_url)
        except:
            # create datapackage
            dp = datapackage.DataPackage()
            with open(settings.project_url + "/datapackage_prepared.json") as fin:
                prepared = json.load(fin)
            dp.descriptor['identifier'] = group['identifier']
            dp.descriptor['name'] = "ifortuna_cz_" + group['identifier']
            dp.descriptor['title'] = group['title'] + " - odds from ifortuna.cz"
            description = "Scraped odds from ifortuna.cz for: " + group['title'] + "; " + group['title_comment']
            dp.descriptor['description'] = description.strip().strip(";")
            dp.descriptor['description'] += " (" + group['title_bet'] + ")"
            for k in prepared:
                dp.descriptor[k] = prepared[k]
            if not os.path.exists(settings.git_dir + data_path + group['identifier']):
                os.makedirs(settings.git_dir + data_path + group['identifier'])
            with open(settings.git_dir + data_path + group['identifier']  +'/datapackage.json', 'w') as fout:
                fout.write(dp.to_json())
            repo.git.add(settings.git_dir + data_path + group['identifier']  +'/datapackage.json')
            with open(settings.git_dir + data_path + group['identifier']  +'/odds.csv',"w") as fout:
                header = []
                for resource in dp.resources:
                    if resource.descriptor['name'] == 'odds':
                        for field in resource.descriptor['schema']['fields']:
                            header.append(field['name'])
                dw = csv.DictWriter(fout,header)
                dw.writeheader()
            repo.git.add(settings.git_dir + data_path + group['identifier']  +'/odds.csv')

        with open(settings.git_dir + data_path + group['identifier']  +'/odds.csv',"a") as fout:
            header = []
            for resource in dp.resources:
                if resource.descriptor['name'] == 'odds':
                    for field in resource.descriptor['schema']['fields']:
                        header.append(field['name'])
            dw = csv.DictWriter(fout,header)
            for row in group['rows']:
                i = 0
                for bet in row['bets']:
                    attributes = ['date','title','result','odds','date_bet','identifier']
                    item = {
                        'date': date,
                        'title': row['title'],
                        'result': group['bets'][i],
                        'odds': bet,
                        'date_bet': row['date_bet'],
                        'identifier': row['identifier'],
                    }
                    i += 1
                    dw.writerow(item)

        repo.git.add(settings.git_dir + data_path + group['identifier']  +'/odds.csv')

    total_groups += len(data)

with repo.git.custom_environment(GIT_COMMITTER_NAME=settings.bot_name, GIT_COMMITTER_EMAIL=settings.bot_email):
    repo.git.commit(message="happily updating data %s groups of bets" % (total_groups), author="%s <%s>" % (settings.bot_name, settings.bot_email))
with repo.git.custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
    o.push()
