from flask import Flask, render_template, request
import json
import glob
from datetime import datetime
import pandas as pd

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def result():
    # フォームから入力情報を抽出
    form_data_key = ['date_from', 'date_to', 'team', 'where', 'type', 'sort']
    form_data_value = {key: request.form.get(key) for key in form_data_key}

    # ファイルから表のデータを読み込む
    logs = []
    log_files = glob.glob("./T*T.jsonl")    # 表示するjsonlファイル
    for file in log_files:
        with open(file) as f:
            for line in f:
                try:
                    row_dict = json.loads(line)
                    # 日付をdatetime型に
                    row_dict['date'] = datetime.strptime(row_dict['date'], "%Y%m%d_%H%M%S")
                    logs.append(row_dict)
                except Exception as e:
                    print(e)

    # dict型のリストをDataFrameに変換
    df_logs = pd.DataFrame(logs)
    original_df_logs = df_logs.copy()

    # 開始日時のフィルタリング
    if form_data_value['date_from']:
        date_from = datetime.strptime(form_data_value['date_from'], "%Y-%m-%d")
        df_logs = df_logs[date_from <= df_logs['date']]

    # 終了日のフィルタリング
    if form_data_value['date_to']:
        date_to = datetime.strptime(form_data_value['date_to'], "%Y-%m-%d")
        date_to = date_to.replace(hour=23, minute=59, second=59)    # 終了日時は23:59:59に設定
        df_logs = df_logs[df_logs['date'] < date_to]

    # ドロップダウンに表示するためのカラムごとの固有要素
    unique_values = {}

    # チーム名のフィルタリング
    if form_data_value['team']:
        df_logs = df_logs[df_logs['team'] == form_data_value['team']]
    unique_values['team'] = original_df_logs['team'].unique()

    # 場所のフィルタリング
    if form_data_value['where']:
        df_logs = df_logs[df_logs['where'] == form_data_value['where']]
    unique_values['where'] = original_df_logs['where'].unique()

    # 種類のフィルタリング
    if form_data_value['type']:
        df_logs = df_logs[df_logs['type'] == form_data_value['type']]
    unique_values['type'] = original_df_logs['type'].unique()

    # ソート（デフォルトは日時降順）
    if form_data_value['sort'] in ['descending', None]:
        sorted_df_logs = df_logs.sort_values(by=['date'], ascending=False)
    else:
        sorted_df_logs = df_logs.sort_values(by=['date'])

    # DataFrameをdict型のリストに変換
    logs_list = sorted_df_logs.to_dict('records')

    # フィルタリングしたログとドロップダウンリストを渡してレンダリングする
    return render_template('index.html', log=logs_list, uniq=unique_values)


if __name__ == '__main__':
    app.run()
