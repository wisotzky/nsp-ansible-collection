#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=no-name-in-module

# Copyright: (c) 2026, Nokia
# BSD 3-Clause License (see LICENSE or
# https://opensource.org/licenses/BSD-3-Clause)

"""Nokia NSP REST Module.

Execute text-based REST API calls against Nokia NSP using httpapi connection.
Aligned with Ansible's uri module but with integrated Bearer token and SSL handling.
For binary file operations, use nokia.nsp.upload and nokia.nsp.download modules.
"""

import json
import os
import tempfile
from datetime import datetime, timezone
from urllib.parse import urlencode

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection
from ansible.module_utils.common.text.converters import to_native

# Validate Python version and required packages (optional fallback)
try:
    from ansible_collections.nokia.nsp.plugins.module_utils.version_check import (  # pylint: disable=import-error
        check_all_requirements,
    )
    check_all_requirements()
except ImportError:
    # Fallback if module utils not available (e.g., during linting)
    pass


DOCUMENTATION = r'''
---
module: rest
short_description: Execute text-based REST API calls against Nokia NSP
description:
  - Execute text-based REST API calls against Nokia NSP.
  - Uses httpapi connection with Bearer token and SSL settings.
  - Similar to ansible.builtin.uri but uses NSP httpapi connection.
  - Supports text file read/write operations.
  - Automatic JSON parsing and various body formats.
  - For binary file operations use M(nokia.nsp.upload) and M(nokia.nsp.download).
version_added: "0.0.1"
author:
  - Sven Wisotzky
options:
  path:
    description:
      - REST API endpoint path without base URL
      - Example "/wfm/api/v1/action-execution"
    required: true
    type: str
  method:
    description:
      - HTTP method to use
    required: false
    type: str
    choices:
      - GET
      - POST
      - PUT
      - DELETE
      - PATCH
      - HEAD
      - OPTIONS
    default: 'GET'
  body:
    description:
      - Request body
      - Can be a dict, list, or string
      - Use with O(body_format) to control serialization
    required: false
    type: raw
  body_format:
    description:
      - Serialization format for request body
      - json - JSON serialization
      - form-urlencoded - URL-encoded form data
      - form-multipart - Multipart form data (for file uploads)
      - raw - Send as-is (default)
    required: false
    type: str
    choices:
      - json
      - form-urlencoded
      - form-multipart
      - raw
    default: 'raw'
  src:
    description:
      - Path to text file to read as request body
      - Cannot be used with O(body)
      - For binary uploads use nokia.nsp.file_upload module
    required: false
    type: path
  dest:
    description:
      - Path where to write text response content
      - If a directory, filename from response will be used
      - If file exists, will be overwritten
      - For binary downloads use nokia.nsp.file_download module
    required: false
    type: path
  return_content:
    description:
      - Whether to return response body content
      - Always true for failed requests
    required: false
    type: bool
    default: false
  status_code:
    description:
      - List of acceptable HTTP status codes for success
      - Default depends on method (200 for GET, 200-201 for POST, etc)
    required: false
    type: list
    elements: int
  headers:
    description:
      - Additional HTTP headers
      - Authorization header added automatically
    required: false
    type: dict
    default: {}
  timeout:
    description:
      - Socket timeout in seconds
    required: false
    type: int
    default: 30
  creates:
    description:
      - Skip if this file exists (idempotency)
    required: false
    type: path
  removes:
    description:
      - Skip if this file does not exist (idempotency)
    required: false
    type: path
  force:
    description:
      - Do not use cached responses
    required: false
    type: bool
    default: false
notes:
  - "Requires httpapi connection with ansible_network_os=nokia.nsp.nsp"
  - "Bearer token and SSL settings come from httpapi configuration"
  - "Mutually exclusive: body and src"
  - "For binary file operations use M(nokia.nsp.upload) and M(nokia.nsp.download)"
  - "src and dest handle text files only with UTF-8 encoding"
'''

EXAMPLES = r'''
- name: Execute WFM action via REST API
  nokia.nsp.rest:
    method: POST
    path: /wfm/api/v1/action-execution
    body_format: json
    body:
      name: nsp.ping
      examples: Default
      description: "Test ping action"
      input:
        host: localhost
        duration: 1
  register: result

- name: List files in NSP file storage
  nokia.nsp.rest:
    method: GET
    path: /nsp-file-service-app/rest/api/v1/directory?dirName=/nokia
    return_content: true
  register: file_list
'''

