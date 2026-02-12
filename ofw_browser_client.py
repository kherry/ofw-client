"""
Our Family Wizard Browser Client (Headless)
Uses Selenium with headless Chrome to handle JavaScript-heavy pages
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import time
import json
from typing import Optional, Dict, Any
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OFWBrowserClient:
    """Client for interacting with Our Family Wizard using a headless browser."""
    
    BASE_URL = "https://ofw.ourfamilywizard.com"
    LOGIN_URL = f"{BASE_URL}/app/login"
    
    def __init__(self, headless: bool = True, debug_screenshots: bool = False):
        """
        Initialize the OFW browser client.
        
        Args:
            headless: Run browser in headless mode (no GUI)
            debug_screenshots: Save screenshots during login process
        """
        self.headless = headless
        self.debug_screenshots = debug_screenshots
        self.driver: Optional[webdriver.Chrome] = None
        self.is_authenticated = False
        
        # Create debug directory
        self.debug_dir = "debug"
        os.makedirs(self.debug_dir, exist_ok=True)
    
    def _setup_driver(self):
        """Set up Chrome driver with appropriate options."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        # Standard Chrome options for compatibility
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # User agent to appear as a normal browser
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Disable automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        logger.info("Initializing Chrome driver...")
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Remove webdriver property to avoid detection
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Set timeouts
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(30)
        
        logger.info("Chrome driver initialized")
    
    def _take_screenshot(self, name: str):
        """Take a screenshot if debug mode is enabled."""
        if self.debug_screenshots and self.driver:
            filepath = os.path.join(self.debug_dir, f"{name}.png")
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved: {filepath}")
    
    def _save_page_source(self, name: str):
        """Save the current page source."""
        if self.driver:
            filepath = os.path.join(self.debug_dir, f"{name}.html")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            logger.info(f"Page source saved: {filepath}")
    
    def _wait_for_page_load(self, timeout: int = 10):
        """Wait for page to fully load including JavaScript."""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            # Additional wait for any async JavaScript
            time.sleep(1)
        except TimeoutException:
            logger.warning("Page load timeout - continuing anyway")
    
    def login(self, username: str, password: str) -> bool:
        """
        Login to Our Family Wizard using headless browser.
        
        Args:
            username: Your OFW username/email
            password: Your OFW password
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            # Step 1: Set up the browser
            if not self.driver:
                self._setup_driver()
            
            logger.info("Step 1: Navigating to login page...")
            
            # Step 2: Navigate to login page (this will trigger localstorage.json calls)
            self.driver.get(self.LOGIN_URL)
            self._wait_for_page_load()
            
            self._take_screenshot("01_login_page_loaded")
            self._save_page_source("01_login_page")
            
            logger.info(f"Current URL: {self.driver.current_url}")
            logger.info("Step 2: Waiting for login form to be ready...")
            
            # Step 3: Wait for login form elements to be present
            try:
                # Wait for username field
                username_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                logger.info("✓ Username field found")
                
                # Wait for password field
                password_field = self.driver.find_element(By.NAME, "password")
                logger.info("✓ Password field found")
                
                # Look for submit button
                submit_button = None
                try:
                    # Try different selectors for submit button
                    submit_button = self.driver.find_element(By.NAME, "submit")
                except NoSuchElementException:
                    try:
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                    except NoSuchElementException:
                        try:
                            submit_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                        except NoSuchElementException:
                            # Last resort - find any submit button
                            submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign')]")
                
                if submit_button:
                    logger.info("✓ Submit button found")
                
            except TimeoutException:
                logger.error("Login form elements not found")
                self._take_screenshot("error_form_not_found")
                self._save_page_source("error_form_not_found")
                return False
            
            # Step 4: Fill in credentials
            logger.info("Step 3: Filling in credentials...")
            username_field.clear()
            username_field.send_keys(username)
            logger.info("✓ Username entered")
            
            password_field.clear()
            password_field.send_keys(password)
            logger.info("✓ Password entered")
            
            self._take_screenshot("02_credentials_entered")
            
            # Step 5: Submit the form
            logger.info("Step 4: Submitting login form...")
            
            # Option 1: Click the submit button
            if submit_button:
                submit_button.click()
            else:
                # Option 2: Submit the form via JavaScript
                self.driver.execute_script("document.querySelector('form').submit();")
            
            logger.info("✓ Form submitted")
            
            # Step 6: Wait for redirect and page load
            logger.info("Step 5: Waiting for authentication...")
            time.sleep(2)  # Give it a moment for any initial redirects/JS
            
            # Wait for the authenticated page to load
            # The redirects might be handled by JavaScript, so we check for page elements
            # instead of relying on URL
            max_wait = 15
            start_time = time.time()
            login_successful = False
            
            logger.info("Looking for authenticated page elements...")
            
            while time.time() - start_time < max_wait:
                try:
                    # Check for elements that indicate successful login
                    # Look for 'greeting' div and 'notificationsSection' div
                    greeting_present = len(self.driver.find_elements(By.ID, "greeting")) > 0
                    notifications_present = len(self.driver.find_elements(By.ID, "notificationsSection")) > 0
                    
                    if greeting_present and notifications_present:
                        logger.info("✓ Found greeting div")
                        logger.info("✓ Found notificationsSection div")
                        login_successful = True
                        break
                    
                    # Also check if we're still on login page with error
                    if 'login' in self.driver.current_url.lower():
                        # Check for error messages
                        error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".error, .alert-danger, [class*='error']")
                        if error_elements and time.time() - start_time > 5:
                            error_text = error_elements[0].text
                            if error_text:
                                logger.error(f"Login error: {error_text}")
                                self._take_screenshot("03_login_error")
                                self._save_page_source("03_login_error")
                                return False
                    
                    # Log current state
                    logger.debug(f"Waiting... greeting={greeting_present}, notifications={notifications_present}, url={self.driver.current_url}")
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.debug(f"Exception while checking elements: {e}")
                    time.sleep(0.5)
            
            # Wait for page to fully load
            self._wait_for_page_load()
            self._take_screenshot("04_after_login")
            self._save_page_source("04_after_login")
            
            # Step 7: Verify successful login
            final_url = self.driver.current_url
            logger.info(f"Final URL: {final_url}")
            
            if login_successful:
                self.is_authenticated = True
                logger.info("✓✓✓ LOGIN SUCCESSFUL! ✓✓✓")
                logger.info("✓ Authenticated page loaded with greeting and notifications sections")
                
                # Save cookies for potential reuse
                self._save_cookies()
                
                # Wait for any async JavaScript to complete (like localstorage.json fetch)
                time.sleep(2)
                
                return True
            else:
                logger.warning("Login may have failed - required elements not found")
                logger.warning("Expected to find: div#greeting and div#notificationsSection")
                self._take_screenshot("05_elements_not_found")
                self._save_page_source("05_elements_not_found")
                
                # Log what we did find
                try:
                    all_divs = self.driver.find_elements(By.TAG_NAME, "div")
                    div_ids = [div.get_attribute('id') for div in all_divs if div.get_attribute('id')]
                    logger.info(f"Div IDs found on page: {div_ids[:20]}")  # First 20
                except:
                    pass
                
                return False
                
        except Exception as e:
            logger.error(f"Error during login: {e}")
            import traceback
            traceback.print_exc()
            
            if self.driver:
                self._take_screenshot("error_exception")
                self._save_page_source("error_exception")
            
            return False
    
    def _save_cookies(self):
        """Save browser cookies to file."""
        if self.driver:
            cookies = self.driver.get_cookies()
            filepath = os.path.join(self.debug_dir, "cookies.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2)
            logger.info(f"Cookies saved: {filepath}")
    
    def get_cookies(self) -> list:
        """Get current browser cookies."""
        if self.driver:
            return self.driver.get_cookies()
        return []
    
    def get_local_storage(self) -> dict:
        """Get localStorage data from the browser."""
        if self.driver and self.is_authenticated:
            try:
                local_storage = self.driver.execute_script(
                    "return Object.entries(localStorage).reduce((acc, [key, value]) => ({...acc, [key]: value}), {});"
                )
                
                logger.debug(f"Raw localStorage from browser: {local_storage}")
                
                # Parse any values that are JSON-encoded strings
                # (localStorage stores everything as strings, so "token" becomes "\"token\"")
                cleaned_storage = {}
                for key, value in local_storage.items():
                    logger.debug(f"Processing key '{key}': type={type(value)}, value={repr(value)[:100]}")
                    
                    # If value is a string and looks like it might be JSON, try to parse it
                    if isinstance(value, str):
                        try:
                            # Try to parse as JSON - if it's a JSON-encoded string, unwrap it
                            parsed = json.loads(value)
                            logger.debug(f"  -> Parsed as JSON: type={type(parsed)}, value={repr(parsed)[:100]}")
                            cleaned_storage[key] = parsed
                        except (json.JSONDecodeError, TypeError):
                            # Not JSON or not a string - use as-is
                            logger.debug(f"  -> Not JSON, using as-is")
                            cleaned_storage[key] = value
                    else:
                        # Not a string - use as-is
                        cleaned_storage[key] = value
                
                # Save to file
                filepath = os.path.join(self.debug_dir, "localstorage_data.json")
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(cleaned_storage, f, indent=2)
                logger.info(f"LocalStorage saved: {filepath}")
                
                return cleaned_storage
            except Exception as e:
                logger.error(f"Error getting localStorage: {e}")
                import traceback
                traceback.print_exc()
                return {}
        return {}
    
    def get_session_storage(self) -> dict:
        """Get sessionStorage data from the browser."""
        if self.driver and self.is_authenticated:
            try:
                session_storage = self.driver.execute_script(
                    "return Object.entries(sessionStorage).reduce((acc, [key, value]) => ({...acc, [key]: value}), {});"
                )
                
                # Parse any values that are JSON-encoded strings
                cleaned_storage = {}
                for key, value in session_storage.items():
                    try:
                        # Try to parse as JSON - if it's a JSON-encoded string, unwrap it
                        parsed = json.loads(value)
                        cleaned_storage[key] = parsed
                    except (json.JSONDecodeError, TypeError):
                        # Not JSON or not a string - use as-is
                        cleaned_storage[key] = value
                
                # Save to file
                filepath = os.path.join(self.debug_dir, "sessionstorage_data.json")
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(cleaned_storage, f, indent=2)
                logger.info(f"SessionStorage saved: {filepath}")
                
                return cleaned_storage
            except Exception as e:
                logger.error(f"Error getting sessionStorage: {e}")
                return {}
        return {}
    
    def navigate_to(self, url: str):
        """Navigate to a URL while authenticated."""
        if not self.is_authenticated:
            logger.warning("Not authenticated - login first")
            return False
        
        try:
            self.driver.get(url)
            self._wait_for_page_load()
            return True
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return False
    
    def get_page_source(self) -> str:
        """Get current page HTML source."""
        if self.driver:
            return self.driver.page_source
        return ""
    
    def execute_script(self, script: str):
        """Execute JavaScript in the browser."""
        if self.driver:
            return self.driver.execute_script(script)
        return None
    
    def find_element(self, by: By, value: str):
        """Find an element on the page."""
        if self.driver:
            return self.driver.find_element(by, value)
        return None
    
    def find_elements(self, by: By, value: str):
        """Find elements on the page."""
        if self.driver:
            return self.driver.find_elements(by, value)
        return []
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get comprehensive session information."""
        if not self.driver:
            return {'authenticated': False, 'error': 'Driver not initialized'}
        
        info = {
            'authenticated': self.is_authenticated,
            'current_url': self.driver.current_url,
            'cookies': self.get_cookies(),
        }
        
        if self.is_authenticated:
            info['localStorage'] = self.get_local_storage()
            info['sessionStorage'] = self.get_session_storage()
        
        return info
    
    def logout(self):
        """Logout and close browser."""
        if self.driver:
            try:
                # Try to navigate to logout URL
                logout_url = f"{self.BASE_URL}/app/logout"
                self.driver.get(logout_url)
                time.sleep(1)
            except:
                pass
            finally:
                logger.info("Closing browser...")
                self.driver.quit()
                self.driver = None
                self.is_authenticated = False
                logger.info("Browser closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures browser is closed."""
        self.logout()
    
    def __del__(self):
        """Destructor - ensures browser is closed."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
