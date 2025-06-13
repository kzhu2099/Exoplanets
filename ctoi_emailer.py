from kzutil import send_email
import json
import pandas
import tabulate

'''
This is supposed to be in the FATVM.
So, it is really just a shell that can only be tested there.
'''

with open('settings.json', 'r') as file:
    settings = file.read()
    settings = json.loads(settings)

    sender_email = settings['sender_email']
    email_app_password = settings['email_app_password']

with open('ctoi_targets.txt', 'r') as file:
    ticids = file.readlines()

data = pandas.DataFrame()
for ticid in ticids:
    url = f'https://exofop.ipac.caltech.edu/tess/download_planet.php?id={ticid}'

    data = pandas.concat([data, pandas.read_csv(url, delimiter = '|')])

data['Name'] = data['Name'] + ': ' + data['Table']
data = data.sort_values('Name')
data = data.drop_duplicates('Tag')
data = data.set_index('Name')
data = data[['TOI', 'Disposition', 'Date', 'User', 'Tag']]

html = '''\
<!DOCTYPE html>
<html>
    <head>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: Verdana, sans-serif;
            }

            h1 {
                font-size: 15px;
            }

            h2 {
                font-size: 14px;
            }

            p, div {
                font-size: 12px;
            }
        </style>
    </head>
    <body>''' + \
        data.style.set_table_styles([
            {'selector': 'table', 'props': [('border', 'none'), ('border-collapse', 'collapse')]},
            {'selector': 'th, td', 'props': [('border', '1px solid #ddd'), ('padding', '10px')]}
        ]).to_html() + '''
    </body>
</html>
'''

send_email(sender_email, email_app_password,
                 'kzhu2099@gmail.com',
                 'Finny\'s CTOIs',
                 '<h1>Complete PC CTOIs</h1>\n' + html,
                 timezone = 'US/Central')