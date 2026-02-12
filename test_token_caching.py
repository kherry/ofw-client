"""
Test Token Caching

This script demonstrates how the JWT token caching works:
- First run: Logs in with browser, gets token, caches it
- Subsequent runs: Uses cached token (no browser needed!)
"""

from ofw_messages_client import create_with_auto_auth
from getpass import getpass


def main():
    print("="*70)
    print("JWT TOKEN CACHING TEST")
    print("="*70)
    print()
    print("This will demonstrate token caching:")
    print("1. First time: Login with browser → Get JWT token → Cache it")
    print("2. Next time: Use cached token → No browser needed!")
    print()
    
    username = input("Enter your OFW username/email: ")
    password = getpass("Enter your OFW password: ")
    
    print("\n" + "="*70)
    print("Attempting Authentication...")
    print("="*70)
    print()
    
    try:
        # This will:
        # 1. Try cached token first
        # 2. If that fails, login with browser and get new token
        client = create_with_auto_auth(username, password, headless=True)
        
        print("\n✓ Authentication successful!")
        print()
        
        # Test the API
        print("="*70)
        print("Testing API...")
        print("="*70)
        print()
        
        # Get folders
        print("Fetching folders...")
        folders = client.get_folders()
        
        print(f"✓ Found {len(folders['systemFolders'])} system folders")
        for folder in folders['systemFolders']:
            print(f"  - {folder['name']}: {folder['unreadMessageCount']} unread")
        
        # Get messages
        print("\nFetching messages from Inbox...")
        messages_data = client.get_messages()
        messages = messages_data['data']
        
        print(f"✓ Found {len(messages)} messages")
        if messages:
            print(f"\nLatest message:")
            msg = messages[0]
            print(f"  From: {msg['author']['name']}")
            print(f"  Subject: {msg['subject']}")
            print(f"  Date: {msg['date']['displayDate']}")
        
        print("\n" + "="*70)
        print("SUCCESS!")
        print("="*70)
        print()
        print("Token has been cached to: debug/ofw_jwt_token.json")
        print()
        print("Next time you run this script:")
        print("- It will use the cached token")
        print("- No browser will launch")
        print("- Authentication will be instant!")
        print()
        print("Try running this script again to see the difference!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
