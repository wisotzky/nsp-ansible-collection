# nokia.nsp.action module

– Execute YANG actions on Nokia NSP RESTCONF resources

## Synopsis

* Execute YANG actions on Nokia NSP RESTCONF resources

* Execute resource-specific RESTCONF actions on Nokia NSP.
* Actions use endpoint C(/restconf/data/{resource}/{action}).
* Uses httpapi connection with OAuth2 client credentials authentication.
* Actions are bound to specific resource instances.
* Input parameters must match YANG action input structure.

## Parameters

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `input` | dict | No | {} | - Input parameters for the action. - Must match YANG action input definition. |
| `operation` | str | Yes | - | - Action name with optional namespace (e.g., C(audit), C(synchronize)). - Use C(... |
| `path` | str | Yes | - | - RESTCONF data resource path where the action is executed. - Special characters... |

## Notes

* Requires httpapi connection with C(ansible_network_os=nokia.nsp.nsp).
* Connection requires valid OAuth2 credentials.
* For global operations use M(nokia.nsp.rpc) instead.
* Resource path must URL-encode special characters properly.

## Examples

```yaml
- name: Audit intent configuration
  nokia.nsp.action:
    path: "ibn:ibn/intent={{ ne_id | urlencode }},{{ intent_name | urlencode }}"
    operation: audit
  register: audit_result

- name: Synchronize intent state
  nokia.nsp.action:
    path: "ibn:ibn/intent={{ ne_id | urlencode }},{{ intent_name | urlencode }}"
    operation: synchronize
  register: sync_result

- name: Display action output
  debug:
    var: audit_result
```

## Return Values

```yaml
output:
  description: Operation output from RESTCONF resource action
  returned: always
  type: dict
  sample:
    ibn:output:
      audit-report:
        intent-type: helloworld
        target: 1034::dead:beef:1
failed:
  description: Module execution failed
  returned: always
  type: bool
changed:
  description: Action caused resource change (action-dependent)
  returned: always
  type: bool
```

*New in version "0.0.1"*