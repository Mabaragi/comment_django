FROM python:3.12.10-slim

COPY install_chrome.sh /tmp/install_chrome.sh
# 시스템 패키지 업데이트 및 Poetry 설치
RUN apt-get update && apt-get install -y\
    unzip curl wget gnupg2 \
    libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 libxss1 libappindicator3-1 \
    libasound2 libatk-bridge2.0-0 libcups2 libxrandr2 libxdamage1 libxcomposite1 \
    libx11-xcb1 libgtk-3-0 && \
    curl -sSL https://install.python-poetry.org | python3 -

RUN chmod +x /tmp/install_chrome.sh && /tmp/install_chrome.sh

# 환경 변수 설정
ENV PATH="/root/.local/bin:$PATH"
WORKDIR /app

# Poetry 설정 (가상환경 생성 비활성화)
RUN poetry config virtualenvs.create false

# 프로젝트 파일 복사
COPY pyproject.toml poetry.lock* /app/
RUN poetry add psycopg2-binary
RUN poetry install --no-root
COPY . /app
