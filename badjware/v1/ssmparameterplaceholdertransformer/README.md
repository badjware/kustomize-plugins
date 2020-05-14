# SSMParameterPlaceholderTransformer

Perform arbitrary key/value replacements in kubernetes resources with values from [AWS Systems Manager Parameters](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html). Placeholders are delimited with `${ssm:<parameter_name>}`. If a placeholder is found, but no matching parameter is available, the placeholder is left as-is.

Support `Secret` by decoding the base64 encoded data, performing the replacement, and encoding back the result in base64.

No replacement is performed on the fields `apiVersion`, `kind` and `metadata`.

## Dependencies

* PyYAML
* boto3

## API

| Field | Description | Type |  Default |
| --- | --- | --- | --- |
| `resourceSelectors` | Selectors to specify on which resources to perform the replacements. Perform replacement only on `Secret`s by default. | list of ResourceSelector | `[{'kind':'Secret'}]` |

## ResourceSelector
| Field | Description | Type |  Default |
| --- | --- | --- | --- |
| `group` | The api group of the resource. | string | |
| `version` | The api version of the resource. | string | |
| `kind` | The kind of resource. | string | |
| `name` | The name of the resource. | string | |
| `namespace` | The namespace the resource is located in. | string | |


## Example
*with awscli*
``` bash
aws ssm put-parameter --name "foo" --type SecureString --value "my_secret"
```

*`kustomization.yaml`*
``` yaml
configmapGenerator:
  - name: example-configmap
    literals:
      - foo=${ssm:foo}

transformers:
  - ssm-example.yaml
```

*`ssm-example.yaml`*
``` yaml
apiVersion: badjware/v1
kind: SSMParameterPlaceholderTransformer
metadata:
  name: not-important
resourceSelectors:
  - kind: ConfigMap
    name: example-configmap
```

### Result
``` yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: example-configmap-k9hkg4fdb5
data:
  foo: my_secret
```
