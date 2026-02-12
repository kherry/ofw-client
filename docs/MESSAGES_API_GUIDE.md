# OFW Messages API Guide

Now that you can successfully login with the browser client, you can use the **OFW Messages Client** to interact with the OFW API using standard HTTP requests!

## How It Works

```
1. Login with Browser Client
   ↓ (Executes JavaScript, handles cookies)
   
2. Extract Cookies from Browser
   ↓ (browser.get_cookies())
   
3. Load Cookies into Requests Session
   ↓ (messages_client.load_cookies_from_browser())
   
4. Use API Endpoints with Requests
   ↓ (GET /pub/v1/messageFolders, etc.)
   
✓ Full API access with authenticated session!
```

## Quick Start

### Option 1: Complete Workflow (Recommended)

```bash
python example_complete_workflow.py
```

This interactive script:
1. Logs in with browser
2. Shows all folders
3. Lets you select a folder
4. Fetches messages
5. Saves everything to JSON files

### Option 2: Quick Helper Functions

```python
from ofw_quick_helpers import quick_login_and_get_messages

# Get messages in one line
messages = quick_login_and_get_messages("username", "password")

for msg in messages:
    print(f"{msg['author']['name']}: {msg['subject']}")
```

### Option 3: Manual Control

```python
from ofw_browser_client import OFWBrowserClient
from ofw_messages_client import create_from_browser_client

# Step 1: Login with browser
with OFWBrowserClient(headless=True) as browser:
    browser.login("username", "password")
    
    # Step 2: Create messages client
    client = create_from_browser_client(browser)
    
    # Step 3: Use API
    folders = client.get_folders()
    messages = client.get_messages()
```

## API Reference

### OFWMessagesClient

#### Authentication

```python
from ofw_messages_client import OFWMessagesClient

client = OFWMessagesClient()

# Option 1: Load from browser client
client.load_cookies_from_browser(browser.get_cookies())

# Option 2: Load from saved cookies file
import json
with open('cookies.json') as f:
    cookies = json.load(f)
client.load_cookies_from_browser(cookies)
```

#### Get Folders

```python
# Get all folders with counts
folders_data = client.get_folders(include_counts=True)

# Returns:
{
    "systemFolders": [
        {
            "id": 12341234,
            "name": "Inbox",
            "folderOrder": 1,
            "totalMessageCount": 5000,
            "unreadMessageCount": 12,
            "folderType": "INBOX"
        },
        {
            "id": 12345789,
            "name": "Action Items",
            "folderOrder": 2,
            "totalMessageCount": 8,
            "unreadMessageCount": 0,
            "folderType": "ACTION_ITEMS"
        }
    ],
    "userFolders": []
}

# Get flat list of all folders
all_folders = client.list_folders()

# Get just the inbox ID
inbox_id = client.get_inbox_id()
```

#### Get Messages

```python
# Get messages from inbox (default)
data = client.get_messages()

# Get messages from specific folder
data = client.get_messages(folder_id=12341234)

# Pagination
data = client.get_messages(
    folder_id=12341234,
    page=1,           # Page number (1-based)
    size=50,          # Messages per page (max 50)
    sort='date',      # Sort field
    sort_direction='desc'  # 'asc' or 'desc'
)

# Returns:
{
    "metadata": {
        "page": 1,
        "count": 50,
        "first": True,
        "last": False
    },
    "data": [
        {
            "id": 987654321,
            "folder": 12341234,
            "subject": "Re: Doctor appointment",
            "preview": "I can take her at 3pm...",
            "read": False,
            "author": {
                "userId": 1011010,
                "name": "John Doe",
                "firstName": "John",
                "lastName": "Doe"
            },
            "date": {
                "displayDate": "2/12/2026",
                "displayTime": "12:00 AM",
                "dateTime": "2026-02-12T00:00:00"
            },
            "recipients": [...]
        }
    ]
}

# Get ALL messages from a folder (fetches all pages)
all_messages = client.get_all_messages(folder_id=12341234)

# Limit pages
all_messages = client.get_all_messages(folder_id=12341234, max_pages=5)
```

#### Display Functions

```python
# Print folders nicely
client.print_folders()
# Output:
# [14381170] Inbox
#   Type: System
#   Messages: 45 total, 12 unread
#   Folder Type: INBOX

# Print messages nicely
messages = client.get_messages()
client.print_messages(messages['data'], limit=10)
# Output:
# [1] Message ID: 987654321
#   From: John Doe
#   To: Jane Smith
#   Subject: Re: Doctor appointment
#   Date: Wed, Feb 12, 12:00 AM
#   Preview: I can take her at 3pm...
#   Status: Unread
```

## Message Data Structure

Each message contains:

