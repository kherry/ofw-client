"""
Debug script to diagnose JSON escaping issue
Run this with DEBUG logging to see exactly what's happening
"""

from ofw_browser_client import OFWBrowserClient
from ofw_messages_client import create_from_browser_client
from getpass import getpass
import logging
import json

# Setup logging directly
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    print("="*70)
    print("JSON ESCAPING DEBUG")
    print("="*70)
    print()
    print("This will show detailed logging to diagnose the escaping issue")
    print()
    
    username = input("Enter username: ")
    password = getpass("Enter password: ")
    
    print("\n" + "="*70)
    print("STEP 1: Browser Login")
    print("="*70)
    
    with OFWBrowserClient(headless=True, debug_screenshots=False) as browser:
        if not browser.login(username, password):
            print("Login failed")
            return
        
        print("\n✓ Login successful")
        
        print("\n" + "="*70)
        print("STEP 2: Get localStorage (watch for debug logs)")
        print("="*70)
        
        # This will show detailed logging
        localstorage = browser.get_local_storage()
        
        print(f"\nLocalStorage keys: {list(localstorage.keys())}")
        if 'auth' in localstorage:
            auth_value = localstorage['auth']
            print(f"\nAuth value:")
            print(f"  Type: {type(auth_value)}")
            print(f"  Repr: {repr(auth_value)[:200]}")
            print(f"  First 50 chars: {str(auth_value)[:50]}")
        
        print("\n" + "="*70)
        print("STEP 3: Create messages client (watch for debug logs)")
        print("="*70)
        
        # This will show what gets saved to the cache
        try:
            client = create_from_browser_client(browser, use_localstorage=True)
            print("\n✓ Messages client created")
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        print("\n" + "="*70)
        print("STEP 4: Check saved files")
        print("="*70)
        
        # Read and display the saved files
        print("\n[localstorage_data.json]")
        try:
            with open('debug/localstorage_data.json', 'r') as f:
                content = f.read()
                print(f"Raw file content (first 500 chars):")
                print(content[:500])
                print()
                
            with open('debug/localstorage_data.json', 'r') as f:
                data = json.load(f)
                if 'auth' in data:
                    print(f"Auth value after loading:")
                    print(f"  Type: {type(data['auth'])}")
                    print(f"  Repr: {repr(data['auth'])[:200]}")
        except Exception as e:
            print(f"Error reading file: {e}")
        
        print("\n[ofw_auth_token.json]")
        try:
            with open('debug/ofw_auth_token.json', 'r') as f:
                content = f.read()
                print(f"Raw file content:")
                print(content)
                print()
                
            with open('debug/ofw_auth_token.json', 'r') as f:
                data = json.load(f)
                print(f"Token value after loading:")
                print(f"  Type: {type(data['token'])}")
                print(f"  Repr: {repr(data['token'])[:200]}")
        except Exception as e:
            print(f"Error reading file: {e}")
        
        print("\n" + "="*70)
        print("Check the debug log file for detailed trace")
        print("="*70)


if __name__ == "__main__":
    main()
