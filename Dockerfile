FROM python:3

ENV KUSTOMIZE_PLUGIN_HOME=/opt/kustomize/plugin

COPY requirements.txt /requirements.txt
RUN cd /usr/bin && \
    curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash && \
    pip install --no-cache-dir -r /requirements.txt

COPY ./badjware /opt/kustomize/plugin/badjware

ENTRYPOINT ["kustomize"]
CMD ["-h"]
