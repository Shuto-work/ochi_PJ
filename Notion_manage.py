from dotenv import load_dotenv
import os

# .env ファイルの読み込み
load_dotenv()

notion_api_key = os.getenv('NOTION_API_KEY')
notion_db_id = os.getenv('NOTION_DB_ID')
