import requests
from dotenv import load_dotenv
import os

# .env ファイルの読み込み
load_dotenv()

NOTION_API_KEY = os.getenv('notion_api_key')
NOTION_DB_ID_TOTAL_CALC = os.getenv('NOTION_DB_ID_TOTAL_CALC')
NOTION_DB_ID_TASK = os.getenv('notion_db_id_task')
NOTION_DB_ID_CLIENT = os.getenv('notion_db_id_client')

# ヘッダー設定
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# レコード（task10）を取得するためのクエリ
def get_task_property_value():
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID_TASK}/query"
    response = requests.post(url, headers=headers)
    data = response.json()

# レコードの取得とフィルタリング
    for result in data.get('results', []):
        # 名前プロパティの存在と値の確認
        name_property = result['properties'].get('タスク名', {}).get('title', [])
        if name_property and name_property[0].get('text', {}).get('content') == "task10":
            # 報酬プロパティの存在確認
            reward = result['properties'].get('報酬', {}).get('formula', 0)
            print(f"Task: task10, 報酬: {reward}")
            return reward
    print("task10のレコードが見つかりませんでした。")

# 実行
get_task_property_value()
