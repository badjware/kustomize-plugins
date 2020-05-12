FROM python:3

ENV KUSTOMIZE_PLUGIN_HOME=/opt/kustomize/plugin

RUN cd /usr/bin && \
    curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash && \
    pip install --no-cache-dir pyyaml boto3

COPY ./badjware /opt/kustomize/plugin/badjware

ENTRYPOINT ["kustomize"]
CMD ["-h"]