```python
{
    "id": 987654321,                    # Unique message ID
    "folder": 12341234,                 # Folder ID
    "draft": False,                     # Is this a draft?
    "subject": "Re: Doctor appointment", # Subject line
    "preview": "I can take her...",     # First ~100 chars
    "files": 2,                         # Number of attachments
    "read": False,                      # Has been read?
    "replied": False,                   # Has been replied to?
    "canReply": True,                   # Can reply to this?
    
    "author": {
        "userId": 1011010,
        "name": "John Doe",
        "firstName": "John",
        "lastName": "Doe",
        "displayInitials": "JD",
        "active": True,
        "color": "#66AA00"              # UI color
    },
    
    "date": {
        "displayDate": "2/12/2026",
        "displayTime": "12:00 AM",
        "dateTime": "2026-02-12T00:00:00",
        "yesterdayTodayTomorrow": "Today",
        "threeCharMonth": "Feb 12, 2026",
        # ... many date format options
    },
    
    "recipients": [
        {
            "user": {
                "userId": 1000111,
                "name": "Jane Smith",
                "firstName": "Jane",
                "lastName": "Smith"
            }
        }
    ]
}
```

## Quick Helper Functions

For common tasks, use the helper functions:

```python
from ofw_quick_helpers import *

# Get unread counts
counts = get_unread_message_count(username, password)
# Returns: {"Inbox": 7250, "Action Items": 5, ...}

# Get messages quickly
messages = quick_login_and_get_messages(username, password)

# Get folders quickly
folders = quick_login_and_get_folders(username, password)

# Save cookies for reuse
save_cookies_for_reuse(username, password, "my_cookies.json")

# Search messages
messages = search_messages_by_subject(username, password, "doctor")
```

## Saving and Reusing Cookies

Cookies can be saved to avoid logging in every time:

```python
# Save cookies once
from ofw_quick_helpers import save_cookies_for_reuse
save_cookies_for_reuse("username", "password", "ofw_cookies.json")

# Later, reuse them
from ofw_messages_client import OFWMessagesClient
import json

client = OFWMessagesClient()
with open("ofw_cookies.json") as f:
    cookies = json.load(f)
client.load_cookies_from_browser(cookies)

# Now use the client
messages = client.get_messages()
```

**Note:** Cookies expire! You'll need to re-login when they expire.

## Common Use Cases

### 1. Check for New Messages

```python
from ofw_quick_helpers import get_unread_message_count

counts = get_unread_message_count(username, password)
total_unread = sum(counts.values())

if total_unread > 0:
    print(f"You have {total_unread} unread messages!")
```

### 2. Get All Messages from Last Week

```python
from datetime import datetime, timedelta
from ofw_messages_client import create_from_browser_client
from ofw_browser_client import OFWBrowserClient

with OFWBrowserClient() as browser:
    browser.login(username, password)
    client = create_from_browser_client(browser)
    
    all_messages = client.get_all_messages()
    
    # Filter by date
    one_week_ago = datetime.now() - timedelta(days=7)
    recent = [
        msg for msg in all_messages
        if datetime.fromisoformat(msg['date']['dateTime']) > one_week_ago
    ]
    
    print(f"Found {len(recent)} messages from last week")
```

### 3. Find Messages from Specific Person

```python
all_messages = client.get_all_messages()

from_john = [
    msg for msg in all_messages
    if msg['author']['name'] == 'John Doe'
]

for msg in from_john:
    print(f"{msg['date']['displayDate']}: {msg['subject']}")
```

### 4. Export All Messages to CSV

```python
import csv
from ofw_messages_client import create_from_browser_client
from ofw_browser_client import OFWBrowserClient

with OFWBrowserClient() as browser:
    browser.login(username, password)
    client = create_from_browser_client(browser)
    
    all_messages = client.get_all_messages()
    
    with open('messages.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'id', 'date', 'from', 'to', 'subject', 'preview', 'read'
        ])
        writer.writeheader()
        
        for msg in all_messages:
            recipients = ', '.join([r['user']['name'] for r in msg['recipients']])
            writer.writerow({
                'id': msg['id'],
                'date': msg['date']['dateTime'],
                'from': msg['author']['name'],
                'to': recipients,
                'subject': msg['subject'],
                'preview': msg['preview'],
                'read': msg['read']
            })
    
    print(f"✓ Exported {len(all_messages)} messages to messages.csv")
```

## Error Handling

```python
from ofw_messages_client import OFWMessagesClient

try:
    client = OFWMessagesClient()
    client.load_cookies_from_browser(cookies)
    
    folders = client.get_folders()
    messages = client.get_messages()
    
except Exception as e:
    print(f"Error: {e}")
    # Cookies might have expired - need to re-login
```

## API Endpoints Reference

These are the endpoints used by the client:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/pub/v1/messageFolders` | GET | Get all folders |
| `/pub/v3/messages` | GET | Get messages from folder |

Query parameters for messages:
- `folders` - Folder ID (required)
- `page` - Page number (default: 1)
- `size` - Results per page (max: 50)
- `sort` - Sort field (default: 'date')
- `sortDirection` - 'asc' or 'desc' (default: 'desc')

## Next Steps

Now that you can fetch messages, you can extend this to:
1. **Send messages** - POST to `/pub/v3/messages`
2. **Mark as read** - Update message status
3. **Delete messages** - Delete endpoint
4. **Get message details** - Full message body
5. **Download attachments** - File endpoints

The pattern is the same:
1. Login with browser to get cookies
2. Use cookies with requests to call API endpoints

---

**Pro Tip:** Run the complete workflow example to see everything in action:
```bash
python example_complete_workflow.py
```
