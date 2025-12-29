"""OAuth authentication endpoints for Fitbit health data"""
import base64
import json
import logging
import time
from pathlib import Path

import requests
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Token storage path
TOKEN_FILE = Path("fitbit_token.json")

# Fitbit OAuth scopes for health data
SCOPES = ['activity', 'heartrate', 'sleep', 'profile']


class FitbitAuthStatus(BaseModel):
    """Fitbit authorization status response"""
    authorized: bool
    fitbit_connected: bool


@router.get("/fitbit")
async def fitbit_auth():
    """
    Initiate Fitbit OAuth 2.0 flow.

    Redirects user to Fitbit OAuth consent screen.
    """
    settings = get_settings()

    if not settings.fitbit_client_id or not settings.fitbit_client_secret:
        raise HTTPException(
            status_code=500,
            detail="Fitbit OAuth not configured. Add FITBIT_CLIENT_ID and FITBIT_CLIENT_SECRET to .env"
        )

    # Build authorization URL
    scope_string = ' '.join(SCOPES)
    authorization_url = (
        f"https://www.fitbit.com/oauth2/authorize"
        f"?client_id={settings.fitbit_client_id}"
        f"&response_type=code"
        f"&scope={scope_string}"
        f"&redirect_uri={settings.fitbit_redirect_uri}"
    )

    logger.info(f"Redirecting to Fitbit OAuth: {authorization_url}")
    return RedirectResponse(url=authorization_url)


