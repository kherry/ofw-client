"""
Complete Example: Browser Login + Messages API

This example shows:
1. Try cached auth token first (no browser needed!)
2. Login with browser if needed (to handle JavaScript)
3. Transfer auth token to requests session
4. Use API endpoints to fetch folders and messages
5. Interactive menu to read messages and navigate
"""

from ofw_browser_client import OFWBrowserClient
from ofw_messages_client import OFWMessagesClient
from getpass import getpass
import json
import os


def display_message_details(messages_client, message_id):
    """Display full message details."""
    print(f"\nFetching full message {message_id}...")
    
    try:
        full_message = messages_client.get_message(message_id)
        
        # Save full message
        with open('debug/full_message.json', 'w') as f:
            json.dump(full_message, f, indent=2)
        
        # Display the message
        print("\n" + "="*70)
        print("MESSAGE DETAILS")
        print("="*70)
        
        print(f"\nFrom: {full_message.get('author', {}).get('name', 'Unknown')}")
        
        recipients = full_message.get('recipients', [])
        if recipients:
            recipient_names = [r['user']['name'] for r in recipients]
            print(f"To: {', '.join(recipient_names)}")
        
        print(f"Subject: {full_message.get('subject', '(No subject)')}")
        
        date_info = full_message.get('date', {})
        print(f"Date: {date_info.get('threeCharMonthWeekdayTimeNoYear', date_info.get('displayDate'))}")
        
        print(f"\n{'-'*70}")
        print("MESSAGE BODY:")
        print(f"{'-'*70}")
        
        body = full_message.get('body', '(No content)')
        print(body)
        
        print(f"{'-'*70}")
        
        # Show attachments if any
        attachments = full_message.get('attachments', [])
        if attachments:
            print(f"\nAttachments ({len(attachments)}):")
            for att in attachments:
                print(f"  - {att.get('name', 'Unknown')} ({att.get('size', 0)} bytes)")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error fetching message: {e}")
        import traceback
        traceback.print_exc()
        return False


def interactive_menu(messages_client):
    """Interactive menu for browsing folders and reading messages."""
    
    current_folder_id = None
    current_folder_name = "Inbox"
    messages_list = []
    folders_data = None
    
    while True:
        print("\n" + "="*70)
        print(f"FOLDER: {current_folder_name}")
        print("="*70)
        print("\nOptions:")
        print("  1. List messages in current folder")
        print("  2. Read a message")
        print("  3. Show all folders")
        print("  4. Switch to different folder")
        print("  5. Quit")
        print()
        
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == "1":
            # List messages
            print("\n" + "="*70)
            print(f"MESSAGES IN: {current_folder_name}")
            print("="*70)
            
            try:
                messages_data = messages_client.get_messages(folder_id=current_folder_id, page=1, size=50)
                messages_list = messages_data.get('data', [])
                metadata = messages_data.get('metadata', {})
                
                # Save messages data
                with open('debug/messages.json', 'w') as f:
                    json.dump(messages_data, f, indent=2)
                
                print(f"\n✓ Retrieved {len(messages_list)} messages")
                print(f"  Page: {metadata.get('page')}")
                print(f"  First page: {metadata.get('first')}")
                print(f"  Last page: {metadata.get('last')}")
                
                # Display messages
                messages_client.print_messages(messages_list, limit=20)
                
            except Exception as e:
                print(f"\n✗ Error fetching messages: {e}")
        
        elif choice == "2":
            # Read a message
            if not messages_list:
                print("\n⚠ Please list messages first (option 1)")
                continue
            
            print(f"\nYou have {len(messages_list)} messages loaded")
            msg_num = input(f"Enter message number (1-{len(messages_list)}) or 'c' to cancel: ").strip()
            
            if msg_num.lower() == 'c':
                continue
            
            if msg_num.isdigit():
                msg_index = int(msg_num) - 1
                
                if 0 <= msg_index < len(messages_list):
                    selected_msg = messages_list[msg_index]
                    msg_id = selected_msg['id']
                    display_message_details(messages_client, msg_id)
                else:
                    print(f"\n✗ Invalid message number. Please enter 1-{len(messages_list)}")
            else:
                print("\n✗ Invalid input. Please enter a number.")
        
        elif choice == "3":
            # Show all folders
            print("\n" + "="*70)
            print("ALL FOLDERS")
            print("="*70)
            
            try:
                if not folders_data:
                    folders_data = messages_client.get_folders()
                
                messages_client.print_folders()
                
            except Exception as e:
                print(f"\n✗ Error fetching folders: {e}")
        
        elif choice == "4":
            # Switch folder
            print("\n" + "="*70)
            print("SWITCH FOLDER")
            print("="*70)
            
            try:
                if not folders_data:
                    folders_data = messages_client.get_folders()
                
                all_folders = messages_client.list_folders()
                
                print("\nAvailable folders:")
                for i, folder in enumerate(all_folders, 1):
                    unread = folder.get('unreadMessageCount', 0)
                    total = folder.get('totalMessageCount', 0)
                    print(f"  {i}. {folder['name']} ({total} total, {unread} unread)")
                
                folder_choice = input(f"\nEnter folder number (1-{len(all_folders)}) or 'c' to cancel: ").strip()
                
                if folder_choice.lower() == 'c':
                    continue
                
                if folder_choice.isdigit():
                    folder_index = int(folder_choice) - 1
                    
                    if 0 <= folder_index < len(all_folders):
                        selected_folder = all_folders[folder_index]
                        current_folder_id = selected_folder['id']
                        current_folder_name = selected_folder['name']
                        messages_list = []  # Clear messages when switching folders
                        print(f"\n✓ Switched to: {current_folder_name}")
                    else:
                        print(f"\n✗ Invalid folder number")
                else:
                    print("\n✗ Invalid input")
                    
            except Exception as e:
                print(f"\n✗ Error: {e}")
        
        elif choice == "5":
            # Quit
            print("\nGoodbye!")
            break
        
        else:
            print("\n✗ Invalid choice. Please enter 1-5.")


