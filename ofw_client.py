"""
Our Family Wizard Python Client
A Python library for interacting with the Our Family Wizard co-parenting app.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OFWClient:
    """Client for interacting with Our Family Wizard."""
    
    BASE_URL = "https://ofw.ourfamilywizard.com"
    LOGIN_URL = f"{BASE_URL}/app/login"
    
    def __init__(self):
        """Initialize the OFW client with a requests session."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.is_authenticated = False
        self._session_id = None
        self._csrf_token = None
        
    def _initialize_session(self) -> bool:
        """
        Initialize session by calling localstorage.json endpoint first.
        This sets the required cookies before accessing the login page.
        
        Returns:
            True if session initialized successfully
        """
        logger.info("Initializing session via localstorage.json...")
        localstorage_url = f"{self.BASE_URL}/ofw/appv2/localstorage.json"
        
        try:
            response = self.session.get(localstorage_url)
            response.raise_for_status()
            
            # Extract cookies after localstorage call
            cookies = dict(self.session.cookies)
            logger.info(f"Cookies received from localstorage.json: {list(cookies.keys())}")
            
            # Store session ID if present
            for cookie_name in ['JSESSIONID', 'sessionid', 'session', 'sid']:
                if cookie_name in cookies:
                    self._session_id = cookies[cookie_name]
                    logger.info(f"Session ID captured from {cookie_name}: {self._session_id[:20]}...")
                    break
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            return False
    
    def _get_login_page(self) -> requests.Response:
        """
        Fetch the login page to extract session ID and CSRF token.
        
        Returns:
            requests.Response: The response from the login page
        """
        logger.info("Fetching login page...")
        response = self.session.get(self.LOGIN_URL)
        response.raise_for_status()
        
        # Extract cookies (session ID) - they should already be set from _initialize_session
        cookies = dict(self.session.cookies)
        logger.info(f"Cookies after login page fetch: {list(cookies.keys())}")
        
        # Update session ID if we got a new one
        if not self._session_id:
            for cookie_name in ['JSESSIONID', 'sessionid', 'session', 'sid']:
                if cookie_name in cookies:
                    self._session_id = cookies[cookie_name]
                    logger.info(f"Session ID captured from {cookie_name}: {self._session_id[:20]}...")
                    break
        
        return response
    
    def _extract_csrf_token(self, html_content: str) -> Optional[str]:
        """
        Extract CSRF token from the login page HTML.
        
        Args:
            html_content: The HTML content of the login page
            
        Returns:
            The CSRF token if found, None otherwise
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Common CSRF token locations
        # 1. Hidden input field
        csrf_input = soup.find('input', {'name': re.compile(r'csrf|_token|authenticity_token', re.I)})
        if csrf_input and csrf_input.get('value'):
            logger.info("CSRF token found in hidden input field")
            return csrf_input['value']
        
        # 2. Meta tag
        csrf_meta = soup.find('meta', {'name': re.compile(r'csrf-token', re.I)})
        if csrf_meta and csrf_meta.get('content'):
            logger.info("CSRF token found in meta tag")
            return csrf_meta['content']
        
        # 3. Script tag with token
        for script in soup.find_all('script'):
            if script.string:
                match = re.search(r'csrfToken["\s:=]+(["\'])([\w-]+)\1', script.string)
                if match:
                    logger.info("CSRF token found in script tag")
                    return match.group(2)
        
        logger.warning("No CSRF token found")
        return None
    
    def _extract_form_data(self, html_content: str) -> Dict[str, str]:
        """
        Extract all hidden form fields from the login page.
        
        Args:
            html_content: The HTML content of the login page
            
        Returns:
            Dictionary of form field names and values
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        form_data = {}
        
        # Find the login form
        login_form = soup.find('form', {'id': re.compile(r'login', re.I)}) or \
                     soup.find('form', {'action': re.compile(r'login|signin|auth', re.I)}) or \
                     soup.find('form')
        
        if login_form:
            # Extract all hidden inputs
            for input_field in login_form.find_all('input', {'type': 'hidden'}):
                name = input_field.get('name')
                value = input_field.get('value', '')
                if name:
                    form_data[name] = value
                    logger.debug(f"Found hidden field: {name}")
        
        return form_data
    
    def login(self, username: str, password: str) -> bool:
        """
        Login to Our Family Wizard.
        
        Args:
            username: Your OFW username/email
            password: Your OFW password
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            # Step 1: Initialize session by calling localstorage.json
            if not self._initialize_session():
                logger.error("Failed to initialize session")
                return False
            
            # Step 2: Get the login page and capture session/tokens
            response = self._get_login_page()
            
            # Step 3: Extract CSRF token and other form data
            self._csrf_token = self._extract_csrf_token(response.text)
            hidden_fields = self._extract_form_data(response.text)
            
            # Step 4: Prepare login payload with correct field names
            login_data = {
                'submit': 'Sign-In',
                '_eventId': 'submit',
                'username': username,
                'password': password,
                **hidden_fields  # Include any other hidden fields
            }
            
            # Add CSRF token if found (with common field names)
            if self._csrf_token:
                login_data['csrf_token'] = self._csrf_token
                login_data['_csrf'] = self._csrf_token
                login_data['authenticity_token'] = self._csrf_token
            
            logger.info("Submitting login credentials...")
            logger.debug(f"Login data fields: {list(login_data.keys())}")
            
            # Step 5: Submit login form - allow redirects to follow the chain
            # /app/login -> /ofw/home.form -> /ofw/appv2/home.form
            login_response = self.session.post(
                self.LOGIN_URL,
                data=login_data,
                allow_redirects=True  # Follow all redirects
            )
            
            # Step 6: Check if login was successful
            # Success indicators based on the redirect chain you described
            # Note: Redirects might be handled by JavaScript, so we also check page content
            
            logger.info(f"Login POST status: {login_response.status_code}")
            logger.info(f"Final URL after redirects: {login_response.url}")
            logger.info(f"Redirect history: {[r.url for r in login_response.history]}")
            
            # Log cookies after login
            logger.info(f"Cookies after login: {list(self.session.cookies.keys())}")
            
            # Parse the final page to check for authenticated elements
            soup = BeautifulSoup(login_response.text, 'html.parser')
            
            # Check for elements that indicate successful login
            greeting_div = soup.find('div', {'id': 'greeting'})
            notifications_div = soup.find('div', {'id': 'notificationsSection'})
            
            has_greeting = greeting_div is not None
            has_notifications = notifications_div is not None
            
            logger.info(f"Page elements found: greeting={has_greeting}, notifications={has_notifications}")
            
            # Check for error messages
            error_div = soup.find('div', {'class': re.compile(r'error|alert-danger', re.I)})
            
            if error_div:
                logger.error(f"Login error: {error_div.get_text(strip=True)}")
                return False
            
            # Success if we found both required elements
            if has_greeting and has_notifications:
                self.is_authenticated = True
                logger.info("✓ Login successful!")
                logger.info("✓ Found greeting and notificationsSection divs")
                logger.info(f"Final URL: {login_response.url}")
                
                # Step 7: Call localstorage.json again (as observed in browser)
                # This is called asynchronously after landing on home page
                logger.info("Calling localstorage.json again (post-login)...")
                localstorage_url = f"{self.BASE_URL}/ofw/appv2/localstorage.json"
                localstorage_response = self.session.get(localstorage_url)
                
                logger.info(f"Localstorage.json status: {localstorage_response.status_code}")
                try:
                    localstorage_data = localstorage_response.json()
                    logger.info(f"Localstorage.json response: {localstorage_data}")
                except:
                    logger.info(f"Localstorage.json response (text): {localstorage_response.text[:200]}")
                
                return True
            else:
                logger.warning("Login may have failed - required page elements not found")
                logger.warning(f"Expected: div#greeting and div#notificationsSection")
                logger.warning(f"Found: greeting={has_greeting}, notifications={has_notifications}")
                
                # Log what divs we did find
                all_divs_with_ids = soup.find_all('div', id=True)
                div_ids = [div.get('id') for div in all_divs_with_ids[:20]]  # First 20
                logger.info(f"Div IDs found on page: {div_ids}")
                
                logger.debug(f"Final URL: {login_response.url}")
                logger.debug(f"Response status: {login_response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during login: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get current session information.
        
        Returns:
            Dictionary containing session details
        """
        return {
            'authenticated': self.is_authenticated,
            'session_id': self._session_id,
            'csrf_token': self._csrf_token[:20] + '...' if self._csrf_token else None,
            'cookies': dict(self.session.cookies)
        }
    
    def logout(self):
        """Logout and clear session."""
        try:
            logout_url = f"{self.BASE_URL}/app/logout"
            self.session.get(logout_url)
        except:
            pass
        finally:
            self.session.cookies.clear()
            self.is_authenticated = False
            self._session_id = None
            self._csrf_token = None
            logger.info("Logged out and session cleared")