@router.get("/fitbit/callback")
async def fitbit_callback(code: str | None = None, error: str | None = None):
    """
    Handle OAuth callback from Fitbit.

    Args:
        code: Authorization code from Fitbit
        error: Error message if authorization failed
    """
    if error:
        logger.error(f"Fitbit OAuth authorization failed: {error}")
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Authorization Failed</title></head>
                <body>
                    <h1>Authorization Failed</h1>
                    <p>Error: {error}</p>
                    <p><a href="/">Return to app</a></p>
                </body>
            </html>
            """,
            status_code=400
        )

    if not code:
        raise HTTPException(status_code=400, detail="No authorization code provided")

    settings = get_settings()

    try:
        # Prepare Basic Auth header (Fitbit requires this)
        credentials = f"{settings.fitbit_client_id}:{settings.fitbit_client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        # Exchange authorization code for tokens
        token_url = "https://api.fitbit.com/oauth2/token"
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.fitbit_redirect_uri
        }

        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()

        token_response = response.json()

        # Calculate expiration timestamp
        expires_at = int(time.time()) + token_response.get('expires_in', 28800)

        # Save tokens to file
        token_data = {
            'access_token': token_response.get('access_token'),
            'refresh_token': token_response.get('refresh_token'),
            'expires_at': expires_at,
            'user_id': token_response.get('user_id'),
            'token_type': token_response.get('token_type', 'Bearer')
        }

        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f, indent=2)

        logger.info("OAuth tokens saved successfully")

        return HTMLResponse(
            content="""
            <html>
                <head>
                    <title>Link Established | Manas</title>
                    <style>
                        :root {
                            --primary: #22d3ee;
                            --background: #02040a;
                            --glass: rgba(255, 255, 255, 0.03);
                            --border: rgba(255, 255, 255, 0.1);
                        }
                        body {
                            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                            background-color: var(--background);
                            color: white;
                            overflow: hidden;
                        }
                        .ambient-glow {
                            position: absolute;
                            width: 600px;
                            height: 600px;
                            background: radial-gradient(circle, rgba(34, 211, 238, 0.1) 0%, transparent 70%);
                            filter: blur(80px);
                            border-radius: 50%;
                            z-index: 1;
                            animation: pulse 8s infinite ease-in-out;
                        }
                        @keyframes pulse {
                            0%, 100% { transform: scale(1); opacity: 0.3; }
                            50% { transform: scale(1.2); opacity: 0.6; }
                        }
                        .container {
                            position: relative;
                            z-index: 10;
                            background: var(--glass);
                            backdrop-filter: blur(20px);
                            padding: 3.5rem;
                            border-radius: 2.5rem;
                            border: 1px solid var(--border);
                            text-align: center;
                            max-width: 440px;
                            width: 100%;
                            box-shadow: 0 0 100px rgba(34, 211, 238, 0.05);
                            animation: slideUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
                        }
                        @keyframes slideUp {
                            from { opacity: 0; transform: translateY(20px) scale(0.95); }
                            to { opacity: 1; transform: translateY(0) scale(1); }
                        }
                        .branding {
                            font-size: 1.5rem;
                            font-weight: 200;
                            letter-spacing: 0.5em;
                            text-transform: uppercase;
                            margin-bottom: 2rem;
                            color: white;
                            opacity: 0.9;
                        }
                        .branding span {
                            display: block;
                            font-size: 0.6rem;
                            font-weight: 700;
                            letter-spacing: 0.8em;
                            color: var(--primary);
                            margin-top: 0.5rem;
                            opacity: 0.6;
                        }
                        .icon-wrap {
                            position: relative;
                            width: 80px;
                            height: 80px;
                            margin: 0 auto 2rem;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            background: rgba(34, 211, 238, 0.1);
                            border-radius: 1.5rem;
                            border: 1px solid rgba(34, 211, 238, 0.2);
                        }
                        .icon-wrap svg { color: var(--primary); }
                        h1 { 
                            font-size: 1.25rem; 
                            font-weight: 500; 
                            margin-bottom: 0.75rem; 
                            letter-spacing: -0.02em;
                        }
                        p { 
                            color: rgba(255, 255, 255, 0.5); 
                            font-size: 0.875rem;
                            line-height: 1.6; 
                            margin-bottom: 2rem;
                        }
                        .close-btn {
                            padding: 0.875rem 2.5rem;
                            background: var(--primary);
                            color: #02040a;
                            border: none;
                            border-radius: 1rem;
                            font-size: 0.75rem;
                            font-weight: 700;
                            letter-spacing: 0.1em;
                            text-transform: uppercase;
                            cursor: pointer;
                            transition: all 0.2s;
                            box-shadow: 0 10px 20px rgba(34, 211, 238, 0.2);
                        }
                        .close-btn:hover { transform: scale(1.02); filter: brightness(1.1); }
                        .footer {
                            margin-top: 2.5rem;
                            font-size: 0.6rem;
                            font-weight: 700;
                            letter-spacing: 0.3em;
                            color: rgba(255, 255, 255, 0.15);
                            text-transform: uppercase;
                        }
                    </style>
                </head>
                <body>
                    <div class="ambient-glow"></div>
                    <div class="container">
                        <div class="branding">
                            MANAS
                            <span>Neural Link</span>
                        </div>
                        <div class="icon-wrap">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.42 4.58a5.4 5.4 0 0 0-7.65 0l-.77.78-.77-.78a5.4 5.4 0 0 0-7.65 0C1.46 6.7 1.33 10.28 4 13l8 8 8-8c2.67-2.72 2.54-6.3.42-8.42z"></path><path d="M3.5 12h6l.5-1 2 4.5 2-7 1.5 3.5h5"></path></svg>
                        </div>
                        <h1>Fitbit Connected</h1>
                        <p>Your biometric data stream has been successfully integrated. Manas is now synched with your health metrics.</p>
                        <button class="close-btn" onclick="window.close()">Secure and Close</button>
                        <div class="footer">Link Established v2.5.0</div>
                    </div>
                    <script>
                        setTimeout(() => window.close(), 3000);
                    </script>
                </body>
            </html>
            """
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to exchange authorization code: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete authorization: {str(e)}"
        )


@router.get("/fitbit/status", response_model=FitbitAuthStatus)
async def fitbit_status():
    """
    Check if Fitbit is authorized.

    Returns authorization status and whether token exists.
    """
    token_exists = TOKEN_FILE.exists()

    if not token_exists:
        return FitbitAuthStatus(authorized=False, fitbit_connected=False)

    # Try to load and validate token
    try:
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)

        # Check if required fields exist
        has_access_token = 'access_token' in token_data
        has_refresh_token = 'refresh_token' in token_data

        return FitbitAuthStatus(
            authorized=has_access_token and has_refresh_token,
            fitbit_connected=has_access_token and has_refresh_token
        )
    except Exception as e:
        logger.error(f"Failed to read token file: {e}")
        return FitbitAuthStatus(authorized=False, fitbit_connected=False)
