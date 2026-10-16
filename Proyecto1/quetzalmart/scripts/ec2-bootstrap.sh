#!/bin/bash
# Prepara una EC2 para QuetzalMart: Docker + Compose, swap 2 GB, zona horaria.
# Soporta Amazon Linux 2023 (usuario ec2-user) y Ubuntu 22.04/24.04 (usuario ubuntu).
# Uso:  bash scripts/ec2-bootstrap.sh
set -euo pipefail
. /etc/os-release

echo ">> Sistema: $PRETTY_NAME"
sudo timedatectl set-timezone America/Guatemala || true

if ! command -v docker >/dev/null 2>&1; then
  if [ "$ID" = "amzn" ]; then
    echo ">> Instalando Docker (dnf)"
    sudo dnf install -y docker git unzip
  else
    echo ">> Instalando Docker (get.docker.com)"
    sudo apt-get update -y && sudo apt-get install -y unzip git
    curl -fsSL https://get.docker.com | sudo sh
  fi
fi
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER" || true

if ! sudo docker compose version >/dev/null 2>&1; then
  echo ">> Instalando plugin Docker Compose"
  sudo mkdir -p /usr/local/lib/docker/cli-plugins
  sudo curl -fsSL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" \
       -o /usr/local/lib/docker/cli-plugins/docker-compose
  sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
fi

if ! swapon --show | grep -q /swapfile; then
  echo ">> Creando swap de 2 GB"
  sudo fallocate -l 2G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  grep -q '^/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

mkdir -p "$(dirname "$0")/../facturas_pdf" "$(dirname "$0")/../backups"
sudo docker --version
sudo docker compose version
free -h
echo ">> Listo. Sal con 'exit' y vuelve a entrar por SSH para usar docker sin sudo."
