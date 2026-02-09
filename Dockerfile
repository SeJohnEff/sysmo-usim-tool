FROM ubuntu:24.04

LABEL maintainer="John Fornehed <john.fornehed@gmail.com>"
LABEL description="sysmo-usim-tool - SIM/USIM card programming tool with GUI"

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-tk \
    python3-venv \
    python3-dev \
    build-essential \
    pcscd \
    pcsc-tools \
    libpcsclite-dev \
    swig \
    dbus \
    polkitd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy application code
COPY . .

# Make entrypoint and CLI tools executable
RUN chmod +x docker-entrypoint.sh \
    && chmod +x sysmo-isim-tool.sja2.py \
    && chmod +x sysmo-isim-tool.sja5.py \
    && chmod +x sysmo-usim-tool.sjs1.py \
    && chmod +x gui_main.py

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gui"]
