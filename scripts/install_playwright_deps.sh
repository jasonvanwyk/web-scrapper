#!/bin/bash

# Script to install Playwright system dependencies on Ubuntu
# This script should be run with sudo privileges

echo "Installing Playwright system dependencies..."

# Update package lists
apt-get update

# Install dependencies listed in the Playwright warning
apt-get install -y \
    libgtk-3-0 \
    libpangocairo-1.0-0 \
    libcairo-gobject2 \
    libgdk-pixbuf-2.0-0 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xvfb \
    fonts-liberation \
    fonts-noto-color-emoji

echo "Playwright dependencies installed successfully!"
echo "You can now run integration tests with: python -m pytest tests/integration/"
