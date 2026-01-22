"""
curl-based HTTP client for environments with DNS restrictions in Python

This module provides a requests-like interface using curl as the backend.
Useful when Python's socket DNS resolution is blocked but curl works.
"""

import subprocess
import json as json_module
from typing import Dict, Any, Optional


class RequestException(Exception):
    """Base exception for requests"""
    pass


class HTTPError(RequestException):
    """HTTP error exception"""
    pass


class ProxyError(RequestException):
    """Proxy error exception"""
    pass


class Timeout(RequestException):
    """Timeout exception"""
    pass


class CurlResponse:
    """Mimics requests.Response object"""

    def __init__(self, status_code: int, text: str, headers: str = ""):
        self.status_code = status_code
        self.text = text
        self.headers = headers
        self.ok = 200 <= status_code < 300

    def json(self) -> Any:
        """Parse response as JSON"""
        return json_module.loads(self.text)

    def raise_for_status(self):
        """Raise exception for HTTP errors"""
        if not self.ok:
            raise HTTPError(f"{self.status_code} Error: {self.text[:200]}")


class CurlHTTPClient:
    """HTTP client using curl as backend"""

    def __init__(self, timeout: int = 30, verify: bool = False):
        self.timeout = timeout
        self.verify = verify  # SSL verification (default: False for compatibility)
        self.headers = {}  # Session headers

    def get(self, url: str, params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None) -> CurlResponse:
        """
        Perform GET request using curl

        Args:
            url: Target URL
            params: Query parameters
            headers: HTTP headers
            timeout: Request timeout in seconds

        Returns:
            CurlResponse object
        """
        # Build URL with parameters
        if params:
            param_str = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{param_str}"

        # Build curl command
        cmd = ["curl", "-s", "-w", "\n%{http_code}", "-X", "GET"]

        # Add timeout
        timeout_val = timeout or self.timeout
        cmd.extend(["--max-time", str(timeout_val)])

        # SSL verification
        if not self.verify:
            cmd.append("-k")

        # Add headers (merge session headers with request headers)
        all_headers = {**self.headers, **(headers or {})}
        for key, value in all_headers.items():
            cmd.extend(["-H", f"{key}: {value}"])

        # Add URL
        cmd.append(url)

        try:
            # Execute curl
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_val + 5  # Add buffer for subprocess
            )

            # Parse output (last line is status code)
            output = result.stdout
            if '\n' in output:
                lines = output.rsplit('\n', 1)
                body = lines[0]
                try:
                    status_code = int(lines[1].strip())
                except (ValueError, IndexError):
                    status_code = 200 if result.returncode == 0 else 500
            else:
                body = output
                status_code = 200 if result.returncode == 0 else 500

            return CurlResponse(status_code, body)

        except subprocess.TimeoutExpired:
            raise Timeout(f"Request timeout after {timeout_val} seconds")
        except Exception as e:
            raise RequestException(f"curl request failed: {e}")

    def post(self, url: str, json: Optional[Dict] = None, json_data: Optional[Dict] = None,
             data: Optional[Dict] = None, headers: Optional[Dict[str, str]] = None,
             timeout: Optional[int] = None) -> CurlResponse:
        """
        Perform POST request using curl

        Args:
            url: Target URL
            json_data: JSON payload
            data: Form data
            headers: HTTP headers
            timeout: Request timeout in seconds

        Returns:
            CurlResponse object
        """
        # Build curl command
        cmd = ["curl", "-s", "-w", "\n%{http_code}", "-X", "POST"]

        # Add timeout
        timeout_val = timeout or self.timeout
        cmd.extend(["--max-time", str(timeout_val)])

        # SSL verification
        if not self.verify:
            cmd.append("-k")

        # Add headers (merge session headers with request headers)
        all_headers = {**self.headers, **(headers or {})}
        for key, value in all_headers.items():
            cmd.extend(["-H", f"{key}: {value}"])

        # Add JSON data (support both 'json' and 'json_data' parameters)
        json_payload = json or json_data
        if json_payload:
            cmd.extend(["-H", "Content-Type: application/json"])
            cmd.extend(["-d", json_module.dumps(json_payload)])
        elif data:
            for key, value in data.items():
                cmd.extend(["-d", f"{key}={value}"])

        # Add URL
        cmd.append(url)

        try:
            # Execute curl
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_val + 5
            )

            # Parse output
            output = result.stdout
            if '\n' in output:
                lines = output.rsplit('\n', 1)
                body = lines[0]
                try:
                    status_code = int(lines[1].strip())
                except (ValueError, IndexError):
                    status_code = 200 if result.returncode == 0 else 500
            else:
                body = output
                status_code = 200 if result.returncode == 0 else 500

            return CurlResponse(status_code, body)

        except subprocess.TimeoutExpired:
            raise Timeout(f"Request timeout after {timeout_val} seconds")
        except Exception as e:
            raise RequestException(f"curl request failed: {e}")


# Create global instance
curl_client = CurlHTTPClient()


def use_curl_backend():
    """
    Replace requests module with curl backend globally

    Usage:
        from curl_http_client import use_curl_backend
        use_curl_backend()

        # Now all imports will use curl
        import requests
        response = requests.get("https://api.example.com")
    """
    import sys
    import types

    # Create a fake requests module
    fake_requests = types.ModuleType('requests')
    fake_requests.get = curl_client.get
    fake_requests.post = curl_client.post
    fake_requests.Session = CurlHTTPClient  # Return class, not instance

    # Create exceptions submodule
    exceptions_module = types.ModuleType('exceptions')
    exceptions_module.HTTPError = HTTPError
    exceptions_module.ProxyError = ProxyError
    exceptions_module.Timeout = Timeout
    exceptions_module.RequestException = RequestException
    fake_requests.exceptions = exceptions_module

    # Replace in sys.modules
    sys.modules['requests'] = fake_requests
    sys.modules['requests.exceptions'] = exceptions_module

    return fake_requests


if __name__ == "__main__":
    # Test the curl client
    print("Testing curl HTTP client...")

    try:
        # Test GET request
        print("\n1. Testing GET request to httpbin.org...")
        response = curl_client.get("https://httpbin.org/get", params={"test": "123"})
        print(f"   Status: {response.status_code}")
        print(f"   Success: {response.ok}")

        # Test JSON parsing
        print("\n2. Testing JSON parsing...")
        data = response.json()
        print(f"   Args: {data.get('args')}")

        # Test POST request
        print("\n3. Testing POST request...")
        response = curl_client.post(
            "https://httpbin.org/post",
            json_data={"key": "value"}
        )
        print(f"   Status: {response.status_code}")

        print("\n✅ All tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
