"""
Tests for the scheduler module.

This module contains tests for the scheduler functionality, including
creating, listing, and removing cron jobs.
"""

import os
import sys
import unittest
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scheduler.scheduler import Scheduler, get_scheduler


class TestScheduler(unittest.TestCase):
    """Test cases for the Scheduler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_script_path = os.path.join(self.temp_dir, "script.py")
        self.test_log_dir = os.path.join(self.temp_dir, "logs")
        
        # Create a test scheduler with mock paths
        with patch('os.makedirs'):  # Mock os.makedirs to avoid actual directory creation
            self.scheduler = Scheduler(
                script_path=self.test_script_path,
                log_dir=self.test_log_dir
            )
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove the temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('subprocess.run')
    @patch('os.makedirs')
    def test_init(self, mock_makedirs, mock_run):
        """Test scheduler initialization."""
        # Test that the log directory is created
        scheduler = Scheduler(
            script_path=self.test_script_path,
            log_dir=self.test_log_dir
        )
        
        # Check that the log directory was created
        mock_makedirs.assert_called_once_with(self.test_log_dir, exist_ok=True)
        
        # Check that the script path was set correctly
        self.assertEqual(scheduler.script_path, self.test_script_path)
        
        # Check that the log directory was set correctly
        self.assertEqual(scheduler.log_dir, self.test_log_dir)
    
    @patch('subprocess.run')
    @patch('os.remove')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_create_cron_job(self, mock_open, mock_remove, mock_run):
        """Test creating a cron job."""
        # Mock the subprocess.run to return success
        mock_run.return_value = MagicMock(returncode=0)
        
        # Call the method under test
        result = self.scheduler.create_cron_job(
            schedule="0 0 1 * *",
            comment="Test Cron Job"
        )
        
        # Check that the result is True (success)
        self.assertTrue(result)
        
        # Check that subprocess.run was called twice
        self.assertEqual(mock_run.call_count, 2)
        
        # Check that the temporary file was removed
        mock_remove.assert_called_once_with("/tmp/scraper_crontab")
        
        # Check that the file was opened for writing
        mock_open.assert_called_with("/tmp/scraper_crontab", "a")
        
        # Check that the cron job was written to the file
        handle = mock_open()
        handle.write.assert_any_call("\n# Test Cron Job\n")
        
        # Check that the cron command includes the script path
        self.assertIn(self.test_script_path, str(handle.write.call_args_list))
    
    @patch('subprocess.run')
    @patch('os.remove')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="# Test Cron Job\n0 0 1 * * python /test/path/to/script.py\n")
    def test_remove_cron_job(self, mock_open, mock_remove, mock_run):
        """Test removing a cron job."""
        # Mock the subprocess.run to return success
        mock_run.return_value = MagicMock(returncode=0)
        
        # Call the method under test
        result = self.scheduler.remove_cron_job(comment="Test Cron Job")
        
        # Check that the result is True (success)
        self.assertTrue(result)
        
        # Check that subprocess.run was called twice
        self.assertEqual(mock_run.call_count, 2)
        
        # Check that the temporary file was removed
        mock_remove.assert_called_once_with("/tmp/scraper_crontab")
        
        # Check that the file was opened for reading and writing
        mock_open.assert_any_call("/tmp/scraper_crontab", "r")
        mock_open.assert_any_call("/tmp/scraper_crontab", "w")
    
    @patch('subprocess.run')
    def test_list_cron_jobs(self, mock_run):
        """Test listing cron jobs."""
        # Mock the subprocess.run to return a list of cron jobs
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "# Test Cron Job\n0 0 1 * * python /test/path/to/script.py\n"
        mock_run.return_value = mock_process
        
        # Call the method under test
        result = self.scheduler.list_cron_jobs()
        
        # Check that subprocess.run was called once
        mock_run.assert_called_once()
        
        # Check that the result is a list with the expected content
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "# Test Cron Job")
        self.assertEqual(result[1], "0 0 1 * * python /test/path/to/script.py")
    
    def test_get_common_schedules(self):
        """Test getting common schedules."""
        # Call the method under test
        schedules = Scheduler.get_common_schedules()
        
        # Check that the result is a dictionary with the expected content
        self.assertIsInstance(schedules, dict)
        self.assertIn("0 0 1 * *", schedules)
        self.assertEqual(schedules["0 0 1 * *"], "Monthly (midnight on the 1st day of each month)")
    
    def test_explain_cron_format(self):
        """Test explaining cron format."""
        # Call the method under test
        explanation = Scheduler.explain_cron_format()
        
        # Check that the result is a string with the expected content
        self.assertIsInstance(explanation, str)
        self.assertIn("minute (0 - 59)", explanation)
        self.assertIn("hour (0 - 23)", explanation)
        self.assertIn("day of the month (1 - 31)", explanation)
        self.assertIn("month (1 - 12)", explanation)
        self.assertIn("day of the week (0 - 6)", explanation)
    
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_generate_cron_documentation(self, mock_open, mock_makedirs):
        """Test generating cron documentation."""
        # Set up a test output file path
        output_file = os.path.join(self.temp_dir, "doc.md")
        
        # Call the method under test
        doc = self.scheduler.generate_cron_documentation(output_file=output_file)
        
        # Check that the result is a string with the expected content
        self.assertIsInstance(doc, str)
        self.assertIn("Cron Format Explanation", doc)
        self.assertIn("Common Schedules", doc)
        
        # Check that the output directory was created
        mock_makedirs.assert_called_once_with(self.temp_dir, exist_ok=True)
        
        # Check that the file was opened for writing
        mock_open.assert_called_once_with(output_file, "w")
    
    def test_get_scheduler(self):
        """Test the get_scheduler function."""
        # Call the function under test
        with patch('os.makedirs'):  # Mock os.makedirs to avoid actual directory creation
            scheduler = get_scheduler(
                script_path=self.test_script_path,
                log_dir=self.test_log_dir
            )
        
        # Check that the result is a Scheduler instance
        self.assertIsInstance(scheduler, Scheduler)
        
        # Check that the script path was set correctly
        self.assertEqual(scheduler.script_path, self.test_script_path)
        
        # Check that the log directory was set correctly
        self.assertEqual(scheduler.log_dir, self.test_log_dir)


if __name__ == "__main__":
    unittest.main()
