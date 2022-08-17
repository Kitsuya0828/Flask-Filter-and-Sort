from flask import Flask, render_template, request
import json
import glob
from datetime import datetime
import pandas as pd

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def result():
    form_data_key = ['date_from', 'date_to', 'team', 'where', 'type', 'sort']
    form_data_value = {key : request.form.get(key) for key in form_data_key}
    print(form_data_value)
    
    logs = []
    log_files = glob.glob("./T*T.jsonl")
    for file in log_files:
        with open(file) as f:
            for line in f:
                try:
                    row_dict = json.loads(line)
                    row_dict['date'] = datetime.strptime(row_dict['date'], "%Y%m%d_%H%M%S")
                    logs.append(row_dict)
                except Exception as e:
                    print(e)
    
    df_logs = pd.DataFrame(logs)
    
    if form_data_value['date_from']:
        date_from = datetime.strptime(form_data_value['date_from'], "%Y-%m-%d")
        df_logs = df_logs[date_from <= df_logs['date']]
        
    if form_data_value['date_to']:
        date_to = datetime.strptime(form_data_value['date_to'], "%Y-%m-%d")
        date_to = date_to.replace(hour=23, minute=59, second=59)
        df_logs = df_logs[df_logs['date'] < date_to]
    
    unique_values = {}
    print(df_logs)
    
    if form_data_value['team']:
        df_logs = df_logs[df_logs['team']==form_data_value['team']]
    unique_values['team'] = df_logs['team'].unique()
    
    if form_data_value['where']:
        df_logs = df_logs[df_logs['where']==form_data_value['where']]
    unique_values['where'] = df_logs['where'].unique()
    
    if form_data_value['type']:
        df_logs = df_logs[df_logs['type']==form_data_value['type']]
    unique_values['type'] = df_logs['type'].unique()
    
    if form_data_value['sort'] in ['descending', None]:
        sorted_df_logs = df_logs.sort_values(by=['date'], ascending=False)
    else:
        sorted_df_logs = df_logs.sort_values(by=['date'])
    
    logs_list = sorted_df_logs.to_dict('records')
    
    return render_template('index.html', log=logs_list, uniq=unique_values)


if __name__ == '__main__':
    app.run(debug=True)
