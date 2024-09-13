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
def fetch_record_value(record_name, record_value, target_property_name, target_property_type):

    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID_TASK}/query"
    response = requests.post(url, headers=headers)
    data = response.json()

    # レコードの取得とフィルタリング
    for result in data.get('results', []):
        # レコード名の存在と値の確認
        record_names = result['properties'].get(record_name, {}).get('title', [])

        # リスト内に record_value が存在するかをチェック
        if any(item.get('text', {}).get('content') == record_value for item in record_names):
            # 報酬プロパティの存在確認
            reward = result['properties'].get(target_property_name, {}).get(target_property_type, 0)
            print(f"Task: {record_value}, {target_property_name}: {reward}")
            return reward

    print(f"{record_value}のレコードが見つかりませんでした。")


fetch_record_value('タスク名','決算前確認', '報酬', 'formula')
