# OFW Login Flow - Quick Reference

## Updated Login Sequence

Based on analysis of the actual OFW site, here's the complete flow:

### Step-by-Step Flow

```
1. GET /ofw/appv2/localstorage.json
   ↓ (Sets session cookies)
   ↓ (Returns empty or minimal JSON)
   
2. GET /app/login
   ↓ (Using cookies from step 1)
   ↓ (Extract CSRF token and form data)
   
3. POST /app/login
   ↓ (With: submit=Sign-In, _eventId=submit, username=..., password=...)
   ↓ (May redirect via HTTP or JavaScript)
   ↓ (Redirects handled: /ofw/home.form → /ofw/appv2/home.form)
   
4. Page loads with authenticated content
   ↓ (JavaScript may handle routing)
   ↓ (Check for: div#greeting and div#notificationsSection)
   
5. GET /ofw/appv2/localstorage.json (again, asynchronously)
   ↓ (This time returns populated JSON with user data)
   
6. ✓ Authenticated!
```

## Success Detection

**Instead of relying on URL redirects** (which may be JavaScript-based), we check for these elements on the page:

✅ `<div id="greeting">` - User greeting/welcome message  
✅ `<div id="notificationsSection">` - Notifications section  

**Both elements must be present** for login to be considered successful.

## What Each Endpoint Does

### `/ofw/appv2/localstorage.json` (Initial)
- **Purpose**: Initialize the session
- **Method**: GET
- **Returns**: Empty JSON `{}` or minimal data
- **Sets**: Session cookies (JSESSIONID or similar)
- **Must**: Be called FIRST before accessing any other page

### `/app/login` (GET)
- **Purpose**: Get the login form
- **Method**: GET
- **Requires**: Cookies from localstorage.json
- **Returns**: HTML with login form
- **Contains**: CSRF token, hidden fields

### `/app/login` (POST)
- **Purpose**: Submit credentials
- **Method**: POST
- **Required Fields**:
  - `submit=Sign-In`
  - `_eventId=submit`
  - `username=<your_username>`
  - `password=<your_password>`
  - Any other hidden fields from the form
- **Redirects**: 
  1. `/ofw/home.form` (empty response, sets cookies)
  2. `/ofw/appv2/home.form` (empty response, sets cookies)
- **Final Status**: 200 OK at `/ofw/appv2/home.form`

### `/ofw/appv2/localstorage.json` (Post-Login)
- **Purpose**: Get user configuration/data
- **Method**: GET (called asynchronously after landing on home)
- **Returns**: Populated JSON with user data, settings, etc.
- **When**: After successful login redirect chain

## Updated Code Structure

The `OFWClient` class now has:

```python
class OFWClient:
    def _initialize_session(self):
        # Calls localstorage.json
        # Sets session cookies
        
    def _get_login_page(self):
        # Calls /app/login (GET)
        # Uses cookies from _initialize_session()
        
    def login(username, password):
        # 1. Calls _initialize_session()
        # 2. Calls _get_login_page()
        # 3. Extracts CSRF token
        # 4. POSTs credentials
        # 5. Verifies success
```

## Debugging Tools

### 1. Main Debugger (`debug_login.py`)
```bash
python debug_login.py
```
Shows the complete flow with cookies at each step.

### 2. Cookie Inspector (`inspect_cookies.py`)
```bash
python inspect_cookies.py
```
Detailed cookie analysis with attributes.

### 3. Manual Testing
```bash
python example_usage.py
```
Test actual login with your credentials.

## Common Cookie Names to Check

The session cookie might be named:
- `JSESSIONID` (Java servers - most likely)
- `sessionid`
- `session`
- `sid`
- `ofw_session`
- Custom name specific to OFW

Run the cookie inspector to see the actual name!

## Troubleshooting

### No cookies after localstorage.json?

Possible causes:
1. **JavaScript sets cookies**: The endpoint might return JavaScript that sets cookies via `document.cookie`
2. **Wrong domain**: Cookies might be set for a different subdomain
3. **Redirects**: The endpoint might redirect, and cookies are set in the redirect
4. **Headers required**: Might need specific headers (User-Agent, Accept, etc.)

### Cookies set but login fails?

Check:
1. Cookie is being sent with login request
2. CSRF token is correctly extracted
3. Form field names match actual form
4. No JavaScript preprocessing of form data

## Next Steps After This Works

Once login succeeds, you can extend the library:

```python
# Message endpoints (examples)
GET /app/messages → List messages
GET /app/messages/{id} → Get message details  
POST /app/messages/send → Send message

# Expense endpoints (examples)
GET /app/expenses → List expenses
POST /app/expenses/create → Create expense
GET /app/expenses/{id} → Get expense details

# Calendar endpoints (examples)
GET /app/calendar → Get calendar
POST /app/calendar/event → Create event
```

Use the authenticated session (`client.session`) to make these requests!

## Testing Checklist

- [ ] Run `python inspect_cookies.py`
- [ ] Verify cookies are set after localstorage.json
- [ ] Check cookie names and values
- [ ] Run `python debug_login.py`
- [ ] Verify CSRF token is found
- [ ] Check form field names
- [ ] Test login with `python example_usage.py`
- [ ] Verify successful redirect after login
- [ ] Check authenticated session works for other endpoints

---

**Remember**: Always test responsibly and respect OFW's Terms of Service!
