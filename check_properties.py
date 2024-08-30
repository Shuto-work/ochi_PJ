# 各DBがどんなプロパティを保持しているのかチェック
import requests
from Notion_manage import NOTION_DB_ID_TOTAL_CALC, NOTION_DB_ID_TASK, NOTION_DB_ID_CLIENT, headers

# Notionエンドポイント
url = f'https://api.notion.com/v1/databases/{NOTION_DB_ID_TOTAL_CALC}'

response = requests.get(url, headers=headers)


def check_notionDB_properties():
    if response.status_code == 200:
        data = response.json()
        # print('プロパティ情報')
        properties = data.get('properties', {})
        for prop_name, prop_info in properties.items():
            print(f"プロパティ名: {prop_name}")
            print(f"  タイプ: {prop_info['type']}")
            print(f"  詳細: {prop_info}")

    else:
        print(f"データベース情報の取得に失敗しました。ステータスコード: {response.status_code}")
        print(f"エラーメッセージ: {response.json()}")  # エラー詳細の出力


check_notionDB_properties()
