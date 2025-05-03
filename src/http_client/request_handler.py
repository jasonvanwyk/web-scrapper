"""
HTTP request handler module.

This module provides a RequestHandler class that wraps around requests.Session
to handle HTTP requests with retry logic, User-Agent rotation, and timeout handling.
"""

import logging
import random
import time
from typing import Dict, List, Optional, Union, Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from urllib.robotparser import RobotFileParser

# Try both import paths to handle different execution contexts
try:
    from src.config import config
except ModuleNotFoundError:
    from config import config


class RequestHandler:
    """
    Handler for HTTP requests with retry logic and User-Agent rotation.
    
    This class wraps around requests.Session to provide additional functionality
    such as retry logic, User-Agent rotation, and timeout handling.
    
    Attributes:
        session: A requests.Session instance for making HTTP requests.
        user_agents: A list of User-Agent strings to rotate through.
        timeout: Timeout for HTTP requests in seconds.
        max_retries: Maximum number of retries for failed HTTP requests.
        delay: Delay between HTTP requests in seconds.
        respect_robots_txt: Whether to respect robots.txt directives.
        robots_cache: Cache of parsed robots.txt files.
        logger: A logger instance for the handler.
    """
    
    # Default list of common User-Agent strings
    DEFAULT_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"
    ]
    
    def __init__(
        self,
        user_agents: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        delay: Optional[float] = None,
        respect_robots_txt: Optional[bool] = None,
        proxies: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the request handler.
        
        Args:
            user_agents: List of User-Agent strings to rotate through.
                         If None, uses DEFAULT_USER_AGENTS.
            timeout: Timeout for HTTP requests in seconds.
                     If None, uses config.scraping.request_timeout.
            max_retries: Maximum number of retries for failed HTTP requests.
                         If None, uses config.scraping.request_retries.
            delay: Delay between HTTP requests in seconds.
                   If None, uses config.scraping.request_delay.
            respect_robots_txt: Whether to respect robots.txt directives.
                               If None, uses config.scraping.respect_robots_txt.
            proxies: Optional dictionary mapping protocol to proxy URL.
        """
        self.session = requests.Session()
        self.user_agents = user_agents or self.DEFAULT_USER_AGENTS
        self.timeout = timeout or config.scraping.request_timeout
        self.max_retries = max_retries or config.scraping.request_retries
        self.delay = delay or config.scraping.request_delay
        self.respect_robots_txt = respect_robots_txt if respect_robots_txt is not None else config.scraping.respect_robots_txt
        self.robots_cache = {}  # Cache for parsed robots.txt files
        
        # Set up proxies if provided
        if proxies:
            self.session.proxies.update(proxies)
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Set a default User-Agent
        self._rotate_user_agent()
    
    def _rotate_user_agent(self) -> None:
        """
        Rotate the User-Agent header to a random one from the list.
        """
        user_agent = random.choice(self.user_agents)
        self.session.headers.update({"User-Agent": user_agent})
        self.logger.debug(f"Rotated User-Agent to: {user_agent}")
    
    def _check_robots_txt(self, url: str) -> bool:
        """
        Check if the URL is allowed by robots.txt.
        
        Args:
            url: The URL to check.
            
        Returns:
            bool: True if the URL is allowed, False otherwise.
        """
        if not self.respect_robots_txt:
            return True
        
        # Parse the URL to get the base URL for robots.txt
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = f"{base_url}/robots.txt"
        
        # Check if we've already parsed this robots.txt
        if base_url not in self.robots_cache:
            try:
                # Fetch and parse robots.txt
                self.logger.debug(f"Fetching robots.txt from {robots_url}")
                rp = RobotFileParser()
                rp.set_url(robots_url)
                
                # Use a simple GET request without our retry logic to avoid recursion
                response = requests.get(robots_url, timeout=self.timeout)
                if response.status_code == 200:
                    rp.parse(response.text.splitlines())
                else:
                    self.logger.warning(f"Failed to fetch robots.txt from {robots_url}: {response.status_code}")
                    # If we can't fetch robots.txt, assume everything is allowed
                    return True
                
                self.robots_cache[base_url] = rp
            except Exception as e:
                self.logger.warning(f"Error parsing robots.txt from {robots_url}: {e}")
                # If there's an error, assume everything is allowed
                return True
        
        # Check if the URL is allowed
        user_agent = self.session.headers.get("User-Agent", "*")
        allowed = self.robots_cache[base_url].can_fetch(user_agent, url)
        if not allowed:
            self.logger.warning(f"URL {url} is disallowed by robots.txt")
        
        return allowed
    
    def _add_delay(self) -> None:
        """
        Add a delay between requests to be polite.
        """
        if self.delay > 0:
            # Add a small random variation to the delay
            actual_delay = self.delay * (0.8 + 0.4 * random.random())
            self.logger.debug(f"Sleeping for {actual_delay:.2f} seconds")
            time.sleep(actual_delay)
    
    @retry(
        stop=stop_after_attempt(3),  # Fixed value instead of lambda
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.HTTPError)),
        reraise=True
    )
    def _request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> requests.Response:
        """
        Make an HTTP request with retry logic.
        
        Args:
            method: HTTP method (e.g., "GET", "POST").
            url: URL to request.
            **kwargs: Additional keyword arguments to pass to requests.
            
        Returns:
            requests.Response: The response object.
            
        Raises:
            requests.exceptions.RequestException: If the request fails after all retries.
        """
        # Check robots.txt
        if not self._check_robots_txt(url):
            raise requests.exceptions.RequestException(f"URL {url} is disallowed by robots.txt")
        
        # Add delay before request
        self._add_delay()
        
        # Rotate User-Agent
        self._rotate_user_agent()
        
        # Set timeout if not provided in kwargs
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        
        # Make the request
        self.logger.debug(f"Making {method} request to {url}")
        response = self.session.request(method, url, **kwargs)
        
        # Raise an exception for 4XX and 5XX status codes
        response.raise_for_status()
        
        return response
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Make a GET request.
        
        Args:
            url: URL to request.
            **kwargs: Additional keyword arguments to pass to requests.
            
        Returns:
            requests.Response: The response object.
        """
        return self._request("GET", url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """
        Make a POST request.
        
        Args:
            url: URL to request.
            **kwargs: Additional keyword arguments to pass to requests.
            
        Returns:
            requests.Response: The response object.
        """
        return self._request("POST", url, **kwargs)
    
    def head(self, url: str, **kwargs) -> requests.Response:
        """
        Make a HEAD request.
        
        Args:
            url: URL to request.
            **kwargs: Additional keyword arguments to pass to requests.
            
        Returns:
            requests.Response: The response object.
        """
        return self._request("HEAD", url, **kwargs)
    
    def put(self, url: str, **kwargs) -> requests.Response:
        """
        Make a PUT request.
        
        Args:
            url: URL to request.
            **kwargs: Additional keyword arguments to pass to requests.
            
        Returns:
            requests.Response: The response object.
        """
        return self._request("PUT", url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> requests.Response:
        """
        Make a DELETE request.
        
        Args:
            url: URL to request.
            **kwargs: Additional keyword arguments to pass to requests.
            
        Returns:
            requests.Response: The response object.
        """
        return self._request("DELETE", url, **kwargs)
    
    def close(self) -> None:
        """
        Close the session.
        """
        self.session.close()
    
    def __enter__(self) -> "RequestHandler":
        """
        Enter the context manager.
        
        Returns:
            RequestHandler: The request handler instance.
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the context manager.
        
        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Exception traceback.
        """
        self.close()
