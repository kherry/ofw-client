# OFW Authentication Flow (Updated)

## Correct Authentication Sequence

```
┌─────────────────────────────────────────────────────────────────┐
│                     COMPLETE AUTH FLOW                          │
└─────────────────────────────────────────────────────────────────┘

1. Browser Login
   ↓ (Selenium handles JavaScript)
   ↓ Cookies obtained
   
2. GET /ofw/appv2/localstorage.json
   ↓ Using browser cookies
   ↓ Response: {"auth": "initial_auth_token", ...}
   
3. Extract Auth Token
   ↓ auth_token = localstorage_data['auth']
   
4. POST /pub/v1/users/iterable/jwt-token?claim=USER_ID
   ↓ Authorization: Bearer <auth_token>
   ↓ Using browser cookies
   ↓ Response: {"token": "jwt_token_here"}
   
5. Base64 Encode JWT Token
   ↓ encoded = base64(jwt_token)
   
6. Set Authorization Header
   ↓ Authorization: Bearer <encoded_jwt_token>
   
7. Cache JWT Token
   ↓ Save to debug/ofw_jwt_token.json
   
8. ✓ Make API Calls
   ↓ All API calls use the encoded JWT token
```

## Key Points

### Two Different Tokens

1. **Auth Token** (from `localstorage.json`)
   - Short-lived initial token
   - Used ONLY to claim the JWT token
   - Found in `localstorage.json` response under `auth` key
   - NOT base64 encoded when used

2. **JWT Token** (from `/jwt-token` endpoint)
   - Long-lived API token
   - Used for ALL API calls
   - Must be base64 encoded before use
   - Can be cached and reused

### Authorization Headers

```python
# Step 1: Get JWT token using auth token
headers = {
    'Authorization': f'Bearer {auth_token}'  # NOT base64 encoded
}
response = POST('/pub/v1/users/iterable/jwt-token?claim=USER_ID')

# Step 2: Use JWT token for API calls
encoded_jwt = base64.b64encode(jwt_token.encode()).decode()
headers = {
    'Authorization': f'Bearer {encoded_jwt}'  # Base64 encoded
}
response = GET('/pub/v1/messageFolders')
```

## Updated Code Flow

### Option 1: From Browser Client (Fastest)

```python
from ofw_browser_client import OFWBrowserClient
from ofw_messages_client import create_from_browser_client

with OFWBrowserClient() as browser:
    browser.login(username, password)
    
    # This will:
    # 1. Get localStorage data (includes auth token)
    # 2. Use auth token to claim JWT
    # 3. Set up API authentication
    client = create_from_browser_client(browser)
    
    messages = client.get_messages()
```

### Option 2: Auto Authentication (Smart Caching)

```python
from ofw_messages_client import create_with_auto_auth

# This will:
# 1. Try cached JWT token first
# 2. If expired, login with browser
# 3. Get auth token from localstorage.json
# 4. Claim new JWT token
# 5. Cache it
client = create_with_auto_auth(username, password)

messages = client.get_messages()
```

### Option 3: Manual Control

```python
from ofw_messages_client import OFWMessagesClient
from ofw_browser_client import OFWBrowserClient

client = OFWMessagesClient()

# Try cached first
if not client.try_cached_token():
    # Need to login
    with OFWBrowserClient() as browser:
        browser.login(username, password)
        
        # Get localStorage data
        localstorage = browser.get_local_storage()
        
        # Use it to authenticate
        client.load_from_browser_client(browser, localstorage)

messages = client.get_messages()
```

## Example: Full Authentication Trace

```python
from ofw_browser_client import OFWBrowserClient
from ofw_messages_client import create_from_browser_client

# Step 1: Browser login
browser = OFWBrowserClient(headless=True)
browser.login("user@email.com", "password")

# Step 2: Get localStorage (after successful login)
localstorage = browser.get_local_storage()
# localstorage = {"auth": "eyJhbGc...", "userId": 123, ...}

# Step 3: Create messages client
client = create_from_browser_client(browser)

# Behind the scenes:
# - Extracts auth token: localstorage['auth']
# - POSTs to /jwt-token with: Authorization: Bearer <auth_token>
# - Gets JWT token: {"token": "xyz..."}
# - Base64 encodes JWT token
# - Sets header: Authorization: Bearer <base64(jwt_token)>
# - Caches JWT token for reuse

# Step 4: Use API
folders = client.get_folders()
messages = client.get_messages()

browser.logout()
```

## What Gets Cached

Only the **JWT token** is cached, not the auth token.

**Cache file:** `debug/ofw_jwt_token.json`
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "encoded": "ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5..."
}
```

The auth token from localstorage.json is NOT cached because:
- It's very short-lived
- It's only needed once (to get JWT token)
- JWT token lasts much longer

## Error Handling

### "No 'auth' field in localstorage.json"

**Cause:** Not fully logged in, or localstorage.json called too early

**Fix:** Make sure browser login is complete before fetching localstorage

```python
browser.login(username, password)
# Wait a moment for any async operations
import time
time.sleep(2)
localstorage = browser.get_local_storage()
```

### "Failed to claim JWT token"

**Cause:** Auth token invalid or expired

**Fix:** Re-login with browser to get fresh auth token

### "Token is expired or invalid" 

**Cause:** Cached JWT token expired

**Fix:** This is handled automatically - just re-run

## Performance Comparison

### Without Caching (Every Run)
```
Browser Login:     ~5 seconds
Get localstorage:  ~0.5 seconds
Claim JWT:         ~0.5 seconds
Total:             ~6 seconds
```

### With Cached JWT Token
```
Load cache:        ~0.01 seconds
Test token:        ~0.3 seconds
Total:             ~0.3 seconds
```

**20x faster** with caching! 🚀

## Testing

Run the test script to see the flow:

```bash
# First run: Full authentication
python test_token_caching.py

# Check what was cached
cat debug/ofw_jwt_token.json

# Second run: Uses cached JWT (instant!)
python test_token_caching.py
```

## Summary

**Old (Incorrect) Flow:**
```
Browser → Cookies → JWT Token (FAILED - missing auth token)
```

**New (Correct) Flow:**
```
Browser → Cookies → localstorage.json → Auth Token → JWT Token → API
```

The key insight is that you need TWO tokens:
1. **Auth token** (from localstorage.json) - to get JWT
2. **JWT token** (from /jwt-token endpoint) - for API calls

Both use `Authorization: Bearer` headers, but only the JWT token needs base64 encoding!
