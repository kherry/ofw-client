# Implementation Guide

This guide will help you get the OFW client working with the actual Our Family Wizard website.

## Step 1: Run the Debug Script

First, run the debugging script to inspect what the login page actually looks like:

```bash
python debug_login.py
```

This will:
1. Call `/ofw/appv2/localstorage.json` to initialize the session
2. Fetch the login page
3. Show you all cookies received at each step
4. Extract any CSRF tokens
5. Show all form fields
6. Save the HTML to `login_page.html`

If no cookies are being set, run the cookie inspector for detailed analysis:

```bash
python inspect_cookies.py
```

## Step 2: Analyze the Login Form

Open the saved `login_page.html` file and look for:

### A. Form field names

Find the login form and check what the actual field names are:

```html
<!-- Example of what you might find: -->
<form action="/app/login" method="POST">
    <input type="text" name="email" id="email" />      <!-- Not 'username'! -->
    <input type="password" name="pwd" id="pwd" />       <!-- Not 'password'! -->
    <input type="hidden" name="_csrf" value="abc123..." />
</form>
```

### B. Session cookie name

From the debug output, note the exact cookie name. It might be:
- `JSESSIONID`
- `sessionid`
- `ofw_session`
- Something else entirely

### C. CSRF token location

Note where the CSRF token is:
- Hidden input field (most common)
- Meta tag
- JavaScript variable
- Cookie value

## Step 3: Update the Code

Based on your findings, you may need to update `ofw_client.py`:

### If field names are different:

In the `login()` method, update the login_data dictionary:

```python
# BEFORE (default):
login_data = {
    'username': username,
    'password': password,
    **hidden_fields
}

# AFTER (if form uses 'email' and 'pwd'):
login_data = {
    'email': username,      # Changed from 'username'
    'pwd': password,         # Changed from 'password'
    **hidden_fields
}
```

### If session cookie has different name:

In the `_get_login_page()` method, add your cookie name:

```python
# Find this section and add your cookie name:
if 'JSESSIONID' in cookies:
    self._session_id = cookies['JSESSIONID']
elif 'sessionid' in cookies:
    self._session_id = cookies['sessionid']
elif 'ofw_session' in cookies:  # ADD YOUR COOKIE NAME HERE
    self._session_id = cookies['ofw_session']
```

### If CSRF token field name is different:

In the `login()` method, update the CSRF field names:

```python
# Add the correct field name based on the HTML:
if self._csrf_token:
    login_data['_csrf'] = self._csrf_token  # Use the actual field name from the form
```

## Step 4: Test the Login

Run the example usage script:

```bash
python example_usage.py
```

Or use the config manager for easier credential handling:

```bash
# Create a .env file first:
echo "OFW_USERNAME=your_username" > .env
echo "OFW_PASSWORD=your_password" >> .env

# Then run:
python config_manager.py
```

## Step 5: Verify Success

A successful login should:
1. Return `True` from the `login()` method
2. Show "Login successful!" message
3. Display session information with cookies
4. Redirect to a URL containing 'dashboard' or 'home'

## Common Issues and Solutions

### Issue: No cookies being set

**Solution**: The site requires a specific initialization sequence. Make sure:

1. The `localstorage.json` endpoint is called first
2. Cookies from that call are preserved for subsequent requests
3. Check if cookies are being set via JavaScript instead of HTTP headers

**Debug steps**:
```bash
python inspect_cookies.py
```

This will show you:
- Exactly which cookies are set at each step
- Cookie attributes (domain, path, secure, httponly)
- Whether Set-Cookie headers are present

**Check browser behavior**:
1. Open browser DevTools (F12)
2. Go to Network tab
3. Visit https://ofw.ourfamilywizard.com/app/login
4. Look at the first few requests
5. Check the Cookies tab for each request
6. See if cookies are set via JavaScript (Application → Cookies)

### Issue: "Login failed" with no error

**Solution**: The form might require JavaScript execution. Check if there's any JS that modifies the form data before submission.

**Workaround**: Use browser developer tools to capture the actual POST request:
1. Open browser DevTools (F12)
2. Go to Network tab
3. Login manually
4. Find the POST request
5. Copy the exact payload and headers
6. Replicate in the code

### Issue: CSRF token not found

**Solution**: Check these locations in the HTML:
```html
<!-- Hidden input -->
<input type="hidden" name="_csrf" value="token_here" />

<!-- Meta tag -->
<meta name="csrf-token" content="token_here" />

<!-- JavaScript variable -->
<script>
var csrfToken = "token_here";
</script>

<!-- Cookie -->
<!-- Check if it's in document.cookie -->
```

### Issue: Login succeeds but subsequent requests fail

**Solution**: You might need to include additional headers or tokens. Use browser DevTools to see what headers are sent with authenticated requests.

Common required headers:
```python
self.session.headers.update({
    'X-CSRF-Token': self._csrf_token,
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://ofw.ourfamilywizard.com/app/login'
})
```

### Issue: Session expires quickly

**Solution**: The site might require periodic keep-alive requests. Add a method:
```python
def keep_alive(self):
    """Send a keep-alive request to maintain the session."""
    try:
        self.session.get(f"{self.BASE_URL}/app/ping")
    except:
        pass
```

## Step 6: Extend the Library

Once login works, you can add more functionality:

### Reading Messages

```python
def get_messages(self, page: int = 1) -> list:
    """Get messages from OFW."""
    if not self.is_authenticated:
        raise Exception("Not authenticated")
    
    url = f"{self.BASE_URL}/app/messages?page={page}"
    response = self.session.get(url)
    
    # Parse the response
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract messages...
    
    return messages
```

### Creating Expenses

```python
def create_expense(self, amount: float, category: str, 
                   description: str, date: str) -> bool:
    """Create a new expense."""
    if not self.is_authenticated:
        raise Exception("Not authenticated")
    
    expense_data = {
        'amount': amount,
        'category': category,
        'description': description,
        'date': date,
        '_csrf': self._csrf_token  # Include CSRF token
    }
    
    url = f"{self.BASE_URL}/app/expenses/create"
    response = self.session.post(url, data=expense_data)
    
    return response.status_code == 200
```

## Step 7: Add Error Handling

Improve robustness with better error handling:

```python
def login(self, username: str, password: str, max_retries: int = 3) -> bool:
    """Login with retry logic."""
    for attempt in range(max_retries):
        try:
            # Login logic here...
            return True
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
        except Exception as e:
            logger.error(f"Login attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                return False
    return False
```

## Testing Tips

1. **Use a test account**: Don't test with your primary account
2. **Log everything**: Keep detailed logs during development
3. **Check rate limits**: Don't make too many requests too quickly
4. **Respect ToS**: Ensure your usage complies with OFW's terms of service

## Next Steps

Once you have login working:
1. Map out all the endpoints you need (messages, expenses, calendar, etc.)
2. Create methods for each endpoint
3. Add proper error handling and validation
4. Write tests
5. Document the API

Good luck! 🚀
