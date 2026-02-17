# nokia.nsp.upload module

– Upload files to Nokia NSP

## Synopsis

* Upload files to Nokia NSP

* Upload binary or text files to Nokia NSP servers.
* Uses httpapi connection with Bearer token authentication.
* Uses NSP file-service endpoint for uploads.

## Parameters

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `local_path` | raw | Yes | - | - Path to local file to upload. - Can be a string for single file or list for mu... |
| `overwrite` | bool | No | true | - Whether to overwrite existing files on NSP file-service. |
| `remote_path` | str | Yes | - | - Remote directory on NSP file-service. - If a file path is provided, the filena... |

## Notes

* "Requires httpapi connection with ansible_network_os=nokia.nsp.nsp"
* "Uses Bearer token authentication (automatic via httpapi)"

## Examples

```yaml
- name: Upload single file
  nokia.nsp.upload:
    local_path: /tmp/router.cfg
    remote_path: /nokia/nsp

# Upload multiple files
- name: Upload multiple files
  nokia.nsp.upload:
    local_path:
      - /tmp/test_upload_A.txt
      - /tmp/test_upload_B.txt
    remote_path: /nokia
```

## Return Values

```yaml
local_path:
  description: Source file path
  returned: always
  type: str
  sample: "/tmp/workflow.json"
remote_path:
  description: Remote path or directory on NSP file-service
  returned: always
  type: str
  sample: "/workflows"
remote_filename:
  description: Remote filename used for upload
  returned: when local_path is a single file
  type: str
  sample: "workflow.json"
url:
  description: Upload endpoint URL (file-service)
  returned: always
  type: str
  sample: "/nsp-file-service-app/rest/api/v1/file/uploadFile?dirName=%2Fworkflows&overwrite=true"
response:
  description: Server response data
  returned: always
  type: raw
  sample: {"status": "success"}
results:
  description: List of per-file results when local_path is a list
  returned: when local_path is a list
  type: list
  elements: dict
  sample: []
```

*New in version "0.0.1"*