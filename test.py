import requests
import time
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class ScheduleEntity:
    def __init__(self, id: int, title: str, flag: int = 0, error_code: str = "", error_message: str = ""):
        self.id = id
        self.title = title
        self.flag = flag
        self.error_code = error_code
        self.error_message = error_message


class Response:
    def __init__(self, status_code: int = 200, error_code: str = "", error_message: str = ""):
        self.status_code = status_code
        self.error_code = error_code
        self.error_message = error_message


class NotionWorkloadManagement:
    def __init__(self, notion_api_key: str, schedule_db_id: str, workload_db_id: str):
        self.notion_api_key = notion_api_key
        self.schedule_db_id = schedule_db_id
        self.workload_db_id = workload_db_id
        self.headers = {
            "Authorization": f"Bearer {self.notion_api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def get_new_schedule_entries(self) -> List[ScheduleEntity]:
        url = f"https://api.notion.com/v1/databases/{
            self.schedule_db_id}/query"
        payload = {
            "filter": {
                "and": [
                    {"property": "フラグ", "number": {"equals": 0}},
                    {"property": "顧問先", "relation": {"is_not_empty": True}}
                ]
            }
        }
        response = requests.post(url, json=payload, headers=self.headers)

        if response.status_code != 200:
            print(f"Error fetching new schedule entries: {response.text}")
            return []

        results = response.json().get("results", [])
        return [ScheduleEntity(
            id=result["id"],
            title=result["properties"]["タイトル"]["title"][0]["plain_text"] if result["properties"]["タイトル"]["title"] else "",
            flag=result["properties"]["フラグ"]["number"]
        ) for result in results]

    def update_workload_entry(self, schedule: ScheduleEntity) -> Response:
        url = f"https://api.notion.com/v1/pages/{self.workload_db_id}"
        payload = {
            "properties": {
                "予定": {
                    "relation": [{"id": schedule.id}]
                }
            }
        }
        response = requests.patch(url, json=payload, headers=self.headers)

        if response.status_code != 200:
            return Response(status_code=response.status_code, error_code="UPDATE_FAILED", error_message=response.text)

        return Response()

    def update_schedule_flag(self, schedule: ScheduleEntity) -> Response:
        url = f"https://api.notion.com/v1/pages/{schedule.id}"
        payload = {
            "properties": {
                "フラグ": {"number": 1}
            }
        }
        response = requests.patch(url, json=payload, headers=self.headers)

        if response.status_code != 200:
            return Response(status_code=response.status_code, error_code="FLAG_UPDATE_FAILED", error_message=response.text)

        return Response()

    def process_new_entries(self):
        new_entries = self.get_new_schedule_entries()
        for entry in new_entries:
            workload_response = self.update_workload_entry(entry)
            if workload_response.status_code == 200:
                flag_response = self.update_schedule_flag(entry)
                if flag_response.status_code != 200:
                    print(f"Failed to update flag for entry {entry.id}: {flag_response.error_message}")
            else:
                print(f"Failed to update workload for entry {entry.id}: {workload_response.error_message}")

    def run(self, interval: int = 15):
        while True:
            print(f"Processing new entries at {datetime.now()}")
            self.process_new_entries()
            time.sleep(interval)


if __name__ == "__main__":
    notion_api_key = "your_notion_api_key_here"
    schedule_db_id = "your_schedule_db_id_here"
    workload_db_id = "your_workload_db_id_here"

    workload_manager = NotionWorkloadManagement(
        notion_api_key, schedule_db_id, workload_db_id)
    workload_manager.run()
