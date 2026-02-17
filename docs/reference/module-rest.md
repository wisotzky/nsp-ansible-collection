# nokia.nsp.rest module

– Execute text-based REST API calls against Nokia NSP

## Synopsis

* Execute text-based REST API calls against Nokia NSP

* Execute text-based REST API calls against Nokia NSP.
* Uses httpapi connection with Bearer token and SSL settings.
* Similar to ansible.builtin.uri but uses NSP httpapi connection.
* Supports text file read/write operations.
* Automatic JSON parsing and various body formats.
* For binary file operations use M(nokia.nsp.upload) and M(nokia.nsp.download).

## Parameters

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `body` | raw | No | - | - Request body - Can be a dict, list, or string - Use with O(body_format) to con... |
| `body_format` | str | No | 'raw' | - Serialization format for request body - json - JSON serialization - form-urlen... Choices: json, form-urlencoded, form-multipart, raw |
| `creates` | path | No | - | - Skip if this file exists (idempotency) |
| `dest` | path | No | - | - Path where to write text response content - If a directory, filename from resp... |
| `force` | bool | No | false | - Do not use cached responses |
| `headers` | dict | No | {} | - Additional HTTP headers - Authorization header added automatically |
| `method` | str | No | 'GET' | - HTTP method to use Choices: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS |
| `path` | str | Yes | - | - REST API endpoint path without base URL - Example "/wfm/api/v1/action-executio... |
| `removes` | path | No | - | - Skip if this file does not exist (idempotency) |
| `return_content` | bool | No | false | - Whether to return response body content - Always true for failed requests |
| `src` | path | No | - | - Path to text file to read as request body - Cannot be used with O(body) - For ... |
| `status_code` | list | No | - | - List of acceptable HTTP status codes for success - Default depends on method (... |
| `timeout` | int | No | 30 | - Socket timeout in seconds |

## Notes

* "Requires httpapi connection with ansible_network_os=nokia.nsp.nsp"
* "Bearer token and SSL settings come from httpapi configuration"
* "Mutually exclusive: body and src"
* "For binary file operations use M(nokia.nsp.upload) and M(nokia.nsp.download)"
* "src and dest handle text files only with UTF-8 encoding"

## Examples

```yaml
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
```

## Return Values

```yaml
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
```

*New in version "0.0.1"*