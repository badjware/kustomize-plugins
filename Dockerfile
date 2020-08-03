FROM python:3-slim

ENV KUSTOMIZE_PLUGIN_HOME=/opt/kustomize/plugin

COPY requirements.txt /requirements.txt
RUN cd /usr/bin && \
    apt-get update && \
    apt-get install -y curl patch && \
    curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash && \
    pip install --no-cache-dir -r /requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./badjware /opt/kustomize/plugin/badjware

ENTRYPOINT ["kustomize"]
CMD ["-h"]
