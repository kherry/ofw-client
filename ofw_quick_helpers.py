"""
Quick Helper Functions for OFW

Simplified functions for common tasks.
"""

from ofw_messages_client import create_with_auto_auth
from typing import Optional, List, Dict, Any
import json


def quick_login_and_get_messages(username: str, 
                                  password: str,
                                  folder_id: Optional[int] = None,
                                  headless: bool = True) -> List[Dict[str, Any]]:
    """
    Quick function to login and get messages in one call.
    Uses cached token if available, otherwise logs in with browser.
    
    Args:
        username: OFW username
        password: OFW password
        folder_id: Folder to get messages from (None = Inbox)
        headless: Run browser in headless mode (if needed)
        
    Returns:
        List of message dictionaries
        
    Example:
        messages = quick_login_and_get_messages("user@email.com", "password")
        for msg in messages:
            print(f"{msg['author']['name']}: {msg['subject']}")
    """
    client = create_with_auto_auth(username, password, headless=headless)
    data = client.get_messages(folder_id=folder_id)
    return data.get('data', [])


def quick_login_and_get_folders(username: str,
                                 password: str,
                                 headless: bool = True) -> Dict[str, Any]:
    """
    Quick function to login and get folders in one call.
    Uses cached token if available, otherwise logs in with browser.
    
    Args:
        username: OFW username
        password: OFW password
        headless: Run browser in headless mode (if needed)
        
    Returns:
        Dictionary with 'systemFolders' and 'userFolders'
        
    Example:
        folders = quick_login_and_get_folders("user@email.com", "password")
        for folder in folders['systemFolders']:
            print(f"{folder['name']}: {folder['unreadMessageCount']} unread")
    """
    client = create_with_auto_auth(username, password, headless=headless)
    return client.get_folders()


def get_unread_message_count(username: str,
                             password: str,
                             headless: bool = True) -> Dict[str, int]:
    """
    Get unread message counts for all folders.
    Uses cached token if available, otherwise logs in with browser.
    
    Args:
        username: OFW username
        password: OFW password
        headless: Run browser in headless mode (if needed)
        
    Returns:
        Dictionary mapping folder name to unread count
        
    Example:
        counts = get_unread_message_count("user@email.com", "password")
        print(f"Inbox: {counts['Inbox']} unread")
        print(f"Action Items: {counts['Action Items']} unread")
    """
    client = create_with_auto_auth(username, password, headless=headless)
    folders_data = client.get_folders()
    
    counts = {}
    for folder in folders_data.get('systemFolders', []):
        counts[folder['name']] = folder.get('unreadMessageCount', 0)
    
    for folder in folders_data.get('userFolders', []):
        counts[folder['name']] = folder.get('unreadMessageCount', 0)
    
    return counts


def search_messages_by_subject(username: str,
                               password: str,
                               search_term: str,
                               folder_id: Optional[int] = None,
                               headless: bool = True) -> List[Dict[str, Any]]:
    """
    Search for messages containing a term in the subject.
    Uses cached token if available, otherwise logs in with browser.
    
    Args:
        username: OFW username
        password: OFW password
        search_term: Term to search for (case-insensitive)
        folder_id: Folder to search (None = Inbox)
        headless: Run browser in headless mode (if needed)
        
    Returns:
        List of matching messages
        
    Example:
        messages = search_messages_by_subject("user@email.com", "password", "doctor")
        for msg in messages:
            print(f"Found: {msg['subject']}")
    """
    client = create_with_auto_auth(username, password, headless=headless)
    all_messages = client.get_all_messages(folder_id=folder_id)
    
    search_term_lower = search_term.lower()
    matches = [
        msg for msg in all_messages
        if search_term_lower in msg.get('subject', '').lower()
    ]
    
    return matches


# Example usage
if __name__ == "__main__":
    from getpass import getpass
    
    print("Quick Helper Functions Demo")
    print("="*70)
    
    username = input("Username: ")
    password = getpass("Password: ")
    
    print("\n1. Getting unread counts...")
    try:
        counts = get_unread_message_count(username, password)
        for folder_name, count in counts.items():
            print(f"  {folder_name}: {count} unread")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n2. Getting recent messages...")
    try:
        messages = quick_login_and_get_messages(username, password)
        print(f"  Retrieved {len(messages)} messages")
        if messages:
            print(f"  Latest: {messages[0]['subject']}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n3. Saving cookies for reuse...")
    try:
        save_cookies_for_reuse(username, password, 'my_ofw_cookies.json')
    except Exception as e:
        print(f"  Error: {e}")
