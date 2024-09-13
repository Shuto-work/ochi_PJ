import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from your_module import NotionWorkloadManagement, ScheduleEntity, Response


class TestNotionWorkloadManagement(unittest.TestCase):

    def setUp(self):
        self.api_key = "test_api_key"
        self.schedule_db_id = "test_schedule_db_id"
        self.workload_db_id = "test_workload_db_id"
        self.manager = NotionWorkloadManagement(
            self.api_key, self.schedule_db_id, self.workload_db_id)

    @patch('your_module.requests.post')
    def test_get_new_schedule_entries(self, mock_post):
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "test_id_1",
                    "properties": {
                        "タイトル": {"title": [{"plain_text": "Test Title 1"}]},
                        "フラグ": {"number": 0}
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        # メソッドの実行
        result = self.manager.get_new_schedule_entries()

        # アサーション
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], ScheduleEntity)
        self.assertEqual(result[0].id, "test_id_1")
        self.assertEqual(result[0].title, "Test Title 1")
        self.assertEqual(result[0].flag, 0)

    @patch('your_module.requests.patch')
    def test_update_workload_entry(self, mock_patch):
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response

        # テスト用のScheduleEntityの作成
        test_schedule = ScheduleEntity(id="test_id", title="Test Title")

        # メソッドの実行
        result = self.manager.update_workload_entry(test_schedule)

        # アサーション
        self.assertIsInstance(result, Response)
        self.assertEqual(result.status_code, 200)

    @patch('your_module.requests.patch')
    def test_update_schedule_flag(self, mock_patch):
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response

        # テスト用のScheduleEntityの作成
        test_schedule = ScheduleEntity(id="test_id", title="Test Title")

        # メソッドの実行
        result = self.manager.update_schedule_flag(test_schedule)

        # アサーション
        self.assertIsInstance(result, Response)
        self.assertEqual(result.status_code, 200)


if __name__ == '__main__':
    unittest.main()
