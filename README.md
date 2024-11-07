# ochi_PJ

## インストール
### 1, リポジトリをクローンする
```bash
git clone <repository-url>
```
### 2, 依存関係のインストール
```bash
pip install -r requirements.txt
```
requirements.txtファイルは、インストールされた依存関係にあるライブラリなどを記載しているファイルです。pythonはこのファイルを参照します。

## 各自ローカル環境で実行する場合
### API KeyとデータベースIDの取得

1、Notion インテグレーションキー
https://www.notion.so/my-integrations

2、各Notionデータベースのid
https://note.com/amatyrain/n/nb9ebe31dfab7

### .envファイルにAPI keyを記述
```env
# Active DB Configuration
NOTION_API_KEY=Your_API_Key
TASK_DB_ID=Your_task_database_id
WORKLOAD_SUMMARY_DB_ID=Your_task_WORKLOAD_SUMMARY_id
```
・「=」の前後はスペース無しで詰めて記述。
・プロジェクトルートディレクトリに配置する。

### 実行コマンド
```
python ファイル名.py
```