def main():
    print("="*70)
    print("OFW COMPLETE WORKFLOW EXAMPLE")
    print("="*70)
    print("\nThis will:")
    print("1. Try cached auth token (fast!)")
    print("2. Login with browser if needed")
    print("3. Interactive menu for browsing messages")
    print()
    
    # Check for cached token
    messages_client = OFWMessagesClient()
    
    print("="*70)
    print("STEP 1: Authentication")
    print("="*70)
    
    if messages_client.try_cached_token():
        print("\n✓ Using cached auth token (no browser needed!)")
    else:
        print("\nNo valid cached token found. Need to login...")
        
        # Get credentials
        username = input("\nEnter your OFW username/email: ")
        password = getpass("Enter your OFW password: ")
        
        print("\nLogging in with browser...")
        
        # Login with browser (headless)
        with OFWBrowserClient(headless=True, debug_screenshots=True) as browser:
            
            if not browser.login(username, password):
                print("\n✗ Login failed. Check debug/ folder for details.")
                return
            
            print("✓ Browser login successful!")
            
            # Get localStorage and extract auth token
            localstorage = browser.get_local_storage()
            
            if not messages_client.load_from_browser_client(browser, localstorage):
                print("\n✗ Failed to authenticate with auth token")
                return
            
            print("✓ Auth token retrieved and cached!")
    
    print("\n" + "="*70)
    print("STEP 2: Fetch Folders")
    print("="*70)
    
    try:
        folders_data = messages_client.get_folders()
        
        # Save folders data
        with open('debug/folders.json', 'w') as f:
            json.dump(folders_data, f, indent=2)
        print("\n✓ Folders data saved to: debug/folders.json")
        
        # Display folders
        messages_client.print_folders()
        
    except Exception as e:
        print(f"\n✗ Error fetching folders: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*70)
    print("STEP 3: Interactive Menu")
    print("="*70)
    
    # Enter interactive menu
    interactive_menu(messages_client)
    
    print("\n" + "="*70)
    print("Session ended. Auth token saved for next time!")
    print("="*70)


if __name__ == "__main__":
    main()
