import unittest
from unittest.mock import patch, MagicMock
from notion_manage import NotionWorkloadManagement, ScheduleEntity, Response
import requests

class TestNotionWorkloadManagementErrors(unittest.TestCase):

    def setUp(self):
        self.api_key = "test_api_key"
        self.schedule_db_id = "test_schedule_db_id"
        self.workload_db_id = "test_workload_db_id"
        self.manager = NotionWorkloadManagement(self.api_key, self.schedule_db_id, self.workload_db_id)

    @patch('notion_manage.requests.post')
    def test_get_new_schedule_entries_api_error(self, mock_post):
        # API エラーのシミュレーション
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_post.return_value = mock_response

        result = self.manager.get_new_schedule_entries()

        self.assertEqual(result, [])
        self.assertTrue(mock_post.called)

    @patch('notion_manage.requests.patch')
    def test_update_workload_entry_api_error(self, mock_patch):
        # API エラーのシミュレーション
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_patch.return_value = mock_response

        test_schedule = ScheduleEntity(id="test_id", title="Test Title")
        result = self.manager.update_workload_entry(test_schedule)

        self.assertEqual(result.status_code, 500)
        self.assertEqual(result.error_code, "UPDATE_FAILED")
        self.assertEqual(result.error_message, "Internal Server Error")

    @patch('notion_manage.requests.patch')
    def test_update_schedule_flag_api_error(self, mock_patch):
        # API エラーのシミュレーション
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_patch.return_value = mock_response

        test_schedule = ScheduleEntity(id="test_id", title="Test Title")
        result = self.manager.update_schedule_flag(test_schedule)

        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.error_code, "FLAG_UPDATE_FAILED")
        self.assertEqual(result.error_message, "Forbidden")

    @patch('notion_manage.NotionWorkloadManagement.get_new_schedule_entries')
    @patch('notion_manage.NotionWorkloadManagement.update_workload_entry')
    @patch('notion_manage.NotionWorkloadManagement.update_schedule_flag')
    def test_process_new_entries_with_errors(self, mock_flag, mock_workload, mock_get):
        # 新しいエントリーのシミュレーション
        mock_get.return_value = [ScheduleEntity(id="test_id", title="Test Title")]
        
        # workload更新エラーのシミュレーション
        mock_workload.return_value = Response(status_code=500, error_code="UPDATE_FAILED", error_message="Error")
        
        # process_new_entriesの実行
        self.manager.process_new_entries()

        # アサーション
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_workload.called)
        self.assertFalse(mock_flag.called)  # workloadの更新に失敗したので、フラグの更新は呼ばれないはず

if __name__ == '__main__':
    unittest.main()