"""
OFW Messages Client
Uses auth token from localstorage.json to interact with the OFW API
"""

import requests
from typing import Optional, List, Dict, Any
import logging
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OFWMessagesClient:
    """Client for interacting with OFW messages using the API."""
    
    BASE_URL = "https://ofw.ourfamilywizard.com"
    API_BASE = f"{BASE_URL}/pub"
    TOKEN_CACHE_FILE = "debug/ofw_auth_token.json"
    
    def __init__(self, token_cache_file: Optional[str] = None):
        """
        Initialize the messages client.
        
        Args:
            token_cache_file: Path to cache auth token (default: debug/ofw_auth_token.json)
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Referer': f'{self.BASE_URL}/',
            'ofw-client': 'WebApplication',
            'ofw-version': '1.0.0',
        })
        self.is_authenticated = False
        self.auth_token = None
        self.token_cache_file = token_cache_file or self.TOKEN_CACHE_FILE
        
        # Ensure cache directory exists
        Path(self.token_cache_file).parent.mkdir(parents=True, exist_ok=True)
    
    def _get_auth_token_from_localstorage(self, browser_cookies: List[Dict[str, Any]]) -> Optional[str]:
        """
        Get the auth token from localstorage.json response.
        
        Args:
            browser_cookies: List of cookie dicts from browser
            
        Returns:
            Auth token from localstorage.json or None if failed
        """
        logger.info("Fetching auth token from localstorage.json...")
        
        # Load cookies into a temporary session
        temp_session = requests.Session()
        temp_session.headers.update(self.session.headers)
        
        for cookie in browser_cookies:
            temp_session.cookies.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie.get('domain', ''),
                path=cookie.get('path', '/'),
                secure=cookie.get('secure', False),
                expires=cookie.get('expiry')
            )
        
        # Get localstorage.json
        localstorage_url = f"{self.BASE_URL}/ofw/appv2/localstorage.json"
        
        try:
            response = temp_session.get(localstorage_url)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"localstorage.json response type: {type(data)}")
            logger.debug(f"localstorage.json keys: {list(data.keys())}")
            
            auth_token = data.get('auth')
            
            if not auth_token:
                logger.error("No 'auth' field in localstorage.json response")
                logger.debug(f"Response keys: {list(data.keys())}")
                return None
            
            logger.debug(f"Auth token from API: type={type(auth_token)}, value={repr(auth_token)[:100]}")
            logger.info("✓ Auth token retrieved from localstorage.json")
            logger.debug(f"Auth token (already base64): {auth_token[:30]}...")
            return auth_token
            
        except Exception as e:
            logger.error(f"Failed to get auth token from localstorage.json: {e}")
            return None
    
    def _set_auth_header(self, token: str):
        """
        Set the Authorization header with the auth token.
        
        Args:
            token: Auth token from localstorage.json (already base64 encoded)
        """
        # Auth token is already base64 encoded, use it directly
        self.session.headers['Authorization'] = f'Bearer {token}'
        logger.debug("Authorization header set")
    
    def _save_token_to_cache(self, token: str):
        """Save token to cache file."""
        try:
            logger.debug(f"Saving token to cache: type={type(token)}, value={repr(token)[:100]}")
            
            cache_data = {
                'token': token
            }
            
            with open(self.token_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"✓ Token cached to: {self.token_cache_file}")
            
            # Verify what was written
            with open(self.token_cache_file, 'r') as f:
                saved = json.load(f)
            logger.debug(f"Verified saved token: {repr(saved.get('token'))[:100]}")
            
        except Exception as e:
            logger.warning(f"Could not save token to cache: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_token_from_cache(self) -> Optional[str]:
        """Load token from cache file."""
        try:
            if not Path(self.token_cache_file).exists():
                return None
            
            with open(self.token_cache_file, 'r') as f:
                cache_data = json.load(f)
            
            token = cache_data.get('token')
            if token:
                logger.info(f"✓ Loaded token from cache: {self.token_cache_file}")
                return token
            
        except Exception as e:
            logger.debug(f"Could not load token from cache: {e}")
        
        return None
    
    def _test_token(self) -> bool:
        """
        Test if the current token works by making a simple API call.
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Try to get folders as a test
            url = f"{self.API_BASE}/v1/messageFolders"
            params = {'includeFolderCounts': 'false'}
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                logger.info("✓ Token is valid")
                return True
            elif response.status_code == 401:
                logger.info("Token is expired or invalid")
                return False
            else:
                logger.warning(f"Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing token: {e}")
            return False
    
    def authenticate_with_token(self, token: str) -> bool:
        """
        Authenticate using an auth token.
        
        Args:
            token: Auth token from localstorage.json
            
        Returns:
            True if authentication successful
        """
        self.auth_token = token
        self._set_auth_header(token)
        
        # Test the token
        if self._test_token():
            self.is_authenticated = True
            return True
        else:
            self.is_authenticated = False
            self.auth_token = None
            return False
    
    def load_from_browser_client(self, browser_client, localstorage_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Load authentication from browser client.
        
        Args:
            browser_client: Authenticated OFWBrowserClient instance
            localstorage_data: Optional localStorage data (if already fetched)
            
        Returns:
            True if authentication successful
        """
        # If localstorage data provided, use auth token directly
        if localstorage_data and 'auth' in localstorage_data:
            logger.info("Using auth token from provided localStorage data")
            auth_token = localstorage_data['auth']
            
            # Save and authenticate
            self._save_token_to_cache(auth_token)
            return self.authenticate_with_token(auth_token)
        else:
            # Fetch auth token from localstorage.json using cookies
            cookies = browser_client.get_cookies()
            return self.load_cookies_from_browser(cookies)
    
    def load_cookies_from_browser(self, browser_cookies: List[Dict[str, Any]]) -> bool:
        """
        Load cookies from browser client and get auth token.
        
        This will:
        1. Fetch localstorage.json to get auth token
        2. Set up API authentication with auth token
        
        Args:
            browser_cookies: List of cookie dicts from browser client.get_cookies()
            
        Returns:
            True if authentication successful
        """
        logger.info(f"Processing {len(browser_cookies)} cookies from browser...")
        
        # Get auth token from localstorage.json
        token = self._get_auth_token_from_localstorage(browser_cookies)
        
        if not token:
            logger.error("Failed to get auth token")
            return False
        
        # Save token to cache
        self._save_token_to_cache(token)
        
        # Set up authentication
        return self.authenticate_with_token(token)
    
    def try_cached_token(self) -> bool:
        """
        Try to authenticate using a cached token.
        
        Returns:
            True if cached token worked, False if need to re-authenticate
        """
        logger.info("Checking for cached token...")
        
        token = self._load_token_from_cache()
        
        if not token:
            logger.info("No cached token found")
            return False
        
        logger.info("Testing cached token...")
        if self.authenticate_with_token(token):
            logger.info("✓ Cached token is valid!")
            return True
        else:
            logger.info("Cached token is invalid or expired")
            return False
    
    def load_cookies_from_dict(self, cookies_dict: Dict[str, str]):
        """
        Load cookies from a dictionary and get auth token.
        
        Args:
            cookies_dict: Dictionary of cookie name -> value
        """
        # Convert dict to browser cookie format
        browser_cookies = [
            {'name': name, 'value': value}
            for name, value in cookies_dict.items()
        ]
        return self.load_cookies_from_browser(browser_cookies)
    
    def get_folders(self, include_counts: bool = True) -> Dict[str, Any]:
        """
        Get all message folders.
        
        Args:
            include_counts: Include message counts in the response
            
        Returns:
            Dictionary with 'systemFolders' and 'userFolders' keys
        """
        if not self.is_authenticated:
            raise Exception("Not authenticated. Load cookies first.")
        
        url = f"{self.API_BASE}/v1/messageFolders"
        params = {'includeFolderCounts': str(include_counts).lower()}
        
        logger.info(f"Fetching folders from {url}")
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"✓ Found {len(data.get('systemFolders', []))} system folders")
        logger.info(f"✓ Found {len(data.get('userFolders', []))} user folders")
        
        return data
    
    def list_folders(self, include_counts: bool = True) -> List[Dict[str, Any]]:
        """
        Get a flat list of all folders (system + user).
        
        Args:
            include_counts: Include message counts in the response
            
        Returns:
            List of folder dictionaries
        """
        data = self.get_folders(include_counts)
        
        all_folders = []
        
        # Add system folders
        for folder in data.get('systemFolders', []):
            folder['isSystemFolder'] = True
            all_folders.append(folder)
        
        # Add user folders
        for folder in data.get('userFolders', []):
            folder['isSystemFolder'] = False
            all_folders.append(folder)
        
        return all_folders
    
    def get_inbox_id(self) -> Optional[int]:
        """
        Get the ID of the Inbox folder.
        
        Returns:
            Inbox folder ID or None if not found
        """
        folders = self.get_folders(include_counts=False)
        
        for folder in folders.get('systemFolders', []):
            if folder.get('folderType') == 'INBOX':
                return folder['id']
        
        return None
    
    def get_messages(self, 
                     folder_id: Optional[int] = None,
                     page: int = 1,
                     size: int = 50,
                     sort: str = 'date',
                     sort_direction: str = 'desc') -> Dict[str, Any]:
        """
        Get messages from a folder.
        
        Args:
            folder_id: Folder ID to get messages from (None = Inbox)
            page: Page number (1-based)
            size: Number of messages per page (max 50)
            sort: Sort field ('date', 'subject', etc.)
            sort_direction: 'asc' or 'desc'
            
        Returns:
            Dictionary with 'metadata' and 'data' keys
        """
        if not self.is_authenticated:
            raise Exception("Not authenticated. Load cookies first.")
        
        # If no folder specified, use Inbox
        if folder_id is None:
            folder_id = self.get_inbox_id()
            if folder_id is None:
                raise Exception("Could not find Inbox folder")
            logger.info(f"Using Inbox folder (ID: {folder_id})")
        
        url = f"{self.API_BASE}/v3/messages"
        params = {
            'folders': folder_id,
            'page': page,
            'size': min(size, 50),  # Max 50
            'sort': sort,
            'sortDirection': sort_direction
        }
        
        logger.info(f"Fetching messages from folder {folder_id}, page {page}")
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        metadata = data.get('metadata', {})
        messages = data.get('data', [])
        
        logger.info(f"✓ Page {metadata.get('page')}, {len(messages)} messages")
        logger.info(f"  First page: {metadata.get('first')}, Last page: {metadata.get('last')}")
        
        return data
    
    def get_all_messages(self,
                         folder_id: Optional[int] = None,
                         max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all messages from a folder (fetches all pages).
        
        Args:
            folder_id: Folder ID to get messages from (None = Inbox)
            max_pages: Maximum number of pages to fetch (None = all pages)
            
        Returns:
            List of all message dictionaries
        """
        all_messages = []
        page = 1
        
        while True:
            if max_pages and page > max_pages:
                logger.info(f"Reached max_pages limit ({max_pages})")
                break
            
            data = self.get_messages(folder_id=folder_id, page=page)
            messages = data.get('data', [])
            metadata = data.get('metadata', {})
            
            all_messages.extend(messages)
            
            # Check if this is the last page
            if metadata.get('last', False):
                logger.info(f"✓ Fetched all messages ({len(all_messages)} total)")
                break
            
            page += 1
        
        return all_messages
    
    def get_message(self, message_id: int) -> Dict[str, Any]:
        """
        Get a single message by ID.
        
        Args:
            message_id: Message ID
            
        Returns:
            Message details dictionary
        """
        if not self.is_authenticated:
            raise Exception("Not authenticated. Load cookies first.")
        
        url = f"{self.API_BASE}/v3/messages/{message_id}"
        
        logger.info(f"Fetching message {message_id}")
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"✓ Message retrieved")
        
        return data
    
    def print_folders(self):
        """Print all folders in a nice format."""
        folders = self.list_folders()
        
        print("\n" + "="*70)
        print("MESSAGE FOLDERS")
        print("="*70)
        
        for folder in folders:
            folder_type = "System" if folder.get('isSystemFolder') else "User"
            unread = folder.get('unreadMessageCount', 0)
            total = folder.get('totalMessageCount', 0)
            
            print(f"\n[{folder['id']}] {folder['name']}")
            print(f"  Type: {folder_type}")
            print(f"  Messages: {total} total, {unread} unread")
            if 'folderType' in folder:
                print(f"  Folder Type: {folder['folderType']}")
    
    def print_messages(self, messages: List[Dict[str, Any]], limit: Optional[int] = None):
        """
        Print messages in a nice format.
        
        Args:
            messages: List of message dictionaries
            limit: Maximum number of messages to print
        """
        if limit:
            messages = messages[:limit]
        
        print("\n" + "="*70)
        print(f"MESSAGES ({len(messages)} shown)")
        print("="*70)
        
        for i, msg in enumerate(messages, 1):
            author = msg.get('author', {})
            date_info = msg.get('date', {})
            recipients = msg.get('recipients', [])
            
            print(f"\n[{i}] Message ID: {msg['id']}")
            print(f"  From: {author.get('name', 'Unknown')}")
            
            if recipients:
                recipient_names = [r['user']['name'] for r in recipients]
                print(f"  To: {', '.join(recipient_names)}")
            
            print(f"  Subject: {msg.get('subject', '(No subject)')}")
            print(f"  Date: {date_info.get('threeCharMonthWeekdayTimeNoYear', date_info.get('displayDate'))}")
            print(f"  Preview: {msg.get('preview', '(No preview)')[:100]}...")
            
            print(f"  Status: {'Read' if msg.get('read') else 'Unread'}", end='')
            if msg.get('replied'):
                print(" | Replied", end='')
            if msg.get('files', 0) > 0:
                print(f" | {msg['files']} file(s)", end='')
            print()


