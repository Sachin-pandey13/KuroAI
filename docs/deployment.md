# Deployment Guide

KuroAI supports three deployment configurations via Docker Compose.

## 1. Development (`docker-compose.dev.yml`)

Hot reload enabled for rapid iteration:

```bash
docker-compose -f docker-compose.dev.yml up --build
```

## 2. Production (`docker-compose.prod.yml`)

Multi-worker Uvicorn server running as a non-root user:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 3. GPU Acceleration (`docker-compose.gpu.yml`)

Passes host NVIDIA GPU to container for local model inference:

```bash
docker-compose -f docker-compose.gpu.yml up -d
```
