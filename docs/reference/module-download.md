# nokia.nsp.download module

– Download files from Nokia NSP

## Synopsis

* Download files from Nokia NSP

* Download binary or text files from Nokia NSP servers.
* Supports NSP file-service API and custom endpoints.
* Streams downloads with atomic writes and automatic MD5 verification.
* Handles both single and batch downloads.

## Parameters

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `local_path` | path | Yes | - | - Local path where file will be saved. - If this is a directory, filename from r... |
| `remote_path` | raw | No | - | - Remote file path on NSP file-service (alternative to C(url)). - Automatically ... |
| `url` | str | No | - | - Full URL path for download (can include query parameters). - For file-service ... |

## Notes

* "Requires httpapi connection with ansible_network_os=nokia.nsp.nsp"
* "Uses Bearer token authentication (automatic via httpapi)"
* "Large files (up to 1GB) streamed with minimal memory usage"
* "All downloads verified with MD5 checksum"

## Examples

```yaml
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
```

## Return Values

```yaml
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
```

*New in version "0.0.1"*