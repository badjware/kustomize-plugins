# kustomize-plugins

A collection of plugins for [kustomize](https://github.com/kubernetes-sigs/kustomize).

## Install and usage

### Manual

1. Install the python dependencies: `pip install --user pyyaml boto3`
2. [Download](https://github.com/badjware/kustomize-plugins/archive/master.zip) or clone this repository.
3. Create the kustomize plugins directory: `mkdir -p ~/.config/kustomize/plugin`
4. Copy the plugins: `cp -r badjware ~/.config/kustomize/plugin`

You are now ready to use the plugins. eg:
``` bash
kustomize build --enable_alpha_plugins ./kustomize/overlay
```

### Docker

A docker image is provided with the plugins and their dependencies already installed. Mount the directory with your kustomizations in the container and run kustomize. eg:
``` bash
docker run -v "$PWD/kustomize:/host" badjware/kustomize-plugins build --enable_alpha_plugins /host/overlays
```

## Plugins

The API description is in the directory of each plugins.

| Type | Name | Description |
| --- | --- | --- |
| Any | [Exec](./badjware/v1/exec/README.md) | Run an executable script as a plugin. |
| Transformer | [PlaceholderTransformer](./badjware/v1/placeholdertransformer/README.md) | Perform arbitrary key/value replacements in kubernetes resources. |
| Transformer | [SSMParameterPlaceholderTransformer](./badjware/v1/ssmparameterplaceholdertransformer/README.md) | Perform arbitrary key/value replacements in kubernetes resources with values from [AWS Systems Manager Parameters](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html). |