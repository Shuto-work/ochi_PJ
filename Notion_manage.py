import requests
import time
from datetime import datetime
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()


class ScheduleEntity:
    def __init__(self, id: str, title: str, client_id: str = "", flag: str = "",
                 start_date: str = "", end_date: str = "", workload: float = 0,
                 parent_task_id: str = "", child_task_ids: List[str] = None):
        self.id = id
        self.title = title
        self.client_id = client_id
        self.flag = flag
        self.start_date = start_date
        self.end_date = end_date
        self.workload = workload
        self.parent_task_id = parent_task_id
        self.child_task_ids = child_task_ids or []


class Response:
    def __init__(self, status_code: int = 200, error_code: str = "", error_message: str = ""):
        self.status_code = status_code
        self.error_code = error_code
        self.error_message = error_message


class NotionWorkloadManagement:
    def __init__(self, NOTION_API_KEY: str, TASK_DB_ID: str, WORKLOAD_SUMMARY_DB_ID: str):
        self.NOTION_API_KEY = NOTION_API_KEY
        self.TASK_DB_ID = TASK_DB_ID
        self.WORKLOAD_SUMMARY_DB_ID = WORKLOAD_SUMMARY_DB_ID

        self.headers = {
            "Authorization": f"Bearer {self.NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        # タスクDB用のプロパティ
        self.task_properties = {
            'flag': 'フラグ',
            'title': '名前',
            'client': '顧問先リスト',
            'workload': '工数',
            'status': 'ステータス',
            'start_date': '開始日',
            'end_date': '終了日',
            'parent_task': '親タスク',  # リレーション型
            'child_tasks': '子タスク'   # リレーション型
        }

        # 工数集計DB用のプロパティ
        self.workload_properties = {
            'task': '予定',
            'client': '顧客先DB',
            'workload': '工数集計',
            'title': '名前'
        }

    def get_database_properties(self):
        """データベースのプロパティを取得して表示"""
        task_url = f"https://api.notion.com/v1/databases/{self.TASK_DB_ID}"
        task_response = requests.get(task_url, headers=self.headers)

        if task_response.status_code == 200:
            properties = task_response.json().get('properties', {})
            print("\nTask Database Properties:")
            for prop_name, prop_info in properties.items():
                print(f"- {prop_name} (type: {prop_info['type']})")
        else:
            print(f"Error fetching task database properties: {
                  task_response.text}")

        workload_url = f"https://api.notion.com/v1/databases/{
            self.WORKLOAD_SUMMARY_DB_ID}"
        workload_response = requests.get(workload_url, headers=self.headers)

        if workload_response.status_code == 200:
            properties = workload_response.json().get('properties', {})
            print("\nWorkload Summary Database Properties:")
            for prop_name, prop_info in properties.items():
                print(f"- {prop_name} (type: {prop_info['type']})")
        else:
            print(f"Error fetching workload database properties: {
                  workload_response.text}")

    def get_new_schedule_entries(self) -> List[ScheduleEntity]:
        """新規スケジュールエントリーの取得"""
        url = f"https://api.notion.com/v1/databases/{self.TASK_DB_ID}/query"
        payload = {
                "filter": {
                "and": [
                    {
                        "property": self.task_properties['flag'],
                        "checkbox": {
                            "equals": False
                        }
                    },
                    {
                        "property": self.task_properties['client'],
                        "relation": {
                            "is_not_empty": True
                        }
                    }
                ]
            }
        }

        response = requests.post(url, json=payload, headers=self.headers)

        if response.status_code != 200:
            print(f"Error fetching new schedule entries: {response.text}")
            return []

        results = response.json().get("results", [])
        schedule_entries = []

        for result in results:
            properties = result.get("properties", {})

            # rollupから親タスクの情報を取得
            parent_task_id = ""
            parent_task_rollup = properties.get(
                self.task_properties['parent_task'], {})
            if parent_task_rollup.get("rollup", {}).get("array", []):
                parent_task_id = parent_task_rollup["rollup"]["array"][0].get(
                    "relation", {}).get("id", "")

            # 子タスクIDsの取得
            child_task_ids = []
            child_task_relations = properties.get(
                self.task_properties['child_tasks'], {}).get("relation", [])
            for child in child_task_relations:
                child_task_ids.append(child.get("id", ""))

            schedule_entries.append(
                ScheduleEntity(
                    id=result["id"],
                    title=properties.get(self.task_properties['title'], {}).get(
                        "title", [{}])[0].get("plain_text", ""),
                    client_id=properties.get(self.task_properties['client'], {}).get("relation", [{}])[0].get(
                        "id", "") if properties.get(self.task_properties['client'], {}).get("relation") else "",
                    flag=properties.get(self.task_properties['flag'], {}).get(
                        "checkbox", False),
                    start_date=properties.get(self.task_properties['start_date'], {}).get(
                        "date", {}).get("start", ""),
                    end_date=properties.get(self.task_properties['end_date'], {}).get(
                        "date", {}).get("end", ""),
                    workload=properties.get(
                        self.task_properties['workload'], {}).get("number", 0),
                    parent_task_id=parent_task_id,
                    child_task_ids=child_task_ids
                )
            )

        return schedule_entries

    def update_parent_task(self, schedule: ScheduleEntity) -> Response:
        """親タスクの更新"""
        if not schedule.parent_task_id:
            return Response()

        url = f"https://api.notion.com/v1/pages/{schedule.parent_task_id}"

        # 親タスクの子タスクリレーションを更新
        payload = {
            "properties": {
                self.task_properties['child_tasks']: {
                    "relation": [{"id": schedule.id}]
                }
            }
        }

        response = requests.patch(url, json=payload, headers=self.headers)

        if response.status_code != 200:
            return Response(
                status_code=response.status_code,
                error_code="PARENT_UPDATE_FAILED",
                error_message=response.text
            )

        return Response()

    def update_workload_entry(self, schedule: ScheduleEntity) -> Response:
        """工数集計DBの更新"""
        query_url = f"https://api.notion.com/v1/databases/{
            self.WORKLOAD_SUMMARY_DB_ID}/query"
        query_payload = {
            "filter": {
                "property": self.workload_properties['client'],
                "relation": {
                    "contains": schedule.client_id
                }
            }
        }

        query_response = requests.post(
            query_url, json=query_payload, headers=self.headers)

        if query_response.status_code != 200:
            return Response(
                status_code=query_response.status_code,
                error_code="QUERY_FAILED",
                error_message=query_response.text
            )

        results = query_response.json().get("results", [])
        if not results:
            print(f"No workload entry found for client ID: {
                  schedule.client_id}")
            return Response(
                status_code=404,
                error_code="NOT_FOUND",
                error_message="Workload entry not found"
            )

        # 既存の工数集計レコードを更新
        workload_entry_id = results[0]["id"]
        url = f"https://api.notion.com/v1/pages/{workload_entry_id}"

        existing_tasks = results[0]["properties"][self.workload_properties['task']]["relation"]
        new_schedules = existing_tasks + [{"id": schedule.id}]

        payload = {
            "properties": {
                self.workload_properties['task']: {
                    "relation": new_schedules
                }
            }
        }

        response = requests.patch(url, json=payload, headers=self.headers)

        if response.status_code != 200:
            return Response(
                status_code=response.status_code,
                error_code="UPDATE_FAILED",
                error_message=response.text
            )

        return Response()

    def update_schedule_flag(self, schedule: ScheduleEntity) -> Response:
        """スケジュールフラグの更新"""
        url = f"https://api.notion.com/v1/pages/{schedule.id}"
        payload = {
            "properties": {
                self.task_properties['flag']: {
                    "checkbox": True
                }
            }
        }

        response = requests.patch(url, json=payload, headers=self.headers)

        if response.status_code != 200:
            return Response(
                status_code=response.status_code,
                error_code="FLAG_UPDATE_FAILED",
                error_message=response.text
            )

        return Response()

    def process_new_entries(self):
        """新規エントリーの処理"""
        new_entries = self.get_new_schedule_entries()
        print(f"Found {len(new_entries)} new entries to process")

        for entry in new_entries:
            print(f"Processing entry: {entry.title}")

            # 親タスクの更新
            parent_response = self.update_parent_task(entry)
            if parent_response.status_code != 200:
                print(f"Failed to update parent task for entry {
                      entry.id}: {parent_response.error_message}")
                continue

            # 工数の更新
            workload_response = self.update_workload_entry(entry)
            if workload_response.status_code == 200:
                flag_response = self.update_schedule_flag(entry)
                if flag_response.status_code != 200:
                    print(f"Failed to update flag for entry {
                          entry.id}: {flag_response.error_message}")
                else:
                    print(f"Successfully processed entry: {entry.title}")
            else:
                print(f"Failed to update workload for entry {
                      entry.id}: {workload_response.error_message}")

    def run(self, interval: int = 15):
        """メインの実行ループ"""
        print("Starting Notion Workload Manager...")
        print(f"Task DB ID: {self.TASK_DB_ID}")
        print(f"Workload Summary DB ID: {self.WORKLOAD_SUMMARY_DB_ID}")

        # 起動時にデータベースプロパティを確認
        self.get_database_properties()

        while True:
            print(f"\nProcessing new entries at {datetime.now()}")
            self.process_new_entries()
            time.sleep(interval)


if __name__ == "__main__":
    NOTION_API_KEY = os.getenv("NOTION_API_KEY")
    TASK_DB_ID = os.getenv("TASK_DB_ID")
    WORKLOAD_SUMMARY_DB_ID = os.getenv("WORKLOAD_SUMMARY_DB_ID")

    if not all([NOTION_API_KEY, TASK_DB_ID, WORKLOAD_SUMMARY_DB_ID]):
        print("Error: Missing required environment variables")
        print(f"NOTION_API_KEY present: {bool(NOTION_API_KEY)}")
        print(f"TASK_DB_ID present: {bool(TASK_DB_ID)}")
        print(f"WORKLOAD_SUMMARY_DB_ID present: {
              bool(WORKLOAD_SUMMARY_DB_ID)}")
        exit(1)

    workload_manager = NotionWorkloadManagement(
        NOTION_API_KEY, TASK_DB_ID, WORKLOAD_SUMMARY_DB_ID
    )
    workload_manager.run()
