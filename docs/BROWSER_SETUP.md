# Browser Setup Guide

This guide will help you set up Selenium with Chrome for the browser-based OFW client.

## Why Use a Browser?

When a website heavily relies on JavaScript (like OFW), using a headless browser provides:

✅ **JavaScript execution** - All dynamic content loads properly  
✅ **Automatic cookie handling** - Browser manages cookies naturally  
✅ **Real user simulation** - Appears as a normal user to the site  
✅ **localStorage/sessionStorage** - Access to browser storage APIs  
✅ **Form auto-fill** - JavaScript validation and form preprocessing  
✅ **Visual debugging** - Can run non-headless to see what's happening  

## Installation

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `selenium` - Browser automation framework
- `webdriver-manager` - Automatically downloads/manages ChromeDriver

### Step 2: Install Chrome Browser

#### Ubuntu/Debian:
```bash
# Download and install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f  # Fix dependencies if needed

# Verify installation
google-chrome --version
```

#### macOS:
```bash
# Using Homebrew
brew install --cask google-chrome

# Or download from: https://www.google.com/chrome/
```

#### Windows:
Download from: https://www.google.com/chrome/

### Step 3: ChromeDriver (Automatic)

The `webdriver-manager` package will automatically download the correct ChromeDriver version for your Chrome browser. No manual setup needed!

If you prefer manual setup, download from: https://chromedriver.chromium.org/

## Quick Test

```python
from ofw_browser_client import OFWBrowserClient

# Test that Selenium is working
with OFWBrowserClient(headless=False) as client:
    client._setup_driver()
    print("✓ Browser setup successful!")
    input("Press Enter to close browser...")
```

## Usage Examples

### Example 1: Basic Login (Headless)

```python
from ofw_browser_client import OFWBrowserClient

client = OFWBrowserClient(headless=True, debug_screenshots=True)

if client.login("username", "password"):
    print("Logged in!")
    session_info = client.get_session_info()
    print(f"Current URL: {session_info['current_url']}")
    
    # Do stuff...
    
    client.logout()
```

### Example 2: Login with Visible Browser (for debugging)

```python
from ofw_browser_client import OFWBrowserClient

# headless=False shows the browser window
client = OFWBrowserClient(headless=False, debug_screenshots=True)

if client.login("username", "password"):
    print("Logged in! Check the browser window.")
    input("Press Enter to continue...")
    
    client.logout()
```

### Example 3: Using Context Manager (Recommended)

```python
from ofw_browser_client import OFWBrowserClient

# Context manager ensures browser is always closed
with OFWBrowserClient(headless=True) as client:
    if client.login("username", "password"):
        # Extract data
        cookies = client.get_cookies()
        local_storage = client.get_local_storage()
        
        # Navigate to messages
        client.navigate_to("https://ofw.ourfamilywizard.com/ofw/messages")
        
        # Get page content
        html = client.get_page_source()
        
# Browser automatically closes when exiting the 'with' block
```

### Example 4: Execute JavaScript

```python
with OFWBrowserClient() as client:
    if client.login("username", "password"):
        # Execute JavaScript to interact with the page
        result = client.execute_script("""
            return {
                title: document.title,
                url: window.location.href,
                cookies: document.cookie
            };
        """)
        print(result)
```

## Troubleshooting

### Chrome/ChromeDriver Version Mismatch

If you see errors about version mismatch:

```bash
# Update Chrome to latest version
# Then webdriver-manager will auto-download matching ChromeDriver
```

Or manually specify ChromeDriver:

```python
from selenium.webdriver.chrome.service import Service

service = Service('/path/to/chromedriver')
# Modify OFWBrowserClient._setup_driver() to use this service
```

### Headless Mode Issues

Some sites detect headless browsers. If you have issues:

1. Try non-headless mode first:
   ```python
   client = OFWBrowserClient(headless=False)
   ```

2. The client already includes anti-detection measures:
   - User-Agent spoofing
   - Automation flag removal
   - CDP commands to hide webdriver

### Chrome Not Found

If Chrome isn't in the default location:

```python
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.binary_location = '/path/to/chrome'
# Modify OFWBrowserClient._setup_driver() to use these options
```

### Permissions Issues (Linux)

```bash
# If Chrome won't start in headless mode
# Add --no-sandbox flag (already included in OFWBrowserClient)

# If using Docker or restricted environment
# You may need to run with --disable-dev-shm-usage (already included)
```

### Debug Screenshots Not Saving

Make sure the `debug/` directory exists and is writable:

```bash
mkdir -p debug
chmod 755 debug
```

## Performance Tips

### Faster Startup

```python
# Disable images to speed up page loads
chrome_options = Options()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
```

### Reduce Memory Usage

```python
# Use headless mode
client = OFWBrowserClient(headless=True)

# Close browser when done
client.logout()
```

### Reuse Browser Session

```python
# Keep browser open between operations
client = OFWBrowserClient()
client.login("username", "password")

# Multiple operations
client.navigate_to("/messages")
# ... do stuff ...
client.navigate_to("/expenses")
# ... do stuff ...

# Close when completely done
client.logout()
```

## Comparison: Requests vs Selenium

| Feature | Requests Library | Selenium Browser |
|---------|-----------------|------------------|
| Speed | ⚡ Fast | 🐌 Slower |
| JavaScript | ❌ No | ✅ Yes |
| Memory | 💚 Low | 🔴 High |
| Setup | ✅ Simple | ⚠️ Requires Chrome |
| Debugging | 📝 HTML only | 👁️ Visual |
| Storage APIs | ❌ No | ✅ Yes |
| User-like | ⚠️ Detectable | ✅ Realistic |

**Recommendation:**
- Use **Selenium** for OFW (JavaScript-heavy site)
- Use **Requests** for simple API endpoints (if OFW adds any)

## Next Steps

1. Run the debug script:
   ```bash
   python debug_browser.py
   ```

2. Choose option 2 to compare what you see with/without JavaScript

3. Choose option 1 to test actual login with visual browser

4. Once working, use `example_browser.py` as a template for your needs

## Advanced: Running in Docker

If you need to run this in a Docker container:

```dockerfile
FROM python:3.11-slim

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your code
COPY . .

# Run headless by default in Docker
ENV HEADLESS=true
```

## Support

Having issues? Check:
1. Chrome version: `google-chrome --version`
2. ChromeDriver compatibility
3. Debug screenshots in `debug/` folder
4. Try non-headless mode to see what's happening
