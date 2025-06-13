from kzutil import send_email
import json
import pandas

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
data = data[['Name', 'TOI', 'Disposition', 'Date', 'User', 'Tag']]

css = '''\
<style>
    /* Global styles from your original HTML */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: Verdana, sans-serif; /* Your specified font */
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

    /* Styles specifically for the Pandas DataFrame table */
    .dataframe {
        border: 1px solid #ddd; /* Apply a single border to the entire table */
        border-collapse: collapse; /* Essential for collapsing internal borders */
        width: 100%; /* Make the table responsive, taking full width */
        font-family: Verdana, sans-serif; /* Use your specified font */
        border-radius: 8px; /* Apply rounded corners to the table */
        overflow: hidden; /* Ensures rounded corners clip content */
        margin-top: 20px; /* Add some space above the table */
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* Subtle shadow for depth */
    }

    /* Target table headers and data cells */
    .dataframe th,
    .dataframe td {
        padding: 8px 10px; /* Adjusted padding to make cells smaller */
        border: none; /* Explicitly remove individual cell borders */
        text-align: left; /* Ensure text is left-aligned */
    }

    /* Style table headers */
    .dataframe th {
        background-color: #eef1f5; /* Light background for headers */
        font-weight: bold;
        color: #333;
        text-transform: uppercase; /* Make headers uppercase */
    }

    /* Add subtle hover effect for rows */
    .dataframe tbody tr:hover {
        background-color: #f6f8fa;
    }

    /* Apply alternating row colors for better readability */
    .dataframe tbody tr:nth-child(even) {
        background-color: #fdfdfd;
    }

    /* Ensure rounded corners are consistent on the table */
    .dataframe th:first-child {
        border-top-left-radius: 8px;
    }
    .dataframe th:last-child {
        border-top-right-radius: 8px;
    }
    .dataframe tr:last-child td:first-child {
        border-bottom-left-radius: 8px;
    }
    .dataframe tr:last-child td:last-child {
        border-bottom-right-radius: 8px;
    }
</style>'''

html = f'''\
<!DOCTYPE html>
<html>
    <head>
        {css}
    </head>
    <body>
        <h1>Complete PC CTOIs</h1>
        {data.to_html(index = False)}
    </body>
</html>
'''

send_email(sender_email, email_app_password,
                 'kzhu2099@gmail.com',
                 'Finny\'s CTOIs',
                 html,
                 timezone = 'US/Central')