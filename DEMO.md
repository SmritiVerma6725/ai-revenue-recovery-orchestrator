# Linux Demo Runbook

Run these commands in Ubuntu or another Linux terminal. This setup uses Docker and synthetic data; no real money moves.

## Prerequisites

Install or enable:

- Docker Engine and Docker Compose plugin, or Docker Desktop with Ubuntu WSL integration
- Bash, `curl`, and `tar`
- WSL2 and Virtual Machine Platform when using Windows

Check Docker before continuing:

```bash
docker version
docker compose version
```

`docker version` must show both `Client` and `Server`.

For Docker Desktop, enable Ubuntu at:

```text
Settings -> Resources -> WSL Integration -> Ubuntu -> Apply & Restart
```

If Docker reports socket permission denied:

```bash
sudo usermod -aG docker "$USER"
```

Close and reopen Ubuntu before retrying `docker version`.

## Option A: Clone From GitHub

```bash
rm -rf ~/ai-revenue-recovery-demo
git clone https://github.com/SmritiVerma6725/ai-revenue-recovery-orchestrator.git ~/ai-revenue-recovery-demo
cd ~/ai-revenue-recovery-demo
```

## Option B: Extract The Tarball

If the tarball is on the Windows F: drive:

```bash
rm -rf ~/ai-revenue-recovery-demo
mkdir -p ~/ai-revenue-recovery-demo
ls -lh /mnt/f/Razorpay/ai-revenue-recovery-pipeline.tar.gz
tar -xzf /mnt/f/Razorpay/ai-revenue-recovery-pipeline.tar.gz \
  -C ~/ai-revenue-recovery-demo
cd ~/ai-revenue-recovery-demo
```

If it is already in your current directory:

```bash
rm -rf ~/ai-revenue-recovery-demo
mkdir -p ~/ai-revenue-recovery-demo
tar -xzf ai-revenue-recovery-pipeline.tar.gz \
  -C ~/ai-revenue-recovery-demo
cd ~/ai-revenue-recovery-demo
```

Confirm the files exist:

```bash
ls
```

You should see `Dockerfile`, `docker-compose.yml`, `backend`, `data`, `tests`, and `.env.example`.

## Configure Demo Mode

```bash
cp .env.example .env
```

Demo `.env` values:

```env
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
WEBHOOK_SECRET=
APP_ENV=development
```

Keep `.env` local. Do not commit it.

## Start And Check The Pipeline

```bash
docker compose config --quiet
docker compose down --remove-orphans 2>/dev/null || true
docker compose up --build -d
docker compose ps
```

Wait until the API is ready:

```bash
until curl -fsS http://localhost:8000/health; do
  sleep 2
done
echo
```

Expected:

```json
{"status":"ok","service":"ai-revenue-recovery"}
```

Check the main endpoints:

```bash
curl -sS http://localhost:8000/health; echo
curl -sS http://localhost:8000/api/dashboard; echo
curl -sS http://localhost:8000/api/recovery-cases; echo
curl -sS http://localhost:8000/api/agent/decision; echo
curl -sS http://localhost:8000/api/audit-trail; echo
curl -sS http://localhost:8000/api/recovery-timeline; echo
```

## Show Recovery Numbers Changing

This changes demo numbers only:

```bash
curl -sS -X POST http://localhost:8000/api/demo/simulate-recovery; echo
curl -sS http://localhost:8000/api/dashboard; echo
```

The recovered amount increases, revenue at risk decreases, and recovery rate is recalculated.

## Simulate A Successful Payment

```bash
curl -sS -X POST http://localhost:8000/api/webhooks/razorpay \
  -H "Content-Type: application/json" \
  -d '{"event":"payment.captured","payload":{"payment":{"entity":{"id":"pay_demo_123","amount":14999,"currency":"INR"}}}}'; echo
```

Expected response contains:

```json
{"status":"recovered","action":"stop"}
```

## Open The Website

Ubuntu/WSL:

```bash
explorer.exe http://localhost:8000
```

Native Ubuntu desktop:

```bash
xdg-open http://localhost:8000
```

For the video, show the dashboard cards, 30-day graph, recovery cases, agent decision, guardrails, audit trail, and `Simulate recovered payment`.

## Run Tests

```bash
docker compose exec api pytest -q
```

Expected result:

```text
36 passed
```

## Troubleshooting

### Docker command not found

Enable Docker Desktop WSL Integration for Ubuntu or install Docker Engine and Compose.

### Permission denied on `/var/run/docker.sock`

```bash
sudo usermod -aG docker "$USER"
```

Close and reopen Ubuntu, then run `docker version`.

### Connection refused or reset

```bash
docker compose ps
docker logs ai-revenue-recovery
docker compose down --remove-orphans
docker compose up --build -d
```

Wait with the health loop before using `curl`.

### Duplicate container name

```bash
docker rm -f ai-revenue-recovery
docker compose up --build -d
```

### Archive not found

```bash
find /mnt/f -name 'ai-revenue-recovery-pipeline.tar.gz' 2>/dev/null
```

## Stop The Demo

```bash
docker compose down
```
