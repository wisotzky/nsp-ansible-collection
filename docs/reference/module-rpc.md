# nokia.nsp.rpc module

– Execute global YANG RPC operations on Nokia NSP

## Synopsis

* Execute global YANG RPC operations on Nokia NSP

* Execute global RESTCONF RPC operations on Nokia NSP.
* RPC operations use endpoint C(/restconf/operations/{operation}).
* Uses httpapi connection with OAuth2 client credentials authentication.
* Global operations not tied to specific resource instances.
* Input parameters must match YANG RPC input structure.

## Parameters

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `input` | dict | No | {} | - Input parameters for the RPC operation. - Must match YANG RPC input definition... |
| `operation` | str | Yes | - | - RPC operation name with optional namespace (e.g., nsp-inventory:find). - Use C... Aliases: path |

## Notes

* Requires httpapi connection with C(ansible_network_os=nokia.nsp.nsp).
* Connection requires valid OAuth2 credentials.
* For resource-specific operations use M(nokia.nsp.action) instead.

## Examples

```yaml
- name: Query network inventory
  nokia.nsp.rpc:
    operation: nsp-inventory:find
    input:
      xpath-filter: "/nsp-equipment:network/network-element"
      fields: "ne-id;ne-name;ip-address"
      include-meta: false
```

## Return Values

```yaml
output:
  description: Operation output from RESTCONF RPC call
  returned: always
  type: dict
  sample:
    nsp-inventory:output:
      data: []
      total-count: 0
failed:
  description: Module execution failed
  returned: always
  type: bool
changed:
  description: Operation caused change (always false for RPC queries)
  returned: always
  type: bool
```

*New in version "0.0.1"*