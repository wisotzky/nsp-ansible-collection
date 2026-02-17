#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=no-name-in-module

# Copyright: (c) 2026, Nokia
# BSD 3-Clause License (see LICENSE or
# https://opensource.org/licenses/BSD-3-Clause)

"""Nokia NSP File Download Module.

Download binary and text files from Nokia NSP using httpapi connection.
Streaming downloads with atomic writes and MD5 verification.
"""

import os

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
module: download
short_description: Download files from Nokia NSP
description:
  - Download binary or text files from Nokia NSP servers.
  - Supports NSP file-service API and custom endpoints.
  - Streams downloads with atomic writes and automatic MD5 verification.
  - Handles both single and batch downloads.
version_added: "0.0.1"
author:
  - Sven Wisotzky
options:
  url:
    description:
      - Full URL path for download (can include query parameters).
      - For file-service use C(/nsp-file-service-app/rest/api/v1/file/downloadFile?filePath=/path).
      - Mutually exclusive with C(remote_path).
    required: false
    type: str
  remote_path:
    description:
      - Remote file path on NSP file-service (alternative to C(url)).
      - Automatically converted to file-service download URL.
      - Can be a string for single file or list for batch downloads.
      - "Example: C(/nokia/nsp/cam/artifacts/bundle/nsp-ne-upgrade-with-phases-1.75.0.zip)."
    required: false
    type: raw
  local_path:
    description:
      - Local path where file will be saved.
      - If this is a directory, filename from remote path is used.
      - Parent directories are created automatically.
    required: true
    type: path
notes:
  - "Requires httpapi connection with ansible_network_os=nokia.nsp.nsp"
  - "Uses Bearer token authentication (automatic via httpapi)"
  - "Large files (up to 1GB) streamed with minimal memory usage"
  - "All downloads verified with MD5 checksum"
requirements:
  - ansible >= 2.9
'''

EXAMPLES = r'''
- name: Download using file-service path
  nokia.nsp.download:
    remote_path: /nokia/nsp/cam/artifacts/bundle/my-bundle.zip
    local_path: /tmp

- name: Download using full URL
  nokia.nsp.download:
    url: /nsp-file-service-app/rest/api/v1/file/downloadFile?filePath=/nokia/nsp/cam/artifacts/bundle/my-bundle.zip
    local_path: /tmp/my-bundle.zip

- name: Download multiple files
  nokia.nsp.download:
    remote_path:
      - /nokia/test_upload_A.txt
      - /nokia/test_upload_B.txt
    local_path: /tmp/download/
'''

RETURN = r'''
remote_path:
  description: Remote file path or URL downloaded
  returned: always
  type: str
  sample: "/nokia/nsp/cam/artifacts/bundle/file.zip"
local_path:
  description: Local destination file path
  returned: always
  type: str
  sample: "/tmp/file.zip"
file_size:
  description: Downloaded file size in bytes
  returned: always
  type: int
  sample: 1048576
checksum:
  description: MD5 checksum of downloaded file
  returned: always
  type: str
  sample: "d41d8cd98f00b204e9800998ecf8427e"
results:
  description: List of per-file results when remote_path is a list
  returned: when remote_path is a list
  type: list
  elements: dict
  sample: []
'''


def build_download_url(remote_path=None, url=None):
    """Build download URL from remote_path or return url as-is."""
    if url:
        return url

    if remote_path:
        from urllib.parse import quote

        if not remote_path.startswith("/"):
            remote_path = "/" + remote_path
        encoded_path = quote(remote_path, safe="")
        return f"/nsp-file-service-app/rest/api/v1/file/downloadFile?filePath={encoded_path}"

    return None


def extract_filename(remote_path=None, url=None):
    """Extract filename from remote_path or url."""
    if remote_path:
        return os.path.basename(remote_path)

    if url:
        if "filePath=" in url:
            from urllib.parse import unquote, parse_qs, urlparse

            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if "filePath" in params:
                file_path = unquote(params["filePath"][0])
                return os.path.basename(file_path)

        from urllib.parse import urlparse

        path = urlparse(url).path
        return os.path.basename(path) or "downloaded_file"

    return "downloaded_file"


def download_file(module, connection, remote_path, local_path, url=None):
    """Download a single file using httpapi connection.

    Delegates to nsp.py download() method for streaming with automatic
    MD5 verification and atomic writes.

    Args:
        module: AnsibleModule instance.
        connection: Connection object (httpapi).
        remote_path: NSP file path or None.
        local_path: Local destination path.
        url: Complete download URL or None.

    Returns:
        Result dict with remote_path, local_path, file_size, checksum.

    Raises:
        Calls module.fail_json on errors.
    """
    download_url = build_download_url(remote_path=remote_path, url=url)
    if not download_url:
        module.fail_json(msg="Could not build download URL")

    # Handle directory destination
    if os.path.isdir(local_path):
        filename = extract_filename(remote_path=remote_path, url=url)
        local_path = os.path.join(local_path, filename)

    try:
        # Create parent directories
        dest_dir = os.path.dirname(local_path)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)

        # Use httpapi download method (handles streaming, atomic write, MD5)
        result = connection.download(download_url, local_path)

        return {
            "remote_path": remote_path or url,
            "local_path": local_path,
            "file_size": result["file_size"],
            "checksum": result["checksum"]
        }

    except Exception as e:
        module.fail_json(
            msg=f"Download failed: {to_native(e)}",
            remote_path=remote_path or url,
            local_path=local_path
        )


def main():
    """Main module execution."""
    module = AnsibleModule(
        argument_spec={
            "url": {"type": "str", "required": False},
            "remote_path": {"type": "raw", "required": False},
            "local_path": {"type": "path", "required": True},
        },
        mutually_exclusive=[["url", "remote_path"]],
        required_one_of=[["url", "remote_path"]],
        supports_check_mode=False,
    )

    url = module.params.get("url")
    remote_path = module.params.get("remote_path")
    local_path = module.params["local_path"]

    try:
        connection = Connection(module._socket_path)
    except Exception as e:
        module.fail_json(msg=f"Failed to establish connection: {to_native(e)}")

    # Handle batch downloads
    if isinstance(remote_path, list):
        if not os.path.isdir(local_path):
            module.fail_json(
                msg="When remote_path is a list, local_path must be a directory",
                remote_path=remote_path,
                local_path=local_path
            )

        results = [download_file(module, connection, item, local_path) for item in remote_path]
        module.exit_json(changed=False, results=results)
        return

    # Single download
    result = download_file(module, connection, remote_path, local_path, url=url)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
