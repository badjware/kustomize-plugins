#!/bin/sh

cat <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: example-configmap
data:
  foo: bar