RETURN = r'''
status:
  description: HTTP status code
  returned: always
  type: int
content:
  description: Response body content as string
  returned: when return_content is true or request failed
  type: str
json:
  description: Response body parsed as JSON
  returned: when response is valid JSON
  type: raw
elapsed:
  description: Seconds elapsed for the request
  returned: always
  type: int
path:
  description: Destination file path (if dest specified)
  returned: when dest is specified
  type: str
changed:
  description: Whether the request changed state
  returned: always
  type: bool
headers:
  description: Response headers
  returned: always
  type: dict
'''


def form_urlencoded(body):
    """Convert dict/list to form-urlencoded string.

    Args:
        body: Dictionary or list of tuples to encode.

    Returns:
        URL-encoded string representation.
    """
    if isinstance(body, str):
        return body

    if isinstance(body, dict):
        return urlencode(body)

    if isinstance(body, list):
        # List of tuples
        return urlencode(body)

    return body


def prepare_body(body, body_format):
    """Prepare request body and content type.

    Args:
        body: Request body (dict, list, str, or None).
        body_format: Format type ("json", "form-urlencoded", "raw").

    Returns:
        Tuple of (body_string, content_type).

    Raises:
        ValueError: If body cannot be serialized.
    """
    if body is None:
        return None, None

    # Convert Ansible data structures to plain Python objects
    if hasattr(body, "items") and callable(body.items):  # dict-like
        body = dict(body)
    elif isinstance(body, (list, tuple)):
        body = list(body)

    if body_format == "json":
        if isinstance(body, str):
            # String body - assume it's already JSON formatted
            return body, "application/json"
        else:
            # Dict/list - convert to JSON string
            try:
                return json.dumps(body), "application/json"
            except TypeError as e:
                raise ValueError(f"Failed to serialize body to JSON: {e}")

    elif body_format == "form-urlencoded":
        result = form_urlencoded(body)
        return (str(result) if result is not None else None,
                "application/x-www-form-urlencoded")

    elif body_format == "raw":
        if isinstance(body, str):
            return body, "text/plain"
        else:
            # For raw format with dict/list, convert to JSON
            try:
                return json.dumps(body), "application/json"
            except TypeError:
                return str(body), "text/plain"

    # Fallback - convert to string
    return str(body) if body is not None else None, None


def write_file(module, dest, content):
    """Write text content to destination file.

    Args:
        module: AnsibleModule instance.
        dest: Destination file path.
        content: Content to write (str or convertible to str).

    Returns:
        True if successful.

    Raises:
        Calls module.fail_json on error.
    """
    try:
        # Create temp file in module tmpdir
        fd, tmpfile = tempfile.mkstemp(dir=module.tmpdir)
        try:
            if isinstance(content, str):
                os.write(fd, content.encode("utf-8"))
            else:
                os.write(fd, str(content).encode("utf-8"))
        finally:
            os.close(fd)

        # Atomic move
        module.atomic_move(tmpfile, dest)
        return True
    except Exception as e:
        module.fail_json(
            msg=f"Failed to write file {dest}: {to_native(e)}"
        )