# Convenience function to create a client from browser cookies
def create_from_browser_client(browser_client, use_localstorage: bool = True) -> OFWMessagesClient:
    """
    Create a messages client from an authenticated browser client.
    
    Args:
        browser_client: Authenticated OFWBrowserClient instance
        use_localstorage: If True, try to get auth token from localStorage (faster)
        
    Returns:
        OFWMessagesClient ready to use
    """
    messages_client = OFWMessagesClient()
    
    # Try to get localStorage data if available
    localstorage_data = None
    if use_localstorage and browser_client.is_authenticated:
        try:
            localstorage_data = browser_client.get_local_storage()
            logger.info(f"Retrieved localStorage with {len(localstorage_data)} keys")
        except Exception as e:
            logger.debug(f"Could not get localStorage: {e}")
    
    if not messages_client.load_from_browser_client(browser_client, localstorage_data):
        raise Exception("Failed to authenticate with JWT token")
    
    return messages_client


def create_with_auto_auth(username: str, password: str, 
                          headless: bool = True,
                          token_cache_file: Optional[str] = None) -> OFWMessagesClient:
    """
    Create a messages client with automatic authentication.
    
    This will:
    1. Try to use cached JWT token first
    2. If that fails, login with browser and get new token
    
    Args:
        username: OFW username
        password: OFW password
        headless: Run browser in headless mode (if needed)
        token_cache_file: Path to token cache file
        
    Returns:
        Authenticated OFWMessagesClient
        
    Example:
        client = create_with_auto_auth("user@email.com", "password")
        messages = client.get_messages()
    """
    from ofw_browser_client import OFWBrowserClient
    
    messages_client = OFWMessagesClient(token_cache_file=token_cache_file)
    
    # Try cached token first
    if messages_client.try_cached_token():
        logger.info("✓ Using cached token (no browser needed)")
        return messages_client
    
    # Need to login with browser
    logger.info("Cached token not available, logging in with browser...")
    
    with OFWBrowserClient(headless=headless) as browser:
        if not browser.login(username, password):
            raise Exception("Browser login failed")
        
        cookies = browser.get_cookies()
        if not messages_client.load_cookies_from_browser(cookies):
            raise Exception("Failed to authenticate with JWT token")
    
    logger.info("✓ Authenticated successfully")
    return messages_client


if __name__ == "__main__":
    print("This module provides the OFWMessagesClient class.")
    print("\nExample usage:")
    print("""
from ofw_browser_client import OFWBrowserClient
from ofw_messages_client import create_from_browser_client

# Login with browser
with OFWBrowserClient() as browser:
    if browser.login(username, password):
        # Create messages client with browser cookies
        client = create_from_browser_client(browser)
        
        # Get folders
        client.print_folders()
        
        # Get messages
        messages = client.get_messages()
        client.print_messages(messages['data'])
""")
