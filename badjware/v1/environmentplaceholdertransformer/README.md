# EnvironmentPlaceholderTransformer

Perform arbitrary key/value replacements in kubernetes resources with values from the environment variables. Placeholders are delimited with `${env:<parameter_name>}`. If a placeholder is found, but no matching environment variable is available, the placeholder is left as-is.

Support `Secret` by decoding the base64 encoded data, performing the replacement, and encoding back the result in base64.

No replacement is performed on the fields `apiVersion`, `kind` and `metadata`.

## Dependencies

* PyYAML

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

*`kustomization.yaml`*
``` yaml
configmapGenerator:
  - name: example-configmap
    literals:
      - foo=${env:foo}

transformers:
  - env-example.yaml
```

*`env-example.yaml`*
``` yaml
apiVersion: badjware/v1
kind: EnvironmentPlaceholderTransformer
metadata:
  name: not-important
resourceSelectors:
  - kind: ConfigMap
    name: example-configmap
```

*run this way*
``` bash
env foo=my_secret kustomize build --enable_alpha_plugins .
```

### Result
``` yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: example-configmap-f8dkmfbdf4
data:
  foo: my_secret
```
