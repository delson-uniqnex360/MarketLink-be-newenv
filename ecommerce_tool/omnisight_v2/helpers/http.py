import requests
from typing import Optional, Dict, Any


def make_http_request(
    method: str,
    endpoint: str,
    base_url: str,
    access_token: str,
    params: Optional[Dict[str, Any]] = None,
    payload: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Makes an HTTP request to the given API endpoint with Authorization.

    Args:
        method (str): HTTP method ('GET', 'POST', 'PUT', 'DELETE', etc.).
        endpoint (str): API endpoint path, e.g., '/amazon-ae/orders/'.
        base_url (str): Base URL of the API.
        access_token (str): Access token for authentication.
        params (dict, optional): Query parameters for GET requests.
        payload (dict, optional): JSON body for POST/PUT requests.
        headers (dict, optional): Additional headers to include.
        timeout (int, optional): Request timeout in seconds. Default is 30.

    Returns:
        dict: Parsed JSON response from the API.

    Raises:
        requests.HTTPError: If the request fails (status code >= 400).
    """
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    # Default headers including Authorization
    request_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Merge user-specified headers if any
    if headers:
        request_headers.update(headers)

    response = requests.request(
        method=method.upper(),
        url=url,
        headers=request_headers,
        params=params,
        json=payload,
        timeout=timeout,
    )

    # Raise exception for HTTP errors
    response.raise_for_status()

    # Return parsed JSON or empty dict if no content
    try:
        return response.json()
    except ValueError:
        return {}
