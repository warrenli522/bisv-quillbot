# type: ignore
#google apis have no typing
import os
import re
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build


DOC_ID_REGEX = re.compile(r"/d/([a-zA-Z0-9_-]+)")


def get_doc_id_from_url(doc_url: str) -> str:
    """
    Extracts a Google Doc/Drive file ID from a URL.

    :param doc_url: The Google Doc or Drive URL
    :type doc_url: str
    :return: The file ID
    :rtype: str
    :raises ValueError: If the URL does not contain a file ID
    """
    match = DOC_ID_REGEX.search(doc_url)
    if not match:
        raise ValueError("Invalid Google Doc URL: could not find file ID.")
    return match.group(1)


def has_anyone_with_link_edit_permission(
    doc_url: str,
    service_account_file: Optional[str] = None,
) -> bool:
    """
    Returns whether the Google Doc has "anyone with the link" edit permission.

    This checks Drive permissions for a permission entry with:
    - type == "anyone"
    - role == "writer"

    :param doc_url: The Google Doc URL
    :type doc_url: str
    :param service_account_file: Optional path to the service account JSON file.
        If omitted, uses GOOGLE_SERVICE_ACCOUNT_FILE or GOOGLE_APPLICATION_CREDENTIALS
        from the environment.
    :type service_account_file: Optional[str]
    :return: True if link-only edit permission exists, else False
    :rtype: bool
    """
    file_id = get_doc_id_from_url(doc_url)

    creds_path = service_account_file or os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS"
    )
    if not creds_path:
        raise ValueError(
            "Service account credentials not found. Set GOOGLE_SERVICE_ACCOUNT_FILE or "
            "GOOGLE_APPLICATION_CREDENTIALS."
        )

    credentials = service_account.Credentials.from_service_account_file( 
        creds_path,
        scopes=["https://www.googleapis.com/auth/drive.metadata.readonly"],
    )

    service = build("drive", "v3", credentials=credentials)
    response = (
        service.permissions() #pylint: disable=no-member
        .list(
            fileId=file_id,
            fields="permissions(type,role)",
        )
        .execute()
    )

    for perm in response.get("permissions", []):
        if perm.get("type") == "anyone" and perm.get("role") == "writer":
            return True

    return False
