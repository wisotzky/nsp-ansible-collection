# nokia.nsp.version module

– Retrieve Nokia NSP system version

## Synopsis

* Retrieve Nokia NSP system version

* Retrieve the NSP system version via internal REST API endpoint.
* Supports version validation against minimum release requirements.
* Uses httpapi connection with OAuth2 client credentials authentication.

## Parameters

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `check` | str | No | null | - Optional minimum required version in C(major.minor) format. - "Examples: C(25.... |

## Notes

* Requires httpapi connection with C(ansible_network_os=nokia.nsp.nsp).
* Connection requires valid OAuth2 credentials.
* This module uses an undocumented internal API endpoint.
* Version information extracted from C(nspOSVersion) field.

## Examples

```yaml
- name: Get NSP version
  nokia.nsp.version:
  register: nsp_version

- name: Validate minimum NSP version
  nokia.nsp.version:
    check: "25.4"
  register: nsp_version
```

## Return Values

```yaml
release:
  description: "NSP Release (example: NSP-CN-25.11.0-rel.302)"
  returned: always
  type: str
major:
  description: Major version number
  returned: always
  type: int
minor:
  description: Minor version number
  returned: always
  type: int
```

*New in version "0.0.1"*