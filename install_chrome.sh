#!/bin/bash
set -e

# 1. Google Chrome 설치 (공식 APT 저장소 등록)
echo "[+] Installing latest Google Chrome..."
apt-get update && apt-get install -y wget gnupg2 curl unzip

# APT 키 추가
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg

# APT 소스 등록
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
  > /etc/apt/sources.list.d/google-chrome.list

# 크롬 설치
apt-get update && apt-get install -y google-chrome-stable

# 2. 설치된 Chrome 버전 확인
CHROME_VERSION=$(google-chrome --version | grep -oP "\d+\.\d+\.\d+\.\d+")
echo "[✓] Installed Chrome version: $CHROME_VERSION"

# 3. ChromeDriver 다운로드 (chrome-for-testing 저장소)
echo "[+] Downloading matching ChromeDriver $CHROME_VERSION ..."
wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" || {
  echo "[!] Failed to download chromedriver for version ${CHROME_VERSION}"
  exit 1
}

unzip chromedriver-linux64.zip
mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver
rm -rf chromedriver-linux64 chromedriver-linux64.zip

# 4. 확인
echo "[✓] Installed versions:"
google-chrome --version
chromedriver --version
