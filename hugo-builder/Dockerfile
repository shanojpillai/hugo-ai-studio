FROM alpine:3.18

WORKDIR /sites

# Install newer version of Hugo
RUN wget https://github.com/gohugoio/hugo/releases/download/v0.147.0/hugo_0.147.0_linux-amd64.tar.gz && \
    tar -xzf hugo_0.147.0_linux-amd64.tar.gz -C /usr/local/bin/ && \
    rm hugo_0.147.0_linux-amd64.tar.gz

COPY scripts/build-site.sh /usr/local/bin/
COPY scripts/validate-site.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/build-site.sh /usr/local/bin/validate-site.sh

# Use tail -f /dev/null as a simple way to keep the container running
CMD ["tail", "-f", "/dev/null"]
