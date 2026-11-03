FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 ANGOLA_HOST=0.0.0.0 ANGOLA_PORT=8000
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt && useradd --system --uid 10001 --create-home appuser
COPY scripts/ ./scripts/
COPY records/ ./records/
COPY coverage/ ./coverage/
COPY sources/ ./sources/
COPY web/ ./web/
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=2).read()"
CMD ["python", "scripts/api.py"]
