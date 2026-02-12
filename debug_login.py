"""
Debugging script to inspect the OFW login flow
This will help you understand what's happening during login
"""

from ofw_client import OFWClient
import requests
from bs4 import BeautifulSoup
from getpass import getpass
import json
import os


# Create debug directory
DEBUG_DIR = "debug"
os.makedirs(DEBUG_DIR, exist_ok=True)


def inspect_login_page():
    """Detailed inspection of the login page."""
    
    print("="*60)
    print("OUR FAMILY WIZARD LOGIN FLOW INSPECTOR")
    print("="*60)
    
    client = OFWClient()
    
    print("\n[1] Initializing session via localstorage.json...")
    try:
        # Call the localstorage.json endpoint first
        localstorage_url = f"{client.BASE_URL}/ofw/appv2/localstorage.json"
        response = client.session.get(localstorage_url)
        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ URL: {response.url}")
        
        # Show response content
        try:
            json_data = response.json()
            print(f"✓ Response JSON: {json_data}")
            
            # Save JSON response
            with open(f'{DEBUG_DIR}/localstorage_initial.json', 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
            print(f"✓ Saved to: {DEBUG_DIR}/localstorage_initial.json")
        except:
            response_text = response.text
            print(f"✓ Response Text (first 200 chars): {response_text[:200]}")
            
            # Save text response
            with open(f'{DEBUG_DIR}/localstorage_initial.txt', 'w', encoding='utf-8') as f:
                f.write(response_text)
            print(f"✓ Saved to: {DEBUG_DIR}/localstorage_initial.txt")
        
        print("\n[2] Cookies received from localstorage.json:")
        cookies_after_localstorage = dict(client.session.cookies)
        if cookies_after_localstorage:
            for cookie_name, cookie_value in cookies_after_localstorage.items():
                print(f"  - {cookie_name}: {cookie_value[:50]}...")
        else:
            print("  ✗ No cookies received!")
        
        print("\n[3] Fetching login page...")
        response = client._get_login_page()
        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ URL: {response.url}")
        
        print("\n[4] Cookies after login page fetch:")
        for cookie_name, cookie_value in client.session.cookies.items():
            print(f"  - {cookie_name}: {cookie_value[:50]}...")
        
        print("\n[5] Extracting CSRF token...")
        csrf_token = client._extract_csrf_token(response.text)
        if csrf_token:
            print(f"✓ CSRF Token found: {csrf_token[:30]}...")
        else:
            print("✗ No CSRF token found")
        
        print("\n[6] Extracting form data...")
        form_data = client._extract_form_data(response.text)
        if form_data:
            print("✓ Hidden form fields found:")
            for field_name, field_value in form_data.items():
                value_display = field_value[:50] if len(field_value) > 50 else field_value
                print(f"  - {field_name}: {value_display}")
        else:
            print("✗ No hidden form fields found")
        
        print("\n[7] Analyzing login form...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all forms
        forms = soup.find_all('form')
        print(f"✓ Found {len(forms)} form(s) on the page")
        
        for idx, form in enumerate(forms, 1):
            print(f"\n  Form {idx}:")
            print(f"    - Action: {form.get('action', 'Not specified')}")
            print(f"    - Method: {form.get('method', 'Not specified')}")
            print(f"    - ID: {form.get('id', 'Not specified')}")
            
            # Find input fields
            inputs = form.find_all('input')
            print(f"    - Input fields ({len(inputs)}):")
            for input_field in inputs:
                field_type = input_field.get('type', 'text')
                field_name = input_field.get('name', 'unnamed')
                field_id = input_field.get('id', 'no-id')
                print(f"      • {field_name} (type: {field_type}, id: {field_id})")
        
        # Save HTML for manual inspection
        print("\n[8] Saving HTML for manual inspection...")
        with open(f'{DEBUG_DIR}/login_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"✓ Saved to: {DEBUG_DIR}/login_page.html")
        
        # Try to identify the login endpoint
        print("\n[9] Identifying login endpoint...")
        for form in forms:
            action = form.get('action', '')
            if any(keyword in action.lower() for keyword in ['login', 'signin', 'auth']) or not action:
                print(f"✓ Likely login form action: {action if action else '(same page)'}")
        
        return client
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_login(client):
    """Test actual login."""
    
    print("\n" + "="*60)
    print("TESTING LOGIN")
    print("="*60)
    
    username = input("\nEnter username (or press Enter to skip): ")
    if not username:
        print("Skipping login test")
        return
    
    password = getpass("Enter password: ")
    
    print("\nAttempting login...")
    print("Expected flow:")
    print("  1. POST to /app/login")
    print("  2. Redirect to /ofw/home.form")
    print("  3. Redirect to /ofw/appv2/home.form")
    print("  4. GET /ofw/appv2/localstorage.json")
    print()
    
    success = client.login(username, password)
    
    if success:
        print("\n✓✓✓ LOGIN SUCCESSFUL! ✓✓✓")
        print("\nSession Info:")
        session_info = client.get_session_info()
        
        # Save session info
        with open(f'{DEBUG_DIR}/session_info.json', 'w', encoding='utf-8') as f:
            json.dump(session_info, f, indent=2, default=str)
        
        print(json.dumps(session_info, indent=2, default=str))
        print(f"\n✓ Session info saved to: {DEBUG_DIR}/session_info.json")
        
        # Check if we got the authenticated page elements
        print("\n[VERIFICATION] Checking for authenticated page elements...")
        from bs4 import BeautifulSoup
        
        # We need to fetch the current page to check
        try:
            current_response = client.session.get(client.driver.current_url if hasattr(client, 'driver') else f"{client.BASE_URL}/ofw/appv2/home.form")
            soup = BeautifulSoup(current_response.text, 'html.parser')
            
            greeting = soup.find('div', {'id': 'greeting'})
            notifications = soup.find('div', {'id': 'notificationsSection'})
            
            if greeting:
                print("✓ Found div#greeting")
                greeting_text = greeting.get_text(strip=True)
                if greeting_text:
                    print(f"  Text: {greeting_text[:100]}")
            else:
                print("✗ div#greeting NOT FOUND")
            
            if notifications:
                print("✓ Found div#notificationsSection")
            else:
                print("✗ div#notificationsSection NOT FOUND")
            
            # Save this page for inspection
            with open(f'{DEBUG_DIR}/authenticated_page.html', 'w', encoding='utf-8') as f:
                f.write(current_response.text)
            print(f"✓ Authenticated page saved to: {DEBUG_DIR}/authenticated_page.html")
            
        except Exception as e:
            print(f"⚠ Could not verify page elements: {e}")
        
        # Try to fetch localstorage.json again and show its contents
        print("\n[POST-LOGIN] Fetching localstorage.json to see populated data...")
        localstorage_url = f"{client.BASE_URL}/ofw/appv2/localstorage.json"
        response = client.session.get(localstorage_url)
        
        try:
            localstorage_data = response.json()
            print(f"✓ Localstorage data (populated): {json.dumps(localstorage_data, indent=2)}")
            
            with open(f'{DEBUG_DIR}/localstorage_authenticated.json', 'w', encoding='utf-8') as f:
                json.dump(localstorage_data, f, indent=2)
            print(f"✓ Saved to: {DEBUG_DIR}/localstorage_authenticated.json")
        except:
            print(f"Response: {response.text[:500]}")
            with open(f'{DEBUG_DIR}/localstorage_authenticated.txt', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"✓ Saved to: {DEBUG_DIR}/localstorage_authenticated.txt")
        
    else:
        print("\n✗✗✗ LOGIN FAILED ✗✗✗")
        print("\nTroubleshooting tips:")
        print("1. Check if your credentials are correct")
        print(f"2. Review the saved HTML file: {DEBUG_DIR}/login_page.html")
        print("3. Check if there are any additional required fields")
        print("4. Verify the login form action URL")
        print(f"5. Check debug files in {DEBUG_DIR}/ directory")


if __name__ == "__main__":
    print(f"Debug files will be saved to: {DEBUG_DIR}/")
    print()
    
    client = inspect_login_page()
    
    if client:
        test_login(client)
        
        if client.is_authenticated:
            input("\nPress Enter to logout...")
            client.logout()

