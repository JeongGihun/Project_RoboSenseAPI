#!/bin/bash
# 수동 배포 스크립트 — GitHub Actions 실패 시 폴백

set -e

EC2_HOST="${EC2_HOST:?EC2_HOST 환경변수 필요}"
EC2_USER="${EC2_USER:-ubuntu}"
SSH_KEY="${SSH_KEY:-~/.ssh/id_rsa}"

echo "=== EC2 배포 시작 ==="
ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" << 'REMOTE'
cd ~/robosense
docker compose pull
docker compose up -d
sleep 10
curl -f http://localhost/health && echo "배포 성공" || echo "Health check 실패"
REMOTE
