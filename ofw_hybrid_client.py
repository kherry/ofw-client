"""
Hybrid OFW Client - Can use either requests or browser automation
"""

from typing import Optional, Literal
import logging

# Import both clients
from ofw_client import OFWClient
from ofw_browser_client import OFWBrowserClient

logger = logging.getLogger(__name__)


class OFWHybridClient:
    """
    Hybrid client that can use either requests or browser automation.
    
    Automatically chooses the best method based on the task.
    """
    
    def __init__(self, mode: Literal['auto', 'requests', 'browser'] = 'auto', 
                 headless: bool = True, debug_screenshots: bool = False):
        """
        Initialize the hybrid client.
        
        Args:
            mode: 
                'auto' - Automatically choose best method (default)
                'requests' - Force use of requests library
                'browser' - Force use of browser automation
            headless: Run browser in headless mode (only for browser mode)
            debug_screenshots: Save debug screenshots (only for browser mode)
        """
        self.mode = mode
        self.headless = headless
        self.debug_screenshots = debug_screenshots
        
        self._requests_client: Optional[OFWClient] = None
        self._browser_client: Optional[OFWBrowserClient] = None
        self._current_mode: Optional[str] = None
        self.is_authenticated = False
    
    def login(self, username: str, password: str, force_browser: bool = False) -> bool:
        """
        Login to OFW using the most appropriate method.
        
        Args:
            username: OFW username/email
            password: OFW password
            force_browser: Force browser mode even if auto mode selected
            
        Returns:
            True if login successful
        """
        # Determine which mode to use
        use_browser = (
            self.mode == 'browser' or 
            force_browser or 
            (self.mode == 'auto' and self._should_use_browser())
        )
        
        if use_browser:
            logger.info("Using browser mode for login")
            return self._login_with_browser(username, password)
        else:
            logger.info("Using requests mode for login")
            return self._login_with_requests(username, password)
    
    def _should_use_browser(self) -> bool:
        """
        Determine if browser should be used in auto mode.
        
        For OFW, we default to browser since it's JavaScript-heavy.
        You can modify this logic based on your needs.
        """
        # For OFW, always prefer browser in auto mode
        # since the site is JavaScript-heavy
        return True
    
    def _login_with_requests(self, username: str, password: str) -> bool:
        """Login using requests library."""
        if not self._requests_client:
            self._requests_client = OFWClient()
        
        success = self._requests_client.login(username, password)
        if success:
            self.is_authenticated = True
            self._current_mode = 'requests'
        
        return success
    
    def _login_with_browser(self, username: str, password: str) -> bool:
        """Login using browser automation."""
        if not self._browser_client:
            self._browser_client = OFWBrowserClient(
                headless=self.headless,
                debug_screenshots=self.debug_screenshots
            )
        
        success = self._browser_client.login(username, password)
        if success:
            self.is_authenticated = True
            self._current_mode = 'browser'
        
        return success
    
    def get_session_info(self):
        """Get session information from active client."""
        if self._current_mode == 'requests' and self._requests_client:
            return self._requests_client.get_session_info()
        elif self._current_mode == 'browser' and self._browser_client:
            return self._browser_client.get_session_info()
        else:
            return {'authenticated': False, 'mode': None}
    
    def navigate_to(self, url: str):
        """Navigate to a URL (browser mode only)."""
        if self._current_mode == 'browser' and self._browser_client:
            return self._browser_client.navigate_to(url)
        else:
            logger.warning("navigate_to() only works in browser mode")
            return False
    
    def get_page_source(self) -> str:
        """Get current page source."""
        if self._current_mode == 'browser' and self._browser_client:
            return self._browser_client.get_page_source()
        else:
            logger.warning("get_page_source() works best in browser mode")
            return ""
    
    def execute_script(self, script: str):
        """Execute JavaScript (browser mode only)."""
        if self._current_mode == 'browser' and self._browser_client:
            return self._browser_client.execute_script(script)
        else:
            logger.warning("execute_script() only works in browser mode")
            return None
    
    def get_cookies(self):
        """Get cookies from active client."""
        if self._current_mode == 'requests' and self._requests_client:
            return dict(self._requests_client.session.cookies)
        elif self._current_mode == 'browser' and self._browser_client:
            return self._browser_client.get_cookies()
        else:
            return {}
    
    def get_local_storage(self):
        """Get localStorage (browser mode only)."""
        if self._current_mode == 'browser' and self._browser_client:
            return self._browser_client.get_local_storage()
        else:
            logger.warning("get_local_storage() only works in browser mode")
            return {}
    
    def get_session_storage(self):
        """Get sessionStorage (browser mode only)."""
        if self._current_mode == 'browser' and self._browser_client:
            return self._browser_client.get_session_storage()
        else:
            logger.warning("get_session_storage() only works in browser mode")
            return {}
    
    def logout(self):
        """Logout from active client."""
        if self._requests_client:
            self._requests_client.logout()
        
        if self._browser_client:
            self._browser_client.logout()
        
        self.is_authenticated = False
        self._current_mode = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.logout()
    
    def __del__(self):
        """Destructor."""
        self.logout()


# Convenience function
def create_client(use_browser: bool = True, headless: bool = True, 
                  debug_screenshots: bool = False):
    """
    Convenience function to create the appropriate client.
    
    Args:
        use_browser: Use browser automation (True) or requests (False)
        headless: Run browser in headless mode
        debug_screenshots: Save debug screenshots
    
    Returns:
        OFWBrowserClient or OFWClient
    """
    if use_browser:
        return OFWBrowserClient(headless=headless, debug_screenshots=debug_screenshots)
    else:
        return OFWClient()


# Example usage
if __name__ == "__main__":
    from getpass import getpass
    
    print("Choose mode:")
    print("1. Browser (recommended for OFW)")
    print("2. Requests")
    print("3. Auto (will choose browser)")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    mode_map = {'1': 'browser', '2': 'requests', '3': 'auto'}
    mode = mode_map.get(choice, 'auto')
    
    username = input("Username: ")
    password = getpass("Password: ")
    
    with OFWHybridClient(mode=mode, headless=True, debug_screenshots=True) as client:
        if client.login(username, password):
            print(f"\n✓ Logged in using {client._current_mode} mode")
            
            session_info = client.get_session_info()
            print(f"✓ Session info retrieved")
            
            if client._current_mode == 'browser':
                print(f"✓ LocalStorage keys: {list(client.get_local_storage().keys())}")
            
            input("\nPress Enter to logout...")
        else:
            print("\n✗ Login failed")
