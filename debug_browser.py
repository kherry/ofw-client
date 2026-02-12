"""
Browser-based debugging script for OFW login
"""

from ofw_browser_client import OFWBrowserClient
from getpass import getpass
import json


def inspect_browser_login():
    """Detailed inspection using browser."""
    
    print("="*70)
    print("OUR FAMILY WIZARD BROWSER LOGIN INSPECTOR")
    print("="*70)
    print()
    print("This will:")
    print("- Open a Chrome browser (visible, not headless)")
    print("- Navigate through the login flow")
    print("- Save screenshots at each step")
    print("- Extract all cookies and storage data")
    print("- Save everything to debug/ folder")
    print()
    
    input("Press Enter to continue...")
    
    # Always use non-headless mode for debugging and enable screenshots
    client = OFWBrowserClient(headless=False, debug_screenshots=True)
    
    try:
        print("\n[Step 1] Setting up browser...")
        print("-" * 70)
        
        # Driver will be set up on first navigation
        print("✓ Browser will open when navigating to login page")
        
        print("\n[Step 2] Do you want to test login?")
        print("-" * 70)
        test_login = input("Test login with credentials? (Y/n): ").strip().lower() != 'n'
        
        if test_login:
            username = input("Enter username: ")
            password = getpass("Enter password: ")
            
            print("\n[Step 3] Logging in...")
            print("-" * 70)
            print("Watch the browser window to see what's happening!")
            print()
            
            success = client.login(username, password)
            
            if success:
                print("\n" + "="*70)
                print("✓✓✓ LOGIN SUCCESSFUL! ✓✓✓")
                print("="*70)
                
                print("\n[Step 4] Extracting session data...")
                print("-" * 70)
                
                # Get all session data
                session_info = client.get_session_info()
                
                # Display summary
                print(f"\n✓ Current URL: {session_info['current_url']}")
                print(f"✓ Cookies ({len(session_info['cookies'])} total):")
                for cookie in session_info['cookies']:
                    print(f"  - {cookie['name']}: {cookie['value'][:30]}...")
                
                if 'localStorage' in session_info:
                    print(f"\n✓ LocalStorage ({len(session_info['localStorage'])} keys):")
                    for key in session_info['localStorage'].keys():
                        print(f"  - {key}")
                
                if 'sessionStorage' in session_info:
                    print(f"\n✓ SessionStorage ({len(session_info['sessionStorage'])} keys):")
                    for key in session_info['sessionStorage'].keys():
                        print(f"  - {key}")
                
                # Check for the success elements
                print("\n[Step 5] Verifying authenticated page elements...")
                print("-" * 70)
                try:
                    greeting = client.find_element(By.ID, "greeting")
                    notifications = client.find_element(By.ID, "notificationsSection")
                    
                    print("✓ Found div#greeting")
                    print("✓ Found div#notificationsSection")
                    
                    # Try to get the greeting text
                    try:
                        greeting_text = greeting.text
                        if greeting_text:
                            print(f"  Greeting text: {greeting_text}")
                    except:
                        pass
                except Exception as e:
                    print(f"⚠ Warning: {e}")
                
                # Save complete session info
                with open('debug/complete_session_info.json', 'w', encoding='utf-8') as f:
                    json.dump(session_info, f, indent=2, default=str)
                print(f"\n✓ Complete session data saved to: debug/complete_session_info.json")
                
                print("\n[Step 6] Screenshots and HTML saved:")
                print("-" * 70)
                import os
                debug_files = sorted([f for f in os.listdir('debug') if f.endswith(('.png', '.html', '.json'))])
                for f in debug_files:
                    print(f"  ✓ debug/{f}")
                
                print("\n[Step 7] Browser will remain open for inspection...")
                print("-" * 70)
                print("You can now:")
                print("- Inspect the authenticated session in the browser")
                print("- Navigate to different pages manually")
                print("- Check the DevTools console")
                print("- Look at cookies in DevTools (Application tab)")
                print()
                
                input("Press Enter to close browser and logout...")
                
            else:
                print("\n" + "="*70)
                print("✗✗✗ LOGIN FAILED ✗✗✗")
                print("="*70)
                
                print("\nDebug information saved:")
                import os
                debug_files = sorted([f for f in os.listdir('debug') if f.endswith(('.png', '.html'))])
                for f in debug_files:
                    print(f"  - debug/{f}")
                
                print("\nNext steps:")
                print("1. Check the screenshots to see where it failed")
                print("2. Review the HTML files for error messages")
                print("3. Check if the form field names are correct")
                print()
                
                input("Press Enter to close browser...")
        
        else:
            print("\nSkipping login test.")
            print("Browser setup verified - you can use the OFWBrowserClient class in your code.")
    
    finally:
        # Clean up
        client.logout()


def compare_with_without_js():
    """Compare what we see with/without JavaScript."""
    
    print("="*70)
    print("COMPARING JAVASCRIPT VS NO-JAVASCRIPT")
    print("="*70)
    print()
    print("This will show you what's different when JavaScript runs")
    print()
    
    # First, get the page with requests (no JS)
    print("[1] Fetching login page WITHOUT JavaScript (using requests)...")
    import requests
    from bs4 import BeautifulSoup
    
    session = requests.Session()
    response = session.get("https://ofw.ourfamilywizard.com/app/login")
    
    with open('debug/no_js_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    no_js_forms = soup.find_all('form')
    no_js_scripts = soup.find_all('script')
    
    print(f"✓ Saved to: debug/no_js_page.html")
    print(f"  Forms found: {len(no_js_forms)}")
    print(f"  Script tags: {len(no_js_scripts)}")
    
    # Now get it with browser (with JS)
    print("\n[2] Fetching login page WITH JavaScript (using browser)...")
    with OFWBrowserClient(headless=True, debug_screenshots=True) as client:
        client._setup_driver()
        client.driver.get("https://ofw.ourfamilywizard.com/app/login")
        client._wait_for_page_load()
        
        # Save the rendered page
        client._save_page_source("with_js_page")
        client._take_screenshot("with_js_page")
        
        # Analyze
        soup_js = BeautifulSoup(client.driver.page_source, 'html.parser')
        js_forms = soup_js.find_all('form')
        
        print(f"✓ Saved to: debug/with_js_page.html")
        print(f"  Forms found: {len(js_forms)}")
    
    print("\n[3] Comparison:")
    print("-" * 70)
    print(f"Forms without JS: {len(no_js_forms)}")
    print(f"Forms with JS:    {len(js_forms)}")
    print(f"\nScripts on page:  {len(no_js_scripts)}")
    
    print("\nYou can now compare:")
    print("  debug/no_js_page.html  - What requests library sees")
    print("  debug/with_js_page.html - What the browser sees after JS runs")
    print()


if __name__ == "__main__":
    print("Choose an option:")
    print("1. Inspect browser login (interactive)")
    print("2. Compare JavaScript vs No-JavaScript")
    print("3. Both")
    print()
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == "1":
        inspect_browser_login()
    elif choice == "2":
        compare_with_without_js()
    elif choice == "3":
        compare_with_without_js()
        print("\n" + "="*70)
        input("Press Enter to continue to interactive login test...")
        inspect_browser_login()
    else:
        print("Invalid choice")
