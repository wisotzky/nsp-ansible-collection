# nokia.nsp.wfm module

– Manage Nokia NSP Workflow Manager workflows

## Synopsis

* Manage Nokia NSP Workflow Manager workflows

* Create, update, delete, and execute workflows in Nokia NSP Workflow Manager.
* Upload workflows from files or directories (with optional README and UI schemas).
* Define workflows inline with YAML text.
* Execute workflows synchronously.
* Follows VS Code Workflow Manager extension logic.

## Parameters

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `define` | str | No | - | - Inline workflow definition as YAML text. - Creates or updates the workflow. |
| `delete` | str | No | - | - Workflow name or UUID to delete. - First sets workflow to DRAFT status before ... |
| `execute` | str | No | - | - Workflow name or UUID to execute synchronously. - Returns execution result wit... |
| `input` | dict | No | {} | - Input parameters for workflow execution. - Only used with I(execute) operation... |
| `upload` | path | No | - | - Path to workflow YAML file or directory. - If directory, must contain exactly ... |

## Notes

* Requires httpapi connection plugin with C(ansible_network_os=nokia.nsp.nsp).
* Exactly one of O(upload), O(define), O(execute), or O(delete) must be specified.
* Using check-mode workflows will be validated but not created/updated.
* Updates follow lifecycle: DRAFT → update → PUBLISHED.
* Creates follow lifecycle: create → PUBLISHED.

## Examples

```yaml
- name: Upload workflow from file
  nokia.nsp.wfm:
    upload: workflow.yaml

- name: Upload workflow from directory
  nokia.nsp.wfm:
    upload: /path/to/workflow_dir/

- name: Define workflow inline
  nokia.nsp.wfm:
    define: |
      ---
      version: '2.0'
      helloworld:
        description: Simple test workflow
        type: direct
        tags:
          - test
        input:
          - host: localhost
          - seconds: 1
        output:
          result: <% task("pingtask").result %>
        tasks:
          pingtask:
            action: nsp.ping
            input:
              host: <% $.host %>
              duration: <% $.seconds %>

- name: Execute workflow by name
  nokia.nsp.wfm:
    execute: helloworld
    input:
      host: localhost
      seconds: 5

- name: Execute workflow by UUID
  nokia.nsp.wfm:
    execute: "{{ workflow_id }}"
    input:
      host: localhost
      seconds: 5

- name: Delete workflow
  nokia.nsp.wfm:
    delete: my_workflow

- name: Complete CI/CD pipeline
  block:
    - name: Upload workflow
      nokia.nsp.wfm:
        upload: workflows/helloworld/helloworld.yaml
      register: wf

    - name: Execute workflow
      nokia.nsp.wfm:
        execute: "{{ wf.workflow_id }}"
        input:
          host: localhost
          seconds: 5

    - name: Cleanup workflow
      nokia.nsp.wfm:
        delete: "{{ wf.workflow_id }}"
```

## Return Values

```yaml
workflow_id:
  description: UUID of the workflow
  returned: success
  type: str
  sample: a1b2c3d4-e5f6-7890-abcd-ef1234567890
workflow_name:
  description: Name of the workflow
  returned: success
  type: str
  sample: my_workflow
status:
  description: Workflow status
  returned: when upload or define
  type: str
  sample: PUBLISHED
execution_id:
  description: UUID of the execution
  returned: when execute
  type: str
  sample: f1e2d3c4-b5a6-7890-cdef-123456789abc
state:
  description: Execution state
  returned: when execute
  type: str
  sample: SUCCESS
output:
  description: Workflow execution output
  returned: when execute and completed
  type: dict
state_info:
  description: Execution state information or error details
  returned: when execute
  type: str
changed:
  description: Whether workflow was created, updated, or deleted
  returned: always
  type: bool
msg:
  description: Human-readable message describing the operation result
  returned: always
  type: str
```

*New in version "0.0.1"*