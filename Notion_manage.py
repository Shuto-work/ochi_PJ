import requests
from dotenv import load_dotenv
import os

# .env ファイルの読み込み
load_dotenv()

NOTION_API_KEY = os.getenv('notion_api_key')
NOTION_DB_ID_TOTAL_CALC = os.getenv('notion_db_id_total_calc')
NOTION_DB_ID_TASK = os.getenv('notion_db_id_task')
NOTION_DB_ID_CLIENT = os.getenv('notion_db_id_client')

# ヘッダー設定
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 任意のレコード値を取得する関数
def fetch_record_value(record_name):
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID_TASK}/query"
    response = requests.post(url, headers=headers)
    data = response.json()

    # レコードの取得とフィルタリング
    for result in data.get('results', []):
        # 名前プロパティの存在と値の確認
        name_property = result['properties'].get('タスク名', {}).get('title', [])

        # リスト内に "task10" が存在するかをチェック
        if any(item.get('text', {}).get('content') == record_name for item in name_property):
            # 報酬プロパティの存在確認
            reward = result['properties'].get('報酬', {}).get('formula', 0)
            print(f"Task: {record_name}, 報酬: {reward}")
            return reward

    print(f"{record_name}のレコードが見つかりませんでした。")


fetch_record_value('決算前確認')