def main():
    """Main module execution."""
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='str', required=True),
            method=dict(
                type='str',
                choices=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'],
                default='GET'
            ),
            body=dict(type='raw', required=False, default=None),
            body_format=dict(
                type='str',
                choices=['json', 'form-urlencoded', 'form-multipart', 'raw'],
                default='raw'
            ),
            src=dict(type='path', required=False),
            dest=dict(type='path', required=False),
            return_content=dict(type='bool', default=False),
            status_code=dict(type='list', elements='int', required=False),
            headers=dict(type='dict', default={}),
            timeout=dict(type='int', default=30),
            creates=dict(type='path', required=False),
            removes=dict(type='path', required=False),
            force=dict(type='bool', default=False),
        ),
        mutually_exclusive=[['body', 'src']],
        supports_check_mode=False,
    )

    path = module.params["path"]
    method = module.params["method"]
    body = module.params["body"]
    body_format = module.params["body_format"]
    src = module.params["src"]
    dest = module.params["dest"]
    return_content = module.params["return_content"]
    status_code = module.params["status_code"]
    headers = module.params["headers"] or {}
    creates = module.params["creates"]
    removes = module.params["removes"]

    # Check idempotency conditions
    if creates and os.path.exists(creates):
        module.exit_json(
            changed=False,
            msg=f"skipped, since '{creates}' exists"
        )

    if removes and not os.path.exists(removes):
        module.exit_json(
            changed=False,
            msg=f"skipped, since '{removes}' does not exist"
        )

    # Default expected status codes based on method
    if status_code is None:
        if method == 'POST':
            status_code = [200, 201]
        elif method in ['PUT', 'DELETE']:
            status_code = [200, 204]
        else:
            status_code = [200]

    # Prepare request body
    request_body = None
    request_data = None

    if src:
        # Read text file
        try:
            with open(src, "r", encoding="utf-8") as f:
                request_data = f.read()
            headers["Content-Type"] = "text/plain"
        except Exception as e:
            module.fail_json(
                msg=f"Failed to read text file {src}: {to_native(e)}"
            )
    elif body is not None:
        # Prepare body based on format
        try:
            request_body, content_type = prepare_body(body, body_format)
            if content_type and 'Content-Type' not in headers:
                headers['Content-Type'] = content_type

            # Keep as string for httpapi (no encoding to bytes)
            request_data = request_body
        except ValueError as e:
            module.fail_json(msg=str(e))

    # Execute request
    connection = Connection(module._socket_path)
    start_time = datetime.now(timezone.utc)
    http_status = 200
    response_content = None

    try:
        # Ensure request_data is string or None
        if request_data is not None and not isinstance(request_data, (str, bytes)):
            request_data = str(request_data)

        # Send request for text-based operations
        response = connection.send_request(
            method=method,
            path=path,
            data=request_data,
            headers=headers,
        )

        # Extract status and content
        if isinstance(response, tuple):
            http_status = response[0]
            response_content = response[1] if len(response) > 1 else None
        else:
            http_status = getattr(connection, '_last_response_status', 200)
            response_content = response

        elapsed = int((datetime.now(timezone.utc) - start_time).total_seconds())

        # Determine if we should return content or parse JSON
        maybe_output = return_content or http_status not in status_code

        # Process text response content
        content = None
        if response_content is not None:
            if isinstance(response_content, (dict, list)):
                # Already parsed JSON by httpapi
                content = response_content
            elif isinstance(response_content, str):
                # String response
                content = response_content
            else:
                # Other types - convert to string
                content = str(response_content) if response_content is not None else None

        # Try to parse as JSON if appropriate
        response_json = None
        if content is not None:
            if isinstance(content, dict) or isinstance(content, list):
                # Already a parsed data structure
                response_json = content
            elif isinstance(content, str):
                # Try to parse string as JSON
                try:
                    response_json = json.loads(content)
                except (json.JSONDecodeError, ValueError, TypeError):
                    # Not JSON - leave as string
                    pass

        # Build result
        result = {
            'status': http_status,
            'elapsed': elapsed,
            'changed': method != 'GET' and http_status in status_code,
            'headers': {},
        }

        # Add content if requested or on error
        if content is not None and maybe_output:
            if isinstance(content, str):
                result["content"] = content
            else:
                result["content"] = json.dumps(content)

        # Add JSON if valid
        if response_json is not None:
            result["json"] = response_json

        # Write to destination file if specified (text only)
        if dest and http_status in status_code and content is not None:
            write_content = content
            if isinstance(content, (dict, list)):
                write_content = json.dumps(content, indent=2)
            elif not isinstance(content, str):
                write_content = str(content)

            write_file(module, dest, write_content)
            result["path"] = dest
            result["changed"] = True

        # Check status code
        if http_status not in status_code:
            result["msg"] = f"Status code {http_status} not in {status_code}"
            module.fail_json(**result)

        module.exit_json(**result)

    except Exception as e:
        elapsed = int((datetime.now(timezone.utc) - start_time).total_seconds())
        module.fail_json(
            msg=f"REST API call failed: {to_native(e)}",
            elapsed=elapsed
        )


if __name__ == "__main__":
    main()
