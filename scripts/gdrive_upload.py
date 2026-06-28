"""
Google Drive uploader — one-time OAuth setup, then silent uploads.

Usage:
  First run (auth):
    python3 scripts/gdrive_upload.py --auth ~/Downloads/gdrive_client.json

  Upload files:
    python3 scripts/gdrive_upload.py --folder-id FOLDER_ID file1.pdf file2.pdf
"""

import argparse
import os
import sys

TOKEN_PATH = os.path.expanduser("~/.config/gdrive_token.json")


def authenticate(client_secrets_path: str):
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    import json

    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
    creds = flow.run_local_server(port=0)

    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())
    print(f"✓ Auth complete. Token saved to {TOKEN_PATH}")
    return creds


def get_credentials():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    if not os.path.exists(TOKEN_PATH):
        sys.exit(f"No token found at {TOKEN_PATH}. Run with --auth first.")

    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return creds


def upload_file(service, file_path: str, folder_id: str) -> str:
    from googleapiclient.http import MediaFileUpload
    import mimetypes

    name = os.path.basename(file_path)
    mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    file_meta = {"name": name, "parents": [folder_id]}
    media = MediaFileUpload(file_path, mimetype=mime, resumable=True)

    print(f"Uploading {name} ({os.path.getsize(file_path) / 1e6:.1f} MB)...", end=" ", flush=True)
    result = service.files().create(body=file_meta, media_body=media, fields="id,name").execute()
    print(f"✓  (id={result['id']})")
    return result["id"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--auth", metavar="CLIENT_JSON", help="Path to OAuth client secrets JSON")
    parser.add_argument("--folder-id", default="1G0h8cBj9ZXDlXXv97LAj9P0esFwyk5KH",
                        help="Drive folder ID to upload into")
    parser.add_argument("files", nargs="*", help="Files to upload")
    args = parser.parse_args()

    if args.auth:
        authenticate(args.auth)
        if not args.files:
            return

    from googleapiclient.discovery import build
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    if not args.files:
        print("No files specified. Use: python3 scripts/gdrive_upload.py file1.pdf file2.pdf")
        return

    for f in args.files:
        if not os.path.exists(f):
            print(f"✗ Not found: {f}")
            continue
        upload_file(service, f, args.folder_id)

    print("Done.")


if __name__ == "__main__":
    main()
