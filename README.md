# Email Sender

A Python script to send bulk personalized emails using Microsoft Graph API with OAuth2 authentication.

## Features

- Send personalized emails to multiple recipients using **Microsoft Graph API**
- Secure **OAuth2 authentication** with device code flow (no passwords!)
- Load recipients from JSON file for easy management
- Environment variables for credential storage
- Automatic token caching and refresh
- Error handling and progress feedback
- Support for personal Microsoft accounts (Hotmail/Outlook.com)

## Prerequisites

- Python 3.6 or higher
- An Office365/Outlook/Hotmail email account
- Azure AD application (free - see setup below)

## Getting Started

### 1. Install Dependencies

First, install the required Python packages:

```powershell
pip install -r requirements.txt
```

This will install:
- `python-dotenv` - Load environment variables from `.env` file
- `msal` - Microsoft Authentication Library for OAuth2
- `requests` - HTTP library for Graph API calls

### 2. Register an Azure Application (Free - 5 minutes)

For personal Microsoft accounts (Hotmail/Outlook.com), you need to register a simple Azure application:

#### Step-by-Step Azure App Registration:

1. **Go to Azure Portal:**
   - Visit: https://portal.azure.com
   - Sign in with your Microsoft account (the same one you'll use for sending emails)

2. **Register a New Application:**
   - Search for **"Azure Active Directory"** or **"Microsoft Entra ID"**
   - Click **"App registrations"** in the left sidebar
   - Click **"+ New registration"**
   - Fill in:
     - **Name**: `Email Sender App` (or any name you like)
     - **Supported account types**: Select **"Personal Microsoft accounts only"**
     - **Redirect URI**: Leave blank
   - Click **"Register"**

3. **Copy Your Application (Client) ID:**
   - On the app overview page, copy the **"Application (client) ID"**
   - Save this as `AZURE_CLIENT_ID` in your `.env` file
   - **That's it! You don't need a client secret for personal accounts.**

4. **Enable Public Client Flow:**
   - Click **"Authentication"** in the left sidebar
   - Scroll down to **"Advanced settings"**
   - Under **"Allow public client flows"**, toggle **"Yes"**
   - Click **"Save"**

5. **Set API Permissions:**
   - Click **"API permissions"** in the left sidebar
   - You should see **"Microsoft Graph" - "User.Read"** by default
   - Click **"+ Add a permission"**
   - Select **"Microsoft Graph"**
   - Select **"Delegated permissions"**
   - Search for and check: **`Mail.Send`**
   - Click **"Add permissions"**
   - **Note:** No admin consent needed for personal accounts!

Done! Your Azure app is ready. The first time you run the script, you'll authenticate via your browser.

### 3. Create a `.env` File

Create a file named `.env` in the project directory with your Azure client ID:

```
AZURE_CLIENT_ID=your_application_client_id_from_step2
SENDER_EMAIL=your.email@hotmail.com
```

> **Important:** The `.env` file is already added to `.gitignore` so your credentials won't be committed to Git.
>
> **Note:** For personal Microsoft accounts, you only need the Client ID! No client secret or tenant ID required.

### 4. Configure Recipients

Edit the `recipients.json` file with your recipients' names and email addresses:

```json
{
  "John Doe": "john@example.com",
  "Jane Smith": "jane@example.com",
  "Alice Johnson": "alice@company.com"
}
```

**Format:** `"Name": "email@address.com"`

### 5. Customize Your Message (Optional)

Open `mail.py` and modify the email content in the main section:

```python
subject: str = "Your Subject Here"
body: str = f"Hi {name},\n\nYour message here...\n\nBest regards"
```

### 6. Run the Script

```powershell
python mail.py
```

## Expected Output

**First Time (Authentication Required):**
```
📧 Email Sender - OAuth2 Authentication
Sending from: carlosalarcon100@hotmail.com

🔐 Authentication Required
==================================================

To sign in, use a web browser to open the page https://microsoft.com/devicelogin
and enter the code AB12CD34 to authenticate.

📋 Steps:
1. Go to: https://microsoft.com/devicelogin
2. Enter code: AB12CD34
3. Sign in with your Microsoft account

Waiting for authentication...
✅ Authentication successful!

Total recipients: 3

Email sent to john@example.com
✓ Sent email to John Doe (john@example.com)
Email sent to jane@example.com
✓ Sent email to Jane Smith (jane@example.com)
Email sent to alice@company.com
✓ Sent email to Alice Johnson (alice@company.com)

Done!
```

**Subsequent Runs (Token Cached):**
```
📧 Email Sender - OAuth2 Authentication
Sending from: carlosalarcon100@hotmail.com

Total recipients: 3

Email sent to john@example.com
✓ Sent email to John Doe (john@example.com)
...

Done!
```

> **Note:** After the first authentication, a `token_cache.json` file is created to store your access token securely. You won't need to authenticate again unless the token expires.

## Project Structure

```
email-sender/
│
├── mail.py              # Main script (uses Microsoft Graph API)
├── oauth_helper.py      # OAuth2 authentication helper (device code flow)
├── recipients.json      # Recipients list
├── requirements.txt     # Python dependencies
├── .env                 # Your Azure client ID (create this, not in Git)
├── token_cache.json     # OAuth token cache (auto-generated, not in Git)
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## Troubleshooting

### Missing Azure Credentials

**Error:**
```
Error: Azure OAuth credentials missing!
```

**Solution:** Make sure your `.env` file contains:
- `AZURE_CLIENT_ID` (from Azure app registration)
- `SENDER_EMAIL` (your Hotmail/Outlook.com email)

### Authentication Timeout

**Error:**
```
Failed to acquire token: timeout
```

**Solution:**
- Make sure you completed the browser authentication within the time limit
- Check that you entered the correct device code
- Try running the script again

### Public Client Flow Not Enabled

**Error:**
```
AADSTS7000218: The request body must contain the following parameter: 'client_assertion' or 'client_secret'
```

**Solution:**
- Go to your Azure app → **Authentication**
- Scroll to **"Advanced settings"**
- Toggle **"Allow public client flows"** to **Yes**
- Click **Save**

### Authentication Successful But Emails Fail

**Error:**
```
✗ Failed to send email: 401 Unauthorized
```

**Solution:**
- The token might not have the correct scopes
- Delete `token_cache.json` and re-authenticate
- Make sure you added the `Mail.Send` permission in Azure
- Verify you're using the correct email address in `SENDER_EMAIL`
- Check that **"Allow public client flows"** is enabled in Azure

### Token Cache Issues

If you're experiencing authentication issues:

1. Delete `token_cache.json` file
2. Run the script again to re-authenticate
3. Make sure to complete the browser authentication flow

### Recipients JSON Not Found

**Error:**
```
Error: recipients.json not found!
```

**Solution:** Make sure `recipients.json` exists in the same directory as `mail.py`.

### Invalid JSON Format

**Error:**
```
Error: Invalid JSON in recipients.json
```

**Solution:** Validate your JSON syntax. Common issues:
- Missing commas between entries
- Missing quotes around names/emails
- Trailing comma after last entry

## Security Notes

- **Never commit your `.env` or `token_cache.json` files** to version control (already in `.gitignore`)
- The `token_cache.json` file contains your access tokens - keep it secure
- OAuth2 device code flow is secure - you authenticate via browser, not in the script
- Access tokens expire automatically and refresh tokens are used for subsequent authentications
- If you suspect your token is compromised, delete `token_cache.json` and re-authenticate
- For personal Microsoft accounts, no client secret is needed (more secure!)
- The authentication is tied to your Microsoft account - you control access via your account security

## Why Microsoft Graph API with OAuth2?

Microsoft has disabled basic authentication (username/password) for security reasons. This script uses Microsoft Graph API with OAuth2:

- ✅ **More Secure** - No passwords stored or transmitted
- ✅ **Token-Based** - Temporary access tokens instead of permanent passwords
- ✅ **Granular Permissions** - Only request Mail.Send permission
- ✅ **Future-Proof** - Microsoft's recommended authentication method
- ✅ **Auditable** - Better tracking of API usage in Azure Portal
- ✅ **REST API** - More reliable than SMTP for personal accounts
- ✅ **Device Code Flow** - User-friendly browser-based authentication

## How It Works

This script uses:

1. **Microsoft Authentication Library (MSAL)** - Handles OAuth2 device code flow
2. **Microsoft Graph API** - Sends emails via REST API (`/me/sendMail` endpoint)
3. **Token Caching** - Stores access tokens locally for subsequent runs

**Authentication Flow:**
- First run: Device code authentication via browser
- Subsequent runs: Uses cached refresh token automatically
- Tokens stored in `token_cache.json` (automatically managed)

## License

This project is free to use and modify for your personal or commercial projects.

## Support

If you encounter any issues, please check the troubleshooting section above or review the Python error messages for specific details.

