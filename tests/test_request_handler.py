"""
Tests for the RequestHandler class.
"""

import unittest
from unittest import mock
import requests
import time

# Try both import paths to handle different execution contexts
try:
    from src.http_client.request_handler import RequestHandler
except ModuleNotFoundError:
    from http_client.request_handler import RequestHandler


class TestRequestHandler(unittest.TestCase):
    """Tests for the RequestHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
        self.timeout = 10
        self.max_retries = 2
        self.delay = 0.01  # Small delay for testing
        
        # Create a request handler with test settings
        self.handler = RequestHandler(
            user_agents=self.user_agents,
            timeout=self.timeout,
            max_retries=self.max_retries,
            delay=self.delay,
            respect_robots_txt=False  # Disable robots.txt for testing
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.handler.close()
    
    def test_init(self):
        """Test initialization of RequestHandler."""
        # Check that the session was created
        self.assertIsInstance(self.handler.session, requests.Session)
        
        # Check that user agents were set
        self.assertEqual(self.handler.user_agents, self.user_agents)
        
        # Check that timeout was set
        self.assertEqual(self.handler.timeout, self.timeout)
        
        # Check that max retries was set
        self.assertEqual(self.handler.max_retries, self.max_retries)
        
        # Check that delay was set
        self.assertEqual(self.handler.delay, self.delay)
        
        # Check that respect_robots_txt was set
        self.assertEqual(self.handler.respect_robots_txt, False)
    
    def test_rotate_user_agent(self):
        """Test rotation of User-Agent header."""
        # Get the initial User-Agent
        initial_user_agent = self.handler.session.headers.get("User-Agent")
        
        # Call _rotate_user_agent multiple times and check that the User-Agent changes
        user_agents_seen = set()
        for _ in range(10):  # Try multiple times to increase chance of seeing different User-Agents
            self.handler._rotate_user_agent()
            current_user_agent = self.handler.session.headers.get("User-Agent")
            user_agents_seen.add(current_user_agent)
        
        # Check that we saw at least one User-Agent
        self.assertGreater(len(user_agents_seen), 0)
        
        # Check that all User-Agents seen are in the list
        for user_agent in user_agents_seen:
            self.assertIn(user_agent, self.user_agents)
    
    @mock.patch("requests.Session.request")
    def test_get(self, mock_request):
        """Test the get method."""
        # Set up the mock
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        # Call the get method
        with mock.patch.object(self.handler, "_add_delay") as mock_add_delay:
            with mock.patch.object(self.handler, "_rotate_user_agent") as mock_rotate_user_agent:
                response = self.handler.get("https://example.com")
        
        # Check that the request was made with the correct arguments
        mock_request.assert_called_once_with(
            "GET",
            "https://example.com",
            timeout=self.timeout
        )
        
        # Check that _add_delay was called
        mock_add_delay.assert_called_once()
        
        # Check that _rotate_user_agent was called
        mock_rotate_user_agent.assert_called_once()
        
        # Check that the response was returned
        self.assertEqual(response, mock_response)
    
    @mock.patch("requests.Session.request")
    def test_post(self, mock_request):
        """Test the post method."""
        # Set up the mock
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        # Call the post method with data
        data = {"username": "test", "password": "test"}
        with mock.patch.object(self.handler, "_add_delay"):
            with mock.patch.object(self.handler, "_rotate_user_agent"):
                response = self.handler.post("https://example.com/login", data=data)
        
        # Check that the request was made with the correct arguments
        mock_request.assert_called_once_with(
            "POST",
            "https://example.com/login",
            data=data,
            timeout=self.timeout
        )
        
        # Check that the response was returned
        self.assertEqual(response, mock_response)
    
    @mock.patch("requests.Session.request")
    def test_request_with_timeout(self, mock_request):
        """Test the _request method with a custom timeout."""
        # Set up the mock
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        # Call the get method with a custom timeout
        with mock.patch.object(self.handler, "_add_delay"):
            with mock.patch.object(self.handler, "_rotate_user_agent"):
                response = self.handler.get("https://example.com", timeout=20)
        
        # Check that the request was made with the custom timeout
        mock_request.assert_called_once_with(
            "GET",
            "https://example.com",
            timeout=20
        )
    
    @mock.patch("requests.Session.request")
    def test_request_with_retry(self, mock_request):
        """Test the _request method with retries."""
        # Set up the mock to raise an exception and then succeed
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_request.side_effect = [
            requests.exceptions.RequestException("Connection error"),
            mock_response
        ]
        
        # Call the get method
        with mock.patch.object(self.handler, "_add_delay"):
            with mock.patch.object(self.handler, "_rotate_user_agent"):
                response = self.handler.get("https://example.com")
        
        # Check that the request was made twice
        self.assertEqual(mock_request.call_count, 2)
        
        # Check that the response was returned
        self.assertEqual(response, mock_response)
    
    @mock.patch("requests.Session.request")
    def test_request_with_max_retries_exceeded(self, mock_request):
        """Test the _request method with max retries exceeded."""
        # Set up the mock to always raise an exception
        mock_request.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Call the get method and check that it raises an exception
        with mock.patch.object(self.handler, "_add_delay"):
            with mock.patch.object(self.handler, "_rotate_user_agent"):
                with self.assertRaises(requests.exceptions.RequestException):
                    self.handler.get("https://example.com")
        
        # Check that the request was made max_retries + 1 times
        self.assertEqual(mock_request.call_count, self.max_retries + 1)
    
    @mock.patch("time.sleep")
    def test_add_delay(self, mock_sleep):
        """Test the _add_delay method."""
        # Call _add_delay
        self.handler._add_delay()
        
        # Check that time.sleep was called
        mock_sleep.assert_called_once()
        
        # Check that the sleep time is based on self.delay
        sleep_time = mock_sleep.call_args[0][0]
        self.assertGreaterEqual(sleep_time, self.delay * 0.8)
        self.assertLessEqual(sleep_time, self.delay * 1.2)
    
    @mock.patch("requests.get")
    def test_check_robots_txt_disabled(self, mock_get):
        """Test the _check_robots_txt method when disabled."""
        # Set respect_robots_txt to False
        self.handler.respect_robots_txt = False
        
        # Call _check_robots_txt
        result = self.handler._check_robots_txt("https://example.com/page")
        
        # Check that the result is True
        self.assertTrue(result)
        
        # Check that requests.get was not called
        mock_get.assert_not_called()
    
    @mock.patch("requests.get")
    def test_check_robots_txt_enabled(self, mock_get):
        """Test the _check_robots_txt method when enabled."""
        # Set respect_robots_txt to True
        self.handler.respect_robots_txt = True
        
        # Set up the mock
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        User-agent: *
        Disallow: /private/
        Allow: /
        """
        mock_get.return_value = mock_response
        
        # Call _check_robots_txt for an allowed URL
        result = self.handler._check_robots_txt("https://example.com/page")
        
        # Check that the result is True
        self.assertTrue(result)
        
        # Check that requests.get was called with the robots.txt URL
        mock_get.assert_called_once_with("https://example.com/robots.txt", timeout=self.timeout)
        
        # Call _check_robots_txt for a disallowed URL
        result = self.handler._check_robots_txt("https://example.com/private/page")
        
        # Check that the result is False
        self.assertFalse(result)
    
    def test_context_manager(self):
        """Test the context manager interface."""
        # Use the handler as a context manager
        with self.handler as handler:
            # Check that the handler is the same
            self.assertEqual(handler, self.handler)
            
            # Check that the session is still active
            self.assertFalse(self.handler.session.closed if hasattr(self.handler.session, 'closed') else False)
        
        # Mock the close method to check if it was called
        with mock.patch.object(self.handler, 'close') as mock_close:
            with self.handler:
                pass
            mock_close.assert_called_once()
    
if __name__ == "__main__":
    unittest.main()
