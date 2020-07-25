# PlaceholderTransformer

Perform arbitrary key/value replacements in kubernetes resources. Placeholders are delimited with `${<placeholder_name>}`. The name of the placeholders are sourced directly from the plugin configuration, or from an external file. If a placeholder is found, but no matching replacement is provided, the placeholder is left as-is. The name of the placeholders must contain only alphanumeric characters.

Support `Secret` by decoding the base64 encoded data, performing the replacement, and encoding back the result in base64.

No replacement is performed on the fields `apiVersion`, `kind` and `metadata`.

## Dependencies

* PyYAML

## API

| Field | Description | Type |  Default |
| --- | --- | --- | --- |
| `placeholders` | A map of placeholders. | map of string | |
| `placeholdersFile` | A file with the placeholders in the dotenv format. Placeholders configured in a file have higher priority. | string | |
| `resourceSelectors` | Selectors to specify on which resources to perform the replacements. Perform replacement on all resources by default. | list of ResourceSelector | null |

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
      - foo=${foo}
      - bar=${bar}

transformers:
  - placeholder-example.yaml
```

*`placeholder-example.yaml`*
``` yaml
apiVersion: badjware/v1
kind: PlaceholderTransformer
metadata:
  name: not-important
placeholders:
  foo: my_first_placeholder
placeholdersFile: placeholders.txt
resourceSelectors:
  - kind: ConfigMap
    name: example-configmap
```

*`placeholders.txt`*
```
bar=my_second_placeholder
```

### Result
``` yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: example-configmap-g9c75m9687
data:
  foo: my_first_placeholder
  bar: my_second_placeholder
```