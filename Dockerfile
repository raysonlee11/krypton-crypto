FROM ubuntu:24.04

LABEL org.opencontainers.image.title="krypton-crypto" \
      org.opencontainers.image.description="Krypton-style cryptography wargame (4 levels) over SSH" \
      org.opencontainers.image.licenses="MIT"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server python3 xxd coreutils vim-tiny nano less file bsdextrautils \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd \
    && sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config \
    && echo 'AllowTcpForwarding no' >> /etc/ssh/sshd_config \
    && echo 'X11Forwarding no' >> /etc/ssh/sshd_config

# Players: krypton0 .. krypton4
RUN for i in 0 1 2 3 4; do useradd -m -s /bin/bash krypton$i; done \
    && rm -f /home/krypton*/.bash_logout

COPY levels/ /opt/krypton/
COPY motd /etc/motd
COPY entrypoint.sh /entrypoint.sh
RUN chmod 700 /opt/krypton /entrypoint.sh && chmod 644 /etc/motd

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
