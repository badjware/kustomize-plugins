# Exec

Run an arbitrary executable as a plugin.

## Dependencies

* PyYAML

## API

Any unspecified fields are ignored, and can be used by the executed plugin.

| Field | Description | Type |  Default |
| --- | --- | --- | --- |
| `path` | The path to the executable to execute as a plugin. | string | |

## Example

*`kustomization.yaml`*
``` yaml
generators:
  - exec-example.yaml
```

*`exec-example.yaml`*
``` yaml
apiVersion: badjware/v1
kind: Exec
metadata:
  name: not-important
path: plugin.sh
```

*`plugin.sh`*
``` sh
#!/bin/sh

cat <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: example-configmap
data:
  foo: bar
EOF
```

### Result
``` yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: example-configmap
data:
  foo: bar
```