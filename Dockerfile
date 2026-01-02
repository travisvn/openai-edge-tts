FROM python:3.12-slim

ARG INSTALL_FFMPEG=false
ARG PORT=5050
WORKDIR /app

RUN apt-get update && apt-get install -y curl

# Install ffmpeg conditionally
RUN if [ "$INSTALL_FFMPEG" = "true" ]; then \
    apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*; \
    fi

# Copy requirements and install them
COPY requirements.txt /app
RUN pip install -U --root-user-action=ignore -r requirements.txt

# Copy the app directory
COPY app/ /app

EXPOSE ${PORT}

HEALTHCHECK --interval=120s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Command to run the server
CMD ["python", "/app/server.py"]  