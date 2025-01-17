#!/bin/bash

set -e

echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "Installing required dependencies..."
sudo apt install -y ca-certificates curl gnupg

echo "Adding Docker’s official GPG key..."
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc > /dev/null
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "Adding Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "Updating package index..."
sudo apt update

echo "Installing Docker Engine, CLI, and containerd..."
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "Enabling and starting Docker service..."
sudo systemctl enable --now docker

echo "Adding current user to the Docker group..."
sudo usermod -aG docker $USER
newgrp docker

echo "Verifying Docker installation..."
docker --version

echo "Installing Docker Compose..."
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")')
sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "Verifying Docker Compose installation..."
docker-compose --version

echo "Docker and Docker Compose installation completed successfully!"
