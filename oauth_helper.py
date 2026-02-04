import os
import msal
import webbrowser
import json

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MicrosoftOAuthHelper:
    """Helper class for Microsoft OAuth2 authentication for personal accounts."""
    
    def __init__(self):
        self.client_id: str = os.getenv("AZURE_CLIENT_ID")
        self.sender_email: str = os.getenv("SENDER_EMAIL")
        
        # For personal Microsoft accounts (hotmail, outlook.com)
        self.authority: str = "https://login.microsoftonline.com/consumers"
        
        # Scopes for personal Microsoft accounts (consumers)
        # Use Microsoft Graph Mail.Send for personal accounts
        self.scopes = [
            "https://graph.microsoft.com/Mail.Send"
        ]
        
        # Token cache file
        self.token_cache_file: str = "token_cache.json"
    
    def _load_cache(self):
        """Load token cache from file."""
        cache = msal.SerializableTokenCache()
        if os.path.exists(self.token_cache_file):
            with open(self.token_cache_file, "r") as f:
                cache.deserialize(f.read())
        return cache
    
    def _save_cache(self, cache):
        """Save token cache to file."""
        if cache.has_state_changed:
            with open(self.token_cache_file, "w") as f:
                f.write(cache.serialize())
    
    def get_access_token(self) -> str:
        """Get OAuth2 access token using device code flow or cached token."""
        cache = self._load_cache()
        
        app = msal.PublicClientApplication(
            self.client_id,
            authority=self.authority,
            token_cache=cache
        )
        
        # Create a fresh list of scopes each time
        # Use Microsoft Graph Mail.Send for personal accounts
        scopes_list = ["https://graph.microsoft.com/Mail.Send"]
        
        # Try to get token from cache first
        accounts = app.get_accounts()
        if accounts:
            try:
                result = app.acquire_token_silent(scopes_list, account=accounts[0])
                if result and "access_token" in result:
                    self._save_cache(cache)
                    return result["access_token"]
            except Exception as e:
                print(f"Note: Cached token expired, re-authenticating...")
        
        # If no cached token, use device code flow (user interactive)
        print("\n🔐 Authentication Required")
        print("=" * 50)
        
        flow = app.initiate_device_flow(scopes_list)
        
        if "user_code" not in flow:
            error_msg = flow.get("error_description", flow.get("error", "Failed to create device flow"))
            raise Exception(f"Failed to create device flow: {error_msg}")
        
        print(f"\n{flow['message']}")
        print("\n📋 Steps:")
        print(f"1. Go to: {flow['verification_uri']}")
        print(f"2. Enter code: {flow['user_code']}")
        print("3. Sign in with your Microsoft account")
        print("\nWaiting for authentication...")
        
        # Try to open browser automatically
        try:
            webbrowser.open(flow['verification_uri'])
        except:
            pass
        
        result = app.acquire_token_by_device_flow(flow)
        
        if "access_token" in result:
            self._save_cache(cache)
            print("✅ Authentication successful!\n")
            return result["access_token"]
        else:
            error_description = result.get("error_description", "Unknown error")
            raise Exception(f"Failed to acquire token: {error_description}")
    
    def generate_oauth_string(self, access_token: str) -> str:
        """Generate XOAUTH2 string for SMTP authentication."""
        auth_string: str = f"user={self.sender_email}\x01auth=Bearer {access_token}\x01\x01"
        return auth_string
