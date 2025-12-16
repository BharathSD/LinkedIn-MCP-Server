# LinkedIn MCP Server Setup Guide (Session Cookie Method)

This guide uses your LinkedIn session cookie - **NO company page or app approval needed!**

## What You'll Need

- Python 3.10 or higher
- Claude Desktop installed
- A LinkedIn account (free or premium)

---

## Step 1: Get Your LinkedIn Session Cookie

Your session cookie (`li_at`) is what keeps you logged into LinkedIn. Here's how to find it:

### Chrome / Edge / Brave

1. Go to [linkedin.com](https://linkedin.com) and make sure you're logged in
2. Press `F12` to open Developer Tools
3. Click the **Application** tab (or **Storage** in some browsers)
4. In the left sidebar, expand **Cookies** → `https://www.linkedin.com`
5. Look for the cookie named **`li_at`**
6. Double-click the **Value** column and copy the entire value (it's a long string)

### Firefox

1. Go to [linkedin.com](https://linkedin.com) and make sure you're logged in
2. Press `F12` to open Developer Tools
3. Click the **Storage** tab
4. Expand **Cookies** → `https://www.linkedin.com`
5. Find **`li_at`** and copy its value

### Safari

1. Enable Developer Menu: Safari → Settings → Advanced → Show Develop menu
2. Go to [linkedin.com](https://linkedin.com) and log in
3. Develop → Show Web Inspector → Storage tab
4. Find Cookies → `linkedin.com` → `li_at`
5. Copy the value

**Important:** This cookie is like your password - keep it secret! It expires when you log out or after ~1 year.

---

## Step 2: Clone the repository and setup server

### Clone the repository

```bash
mkdir ~/linkedin-mcp-server
cd ~/linkedin-mcp-server
```

### Install Dependencies

Create `requirements.txt`:

```
mcp>=0.9.0
httpx>=0.27.0
```

Install:

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install mcp httpx
```

---

## Step 3: Configure Claude Desktop

### macOS

1. Open or create the config file:
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

2. Add this configuration:
```json
{
  "mcpServers": {
    "linkedin": {
      "command": "python3",
      "args": ["/Users/YOUR_USERNAME/linkedin-mcp-server/server.py"],
      "env": {
        "LINKEDIN_SESSION_COOKIE": "paste_your_li_at_cookie_value_here"
      }
    }
  }
}
```

**Replace:**
- `YOUR_USERNAME` with your actual username
- `paste_your_li_at_cookie_value_here` with your `li_at` cookie value

### Windows

1. Create or edit the config file at:
```
%APPDATA%\Claude\claude_desktop_config.json
```

2. Add this configuration:
```json
{
  "mcpServers": {
    "linkedin": {
      "command": "python",
      "args": ["C:\\Users\\YOUR_USERNAME\\linkedin-mcp-server\\server.py"],
      "env": {
        "LINKEDIN_SESSION_COOKIE": "paste_your_li_at_cookie_value_here"
      }
    }
  }
}
```

### Linux

1. Create or edit:
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

2. Add:
```json
{
  "mcpServers": {
    "linkedin": {
      "command": "python3",
      "args": ["/home/YOUR_USERNAME/linkedin-mcp-server/server.py"],
      "env": {
        "LINKEDIN_SESSION_COOKIE": "paste_your_li_at_cookie_value_here"
      }
    }
  }
}
```

---

## Step 4: Test the Connection

1. **Completely quit Claude Desktop** (not just close the window)
   - macOS: Cmd+Q
   - Windows: Right-click taskbar icon → Exit
   
2. **Restart Claude Desktop**

3. **Open a new conversation**

4. Look for the 🔌 icon at the bottom - this means MCP tools are connected!

5. **Try it out:**
   - "Can you get my LinkedIn profile?"
   - "Search for software engineer jobs in San Francisco"
   - "Who are my recent LinkedIn connections?"

---

## Available Commands

Once connected, you can ask Claude to:

| Command | What it does |
|---------|-------------|
| **get_my_profile** | Get your complete profile with experience, education, skills |
| **get_profile_by_url** | View any public LinkedIn profile |
| **search_profiles** | Search for people by name, title, company |
| **search_jobs** | Find job postings by keywords and location |
| **get_my_connections** | See your LinkedIn connections |
| **get_feed** | View recent posts from your feed |

---

## Example Prompts

```
"Show me my LinkedIn profile"

"Get the profile of linkedin.com/in/satyanadella"

"Search for AI researchers at Google"

"Find remote software engineer jobs"

"Show me my recent connections"

"What's in my LinkedIn feed today?"
```

---

## Troubleshooting

### ❌ "Session cookie not set" error

- Make sure you copied the entire `li_at` cookie value
- Check there are no extra spaces or quotes
- The cookie value should be ~200+ characters long

### ❌ Server not showing up in Claude

1. Check the file path is correct and absolute (full path, not `~/`)
2. Verify Python is installed: `python3 --version` or `python --version`
3. Check the config file is valid JSON (use [jsonlint.com](https://jsonlint.com))
4. Look at Claude logs:
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`

### ❌ "Cookie expired" or authentication errors

Your session cookie may have expired. This happens if:
- You logged out of LinkedIn
- LinkedIn detected unusual activity
- The cookie is ~1 year old

**Solution:** Get a fresh cookie:
1. Log into LinkedIn again
2. Get the new `li_at` cookie value (Step 1)
3. Update `claude_desktop_config.json`
4. Restart Claude Desktop

### ❌ Rate limiting errors

LinkedIn may temporarily limit requests if you make too many too quickly. Wait a few minutes and try again.

---

## Security Best Practices

⚠️ **Important Security Notes:**

1. **Never share your `li_at` cookie** - it's equivalent to your password
2. **Don't commit it to Git** - add `claude_desktop_config.json` to `.gitignore`
3. **Cookie expires when you log out** - you'll need to get a new one
4. **Use only on your personal computer** - don't use on shared/public computers
5. **Monitor your LinkedIn session** - LinkedIn will show active sessions in Settings

---

## Advantages Over Official API

✅ No company page required  
✅ No app approval process  
✅ No waiting period  
✅ Works immediately  
✅ Access your personal data  
✅ View any public profiles  
✅ Free - no API costs  

---

## Need Help?

Common issues:

1. **Python not found**: Install Python from [python.org](https://python.org)
2. **Path issues on Windows**: Use double backslashes `\\` in paths
3. **Permission denied**: Make sure the file is readable
4. **Module not found**: Run `pip install mcp httpx` again

Still stuck? Check:
- Claude Desktop version is up to date
- Python version is 3.10+
- Config file is in the correct location
- Cookie value is current and complete

---

## What's Next?

Once set up, you can:

- Ask Claude to analyze your LinkedIn profile and suggest improvements
- Have Claude create a personal website from your profile
- Search for jobs and get summaries
- Research companies and people
- Track your professional network

**Ready to create that website now?** Just say: *"Get my LinkedIn profile and create a personal website for me"*
