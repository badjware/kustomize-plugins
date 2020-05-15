# RemoteResource

Download kubernetes resources from a remote location with an optional sha256 checksum validation.

## Dependencies

* PyYAML

## API

| Field | Description | Type |  Default |
| --- | --- | --- | --- |
| `resources` | A list of resources to download | list of resource | |

## Resource
| Field | Description | Type |  Default |
| --- | --- | --- | --- |
| `url` | The url of the resource. | string | |
| `sha256` | An optional sha256 checksum of the resource. | string | |

## Example

*`kustomization.yaml`*
``` yaml
generators:
  - remoteresources-example.yaml
```

*`remoteresources-example.yaml`*
``` yaml
apiVersion: badjware/v1
kind: RemoteResources
metadata:
  name: not-important
resources:
  - url: https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml
    sha256: d8b96dfa27da511d5116fc3583281dd1da709c3c6e07b033e4f3424bc2ab64c8
```

### Result
``` yaml
apiVersion: v1
kind: Namespace
metadata:
  name: kubernetes-dashboard
---
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    k8s-app: kubernetes-dashboard
  name: kubernetes-dashboard
  namespace: kubernetes-dashboard
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  labels:
    k8s-app: kubernetes-dashboard
  name: kubernetes-dashboard
  namespace: kubernetes-dashboard
rules:
- apiGroups:
  - ""
  resourceNames:
  - kubernetes-dashboard-key-holder
  - kubernetes-dashboard-certs
  - kubernetes-dashboard-csrf
  resources:
  - secrets
  verbs:
  - get
  - update
  - delete
- apiGroups:
  - ""
  resourceNames:
  - kubernetes-dashboard-settings
  resources:
  - configmaps
  verbs:
  - get
  - update
- apiGroups:
  - ""
  resourceNames:
  - heapster
  - dashboard-metrics-scraper
  resources:
  - services
  verbs:
  - proxy
- apiGroups:
  - ""
  resourceNames:
  - heapster
  - 'http:heapster:'
  - 'https:heapster:'
  - dashboard-metrics-scraper
  - http:dashboard-metrics-scraper
  resources:
  - services/proxy
  verbs:
  - get
---
# [...]
```