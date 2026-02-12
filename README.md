# Our Family Wizard Python Client - v0.3.0

## What is this
This is a tool to interact with OFW in an automated and repeatable manner to do things such as read messages, 
expenses, calendar events, and journal check-ins and mentions. I began by reverse engineering the OFW 
application network calls and created a login client. Once this was successful, I built an API client to 
retrieve message folders and messages. This is a proof of concept and may break at any moment. Please keep in
mind this may violate Our Family Wizard's terms of service, so consider using my [`ofw-server`](https://github.com/kherry/ofw-server) and 
`ofw-extension` projects for testing and using this client. `ofw-extension` is a chrome and firefox browser
plugin, which can be used to pull data from the official Our Family Wizard application and store data locally
using the [`ofw-server`](https://github.com/kherry/ofw-server) project.

## 🎉 NEW: Browser Automation Support!

Since OFW is JavaScript-heavy, we now support **Selenium with headless Chrome** for full JavaScript execution.

## What You Have

### Two Approaches Available:

1. **🌐 Browser Client (RECOMMENDED)** - Uses Selenium
   - ✅ Executes JavaScript
   - ✅ Handles dynamic content
   - ✅ Access to localStorage/sessionStorage
   - ✅ Visual debugging (non-headless mode)
   - ✅ Auto-detects form fields after JS renders
   
2. **📡 Requests Client** - Pure HTTP requests
   - ⚡ Faster
   - 💚 Lower memory
   - ❌ No JavaScript execution
   - ⚠️ May not work if login requires JS

3. **🔀 Hybrid Client** - Intelligently uses both
   - Automatically chooses the best approach
   - Falls back to browser when needed

## Files Included

### Core Clients
- **`ofw_browser_client.py`** ⭐ NEW - Selenium-based browser automation
- **`ofw_client.py`** - Requests-based client
- **`ofw_hybrid_client.py`** ⭐ NEW - Smart hybrid approach

### Usage Examples
- **`example_complete_workflow.py`** ⭐ NEW - CLI example using Login, Folder List, Messages API calls
- **`example_browser.py`** ⭐ NEW - Browser client example
- **`example_usage.py`** - Requests client example
- **`config_manager.py`** - Secure credential management

### Debug Tools
- **`debug_browser.py`** ⭐ NEW - Browser-based debugging
  - Interactive login test
  - Compare JS vs non-JS rendering
  - Visual browser window
- **`debug_login.py`** - Requests-based debugging
- **`inspect_cookies.py`** - Detailed cookie analysis

### Documentation
- **`BROWSER_SETUP.md`** ⭐ NEW - Complete browser setup guide
- **`README.md`** - Main documentation
- **`IMPLEMENTATION_GUIDE.md`** - Step-by-step implementation
- **`QUICK_REFERENCE.md`** - Quick reference for login flow
- **`CHANGELOG.md`** - Version history
- **`requirements.txt`** - Updated with Selenium dependencies

## Quick Start (Browser Mode - RECOMMENDED)

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Chrome browser (if not already installed)
# Ubuntu/Debian:
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb

# macOS:
brew install --cask google-chrome

# Windows: Download from https://www.google.com/chrome/
```

### 2. Test It Out

```bash
# Run the demo workflow
python example_complete_workflow.py
```
Provide your credentials to login, then use the menu to select a folder and read messages. Or
you can view the login process in real time:

```bash
# Run the browser debug tool (with visible browser window)
python debug_browser.py
```

Choose option 1 to test login with a visible browser window - you'll see exactly what's happening!

### 3. Use in Your Code

```python
from ofw_browser_client import OFWBrowserClient

# Use context manager (automatically closes browser)
with OFWBrowserClient(headless=True, debug_screenshots=True) as client:
    if client.login("username", "password"):
        print("Logged in!")
        
        # Get session data
        cookies = client.get_cookies()
        local_storage = client.get_local_storage()
        
        # Navigate to pages
        client.navigate_to("https://ofw.ourfamilywizard.com/ofw/messages")
        
        # Get page content
        html = client.get_page_source()
        
        # Execute JavaScript
        data = client.execute_script("return localStorage;")

# Browser automatically closes
```
# Key Features of Browser Client

### 🎯 Automatic JavaScript Execution
All the JavaScript that runs on the OFW site will run automatically:
- Form validation
- Dynamic form fields
- AJAX calls to localstorage.json
- Client-side routing
- React/Vue/Angular components

### 🍪 Complete Cookie & Storage Access
```python
cookies = client.get_cookies()              # Browser cookies
local_storage = client.get_local_storage()  # localStorage data
session_storage = client.get_session_storage()  # sessionStorage data
```

### 📸 Visual Debugging
Run in non-headless mode to see what's happening:
```python
client = OFWBrowserClient(headless=False, debug_screenshots=True)
```

Screenshots saved automatically at each step:
- `debug/01_login_page_loaded.png`
- `debug/02_credentials_entered.png`
- `debug/03_login_error.png` (if error)
- `debug/04_after_login.png`

### 🔍 Page Interaction
```python
# Find elements
element = client.find_element(By.CSS_SELECTOR, ".message")

# Execute JavaScript
result = client.execute_script("""
    return document.querySelector('.username').textContent;
""")

# Navigate
client.navigate_to("/messages")
```

## Why Browser Mode for OFW?

The OFW website likely:
1. ✅ Renders the login form with JavaScript
2. ✅ Validates credentials client-side
3. ✅ Makes AJAX calls during login
4. ✅ Stores session data in localStorage
5. ✅ Uses client-side routing after login

All of these require JavaScript execution, which the browser client handles perfectly.

## Comparison: Requests vs Browser

| Feature | Requests Client | Browser Client |
|---------|----------------|----------------|
| JavaScript | ❌ | ✅ |
| Speed | ⚡ Very Fast | 🐌 Slower (2-5s) |
| Memory | 💚 ~50MB | 🔴 ~200MB |
| Setup | ✅ pip install | ⚠️ Needs Chrome |
| Debug | 📝 HTML only | 👁️ Visual + Screenshots |
| Storage APIs | ❌ | ✅ localStorage/sessionStorage |
| Detection | ⚠️ Easily detected | ✅ Looks like real user |

## Troubleshooting

### Browser won't start
```bash
# Check Chrome is installed
google-chrome --version

# If not found, install it (see BROWSER_SETUP.md)
```

### Login fails in browser
```bash
# Run with visible browser to see what's happening
python debug_browser.py
# Choose option 1 for interactive test
```

### Version mismatch errors
```bash
# Update Chrome to latest, then webdriver-manager 
# will auto-download the matching ChromeDriver
```

### Cookie Inspector
```bash
python inspect_cookies.py
```

This provides detailed cookie analysis:
- Shows cookies after each request
- Displays cookie attributes (domain, path, expires, secure, httponly)
- Analyzes Set-Cookie headers
- Helps diagnose cookie-related issues

## Understanding the Session ID

The session ID is  stored in the `SESSION` cookie

The library automatically detects and stores this for you.

### Session Cookie Issues

If the session isn't persisting:

1. Check which cookies are being set (use debug script)
2. Verify the cookie domain matches
3. Ensure `allow_redirects=True` is set for login POST

## Advanced Usage

### Custom Session Headers

```python
client = OFWClient()
client.session.headers.update({
    'Custom-Header': 'value'
})
```

### Accessing Session Info

```python
session_info = client.get_session_info()
print(session_info)
# {
#     'authenticated': True,
#     'session_id': 'ABC123...',
#     'csrf_token': 'XYZ789...',
#     'cookies': {...}
# }
```

### Using Session for Custom Requests

Once logged in, you can use the authenticated session:

```python
if client.is_authenticated:
    # Make authenticated requests
    response = client.session.get('https://ofw.ourfamilywizard.com/app/messages')
    # Process response...
```

## Next Steps

### 1. Test Login
```bash
python example_browser.py
```

### 2. Explore Debug Tools
```bash
python debug_browser.py
```

### 3. Build Your Features

Once logged in, you can:

```python
with OFWBrowserClient() as client:
    client.login(username, password)
    
    # Navigate to messages
    client.navigate_to("https://ofw.ourfamilywizard.com/ofw/messages")
    
    # Get messages using JavaScript
    messages = client.execute_script("""
        // Your JS code to extract messages
        return Array.from(document.querySelectorAll('.message')).map(m => ({
            sender: m.querySelector('.sender').textContent,
            text: m.querySelector('.text').textContent,
            date: m.querySelector('.date').textContent
        }));
    """)
    
    # Or parse the HTML
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(client.get_page_source(), 'html.parser')
    # Extract data...
```

## Advanced: Hybrid Mode

Use the hybrid client for maximum flexibility:

```python
from ofw_hybrid_client import OFWHybridClient

# Auto mode: intelligently chooses browser or requests
with OFWHybridClient(mode='auto') as client:
    client.login(username, password)
    # Client automatically used browser mode for OFW
```

## What's Next

With a working browser-based login, you can now:

1. **Extract Messages** - Navigate to messages page, parse HTML or use JS
2. **Send Messages** - Fill form fields and submit
3. **Read Expenses** - Navigate to expenses, extract data
4. **Create Expenses** - Fill expense form and submit
5. **Access Calendar** - View and create events
6. **Upload Files** - Use file inputs in browser

All with full JavaScript support! 🚀

## Performance Tips

### For Development
```python
# Use visible browser to see what's happening
client = OFWBrowserClient(headless=False, debug_screenshots=True)
```

### For Production
```python
# Use headless mode for speed
client = OFWBrowserClient(headless=True, debug_screenshots=False)
```

### Reuse Browser
```python
# Don't create new browser for each operation
client = OFWBrowserClient()
client.login(username, password)

# Multiple operations
client.navigate_to("/messages")
# ... extract messages ...

client.navigate_to("/expenses")
# ... extract expenses ...

# Close when done
client.logout()
```



## License

MIT License - See LICENSE file for details

## Disclaimer

This is an unofficial library and is not affiliated with or endorsed by Our Family Wizard. Use at your own risk and ensure you comply with the Our Family Wizard Terms of Service.

## Support

Need help?
1. Check `BROWSER_SETUP.md` for installation issues
2. Run `debug_browser.py` to see what's happening
3. Check screenshots in `debug/` folder
4. Review saved HTML files in `debug/`

For issues or questions, please open an issue on the repository.

## Contributing

Contributions welcome! Please ensure:
- Code follows existing style
- Add tests for new features
- Update documentation

Reference the issue in the pull request

---

**Version:** 0.3.0  
**Last Updated:** 2025-02-11  
**Status:** ✅ Browser support fully implemented
