"""
Cookie Inspector - Detailed analysis of OFW cookie flow
"""

import requests
from ofw_client import OFWClient
import json
import os


# Create debug directory
DEBUG_DIR = "debug"
os.makedirs(DEBUG_DIR, exist_ok=True)


def inspect_cookies_detailed():
    """Perform detailed cookie inspection."""
    
    print("="*70)
    print("OFW COOKIE FLOW INSPECTOR")
    print("="*70)
    print(f"Debug files will be saved to: {DEBUG_DIR}/")
    print()
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    })
    
    base_url = "https://ofw.ourfamilywizard.com"
    
    # Step 1: Call localstorage.json
    print("\n[STEP 1] Calling localstorage.json endpoint")
    print("-" * 70)
    
    localstorage_url = f"{base_url}/ofw/appv2/localstorage.json"
    print(f"URL: {localstorage_url}")
    
    cookies_log = []
    
    try:
        response1 = session.get(localstorage_url)
        print(f"✓ Status Code: {response1.status_code}")
        print(f"✓ Response URL: {response1.url}")
        
        # Show response headers
        print("\nResponse Headers:")
        for header, value in response1.headers.items():
            if 'cookie' in header.lower() or 'set-cookie' in header.lower():
                print(f"  {header}: {value}")
        
        # Show cookies
        print("\nCookies in Session After Step 1:")
        step1_cookies = []
        if session.cookies:
            for cookie in session.cookies:
                cookie_info = {
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                    'expires': cookie.expires,
                    'secure': cookie.secure,
                    'httponly': cookie.has_nonstandard_attr('HttpOnly')
                }
                step1_cookies.append(cookie_info)
                
                print(f"  Name: {cookie.name}")
                print(f"    Value: {cookie.value[:50]}..." if len(cookie.value) > 50 else f"    Value: {cookie.value}")
                print(f"    Domain: {cookie.domain}")
                print(f"    Path: {cookie.path}")
                print(f"    Expires: {cookie.expires}")
                print(f"    Secure: {cookie.secure}")
                print(f"    HttpOnly: {cookie.has_nonstandard_attr('HttpOnly')}")
                print()
        else:
            print("  ✗ NO COOKIES SET!")
        
        cookies_log.append({
            'step': 'localstorage.json (initial)',
            'cookies': step1_cookies
        })
        
        # Show response content
        print("Response Content:")
        try:
            json_data = response1.json()
            print(f"  {json_data}")
            
            with open(f'{DEBUG_DIR}/step1_localstorage_response.json', 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
            print(f"✓ Saved to: {DEBUG_DIR}/step1_localstorage_response.json")
        except:
            content_preview = response1.text[:500]
            print(f"  {content_preview}...")
            
            with open(f'{DEBUG_DIR}/step1_localstorage_response.txt', 'w', encoding='utf-8') as f:
                f.write(response1.text)
            print(f"✓ Saved to: {DEBUG_DIR}/step1_localstorage_response.txt")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 2: Call login page
    print("\n\n[STEP 2] Calling login page")
    print("-" * 70)
    
    login_url = f"{base_url}/app/login"
    print(f"URL: {login_url}")
    
    try:
        response2 = session.get(login_url)
        print(f"✓ Status Code: {response2.status_code}")
        print(f"✓ Response URL: {response2.url}")
        
        # Show response headers
        print("\nResponse Headers:")
        for header, value in response2.headers.items():
            if 'cookie' in header.lower() or 'set-cookie' in header.lower():
                print(f"  {header}: {value}")
        
        # Show cookies
        print("\nCookies in Session After Step 2:")
        step2_cookies = []
        if session.cookies:
            for cookie in session.cookies:
                cookie_info = {
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                    'expires': cookie.expires,
                    'secure': cookie.secure,
                    'httponly': cookie.has_nonstandard_attr('HttpOnly')
                }
                step2_cookies.append(cookie_info)
                
                print(f"  Name: {cookie.name}")
                print(f"    Value: {cookie.value[:50]}..." if len(cookie.value) > 50 else f"    Value: {cookie.value}")
                print(f"    Domain: {cookie.domain}")
                print(f"    Path: {cookie.path}")
                print(f"    Expires: {cookie.expires}")
                print(f"    Secure: {cookie.secure}")
                print(f"    HttpOnly: {cookie.has_nonstandard_attr('HttpOnly')}")
                print()
        else:
            print("  ✗ STILL NO COOKIES!")
        
        cookies_log.append({
            'step': 'login page',
            'cookies': step2_cookies
        })
        
        # Save login page HTML
        with open(f'{DEBUG_DIR}/step2_login_page.html', 'w', encoding='utf-8') as f:
            f.write(response2.text)
        print(f"✓ Login page saved to: {DEBUG_DIR}/step2_login_page.html")
        
        # Check for cookies in response headers directly
        print("\nChecking Set-Cookie headers directly:")
        set_cookie_headers = response1.headers.get('Set-Cookie', '') + '\n' + response2.headers.get('Set-Cookie', '')
        if set_cookie_headers.strip():
            print(f"  {set_cookie_headers}")
        else:
            print("  ✗ No Set-Cookie headers found")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Save cookies log
    with open(f'{DEBUG_DIR}/cookies_log.json', 'w', encoding='utf-8') as f:
        json.dump(cookies_log, f, indent=2)
    print(f"\n✓ Complete cookies log saved to: {DEBUG_DIR}/cookies_log.json")
    
    # Summary
    print("\n\n[SUMMARY]")
    print("="*70)
    print(f"Total cookies in session: {len(session.cookies)}")
    print(f"Cookie names: {[cookie.name for cookie in session.cookies]}")
    
    if not session.cookies:
        print("\n⚠️  WARNING: No cookies were set!")
        print("\nPossible reasons:")
        print("1. The site may use JavaScript to set cookies")
        print("2. The site may check for specific headers or User-Agent")
        print("3. The site may use a different initial endpoint")
        print("4. The site may require HTTPS with specific TLS settings")
        print("\nNext steps:")
        print("- Try accessing the site in a browser with DevTools open")
        print("- Check the Network tab to see the exact request/response")
        print("- Look for JavaScript that sets cookies")
        print("- Check if cookies are being set via JavaScript (document.cookie)")


if __name__ == "__main__":
    inspect_cookies_detailed()
