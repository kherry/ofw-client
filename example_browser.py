"""
Example usage of the OFW Browser Client (Selenium-based)
"""

from ofw_browser_client import OFWBrowserClient
from getpass import getpass
import json


def main():
    """Example of how to use the OFW browser client."""
    
    print("="*60)
    print("OUR FAMILY WIZARD BROWSER CLIENT")
    print("Uses Selenium with headless Chrome")
    print("="*60)
    print()
    
    # Get credentials
    username = input("Enter your OFW username/email: ")
    password = getpass("Enter your OFW password: ")
    
    # Ask about headless mode
    headless_input = input("Run in headless mode? (Y/n): ").strip().lower()
    headless = headless_input != 'n'
    
    # Ask about debug screenshots
    debug_input = input("Save debug screenshots? (Y/n): ").strip().lower()
    debug_screenshots = debug_input != 'n'
    
    print("\n" + "="*60)
    print("Logging in...")
    print("="*60)
    print()
    
    # Use context manager to ensure browser is closed
    with OFWBrowserClient(headless=headless, debug_screenshots=debug_screenshots) as client:
        
        # Attempt login
        success = client.login(username, password)
        
        if success:
            print("\n" + "✓"*60)
            print("LOGIN SUCCESSFUL!")
            print("✓"*60)
            
            # Get session information
            print("\nRetrieving session information...")
            session_info = client.get_session_info()
            
            # Save session info
            with open('debug/browser_session_info.json', 'w', encoding='utf-8') as f:
                json.dump(session_info, f, indent=2, default=str)
            
            print(f"\n✓ Session info saved to: debug/browser_session_info.json")
            print(f"✓ Current URL: {session_info['current_url']}")
            print(f"✓ Number of cookies: {len(session_info['cookies'])}")
            
            if 'localStorage' in session_info:
                print(f"✓ LocalStorage keys: {list(session_info['localStorage'].keys())}")
            
            if 'sessionStorage' in session_info:
                print(f"✓ SessionStorage keys: {list(session_info['sessionStorage'].keys())}")
            
            # Example: Navigate to messages page
            print("\n" + "="*60)
            print("Authenticated session is active!")
            print("="*60)
            print()
            print("You can now:")
            print("- Navigate to different pages")
            print("- Extract data from the page")
            print("- Interact with elements")
            print("- Execute JavaScript")
            print()
            
            # Keep browser open for inspection
            if not headless:
                input("Press Enter to close browser and logout...")
            else:
                print("Browser will close in 5 seconds...")
                import time
                time.sleep(5)
            
            print("\nLogging out...")
            # Browser will auto-close when exiting context manager
            
        else:
            print("\n" + "✗"*60)
            print("LOGIN FAILED")
            print("✗"*60)
            print()
            print("Troubleshooting:")
            print("1. Check your credentials")
            print("2. Review debug screenshots in debug/ folder")
            print("3. Check debug HTML files for error messages")
            print("4. Try running without headless mode to see what's happening")


if __name__ == "__main__":
    main()
