#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "错误：$*" >&2
  exit 1
}

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

command -v node >/dev/null 2>&1 || fail "未找到 node，请先安装 Node.js。"
command -v rsync >/dev/null 2>&1 || fail "未找到 rsync，请先在本机安装 rsync。"
command -v ssh >/dev/null 2>&1 || fail "未找到 ssh。"
command -v scp >/dev/null 2>&1 || fail "未找到 scp。"
command -v curl >/dev/null 2>&1 || fail "未找到 curl。"

: "${SERVER_IP:?请先设置 SERVER_IP，例如 SERVER_IP=1.2.3.4}"
: "${WORKER_ORIGIN:?请先设置 WORKER_ORIGIN，例如 WORKER_ORIGIN=https://xxx.workers.dev}"

SSH_USER="${SSH_USER:-root}"
SSH_PORT="${SSH_PORT:-22}"

case "$SERVER_IP" in
  *[!A-Za-z0-9._:-]*) fail "SERVER_IP 只能包含 IP、域名或常用主机字符。" ;;
esac

case "$SSH_USER" in
  *[!A-Za-z0-9._-]*) fail "SSH_USER 只能包含用户名常用字符。" ;;
esac

case "$SSH_PORT" in
  *[!0-9]*) fail "SSH_PORT 必须是数字。" ;;
esac

worker_meta="$(mktemp)"
rendered_nginx="$(mktemp)"
health_body="$(mktemp)"
cleanup() {
  rm -f "$worker_meta" "$rendered_nginx" "$health_body"
}
trap cleanup EXIT

if ! node --input-type=module >"$worker_meta" <<'NODE'
const raw = process.env.WORKER_ORIGIN
try {
  const url = new URL(raw)
  if (!['https:', 'http:'].includes(url.protocol)) throw new Error('scheme')
  if ((url.pathname && url.pathname !== '/') || url.search || url.hash) {
    console.error('WORKER_ORIGIN 只能填 origin，例如 https://xxx.workers.dev，不要带 /api、查询参数或 #。')
    process.exit(2)
  }
  console.log(url.origin)
  console.log(url.host)
  console.log(url.hostname)
} catch {
  console.error('WORKER_ORIGIN 不是有效地址，例如 https://xxx.workers.dev')
  process.exit(2)
}
NODE
then
  fail "WORKER_ORIGIN 校验失败。"
fi

WORKER_ORIGIN_CLEAN="$(sed -n '1p' "$worker_meta")"
WORKER_HOST="$(sed -n '2p' "$worker_meta")"
WORKER_TLS_NAME="$(sed -n '3p' "$worker_meta")"
export WORKER_ORIGIN_CLEAN WORKER_HOST WORKER_TLS_NAME RENDERED_NGINX="$rendered_nginx"

if [ -f pnpm-lock.yaml ]; then
  PACKAGE_MANAGER="pnpm"
  command -v pnpm >/dev/null 2>&1 || fail "检测到 pnpm-lock.yaml，但本机没有 pnpm。"
  pnpm install --frozen-lockfile
  pnpm run build
elif [ -f yarn.lock ]; then
  PACKAGE_MANAGER="yarn"
  command -v yarn >/dev/null 2>&1 || fail "检测到 yarn.lock，但本机没有 yarn。"
  yarn install --frozen-lockfile
  yarn build
elif [ -f package-lock.json ]; then
  PACKAGE_MANAGER="npm"
  npm ci
  npm run build
else
  PACKAGE_MANAGER="npm"
  npm install
  npm run build
fi

if [ -f dist/client/index.html ]; then
  BUILD_DIR="dist/client"
elif [ -f dist/index.html ]; then
  BUILD_DIR="dist"
else
  fail "构建完成但没有找到 dist/client/index.html 或 dist/index.html。"
fi

node --input-type=module <<'NODE'
import { readFileSync, writeFileSync } from 'node:fs'

let conf = readFileSync('deploy/nginx/wenjian.conf', 'utf8')
const replacements = {
  WORKER_ORIGIN: process.env.WORKER_ORIGIN_CLEAN,
  WORKER_HOST: process.env.WORKER_HOST,
  WORKER_TLS_NAME: process.env.WORKER_TLS_NAME,
}

for (const [key, value] of Object.entries(replacements)) {
  conf = conf.split(key).join(value)
}

writeFileSync(process.env.RENDERED_NGINX, conf)
NODE

REMOTE="${SSH_USER}@${SERVER_IP}"
REMOTE_TMP="/tmp/wenjian-deploy-$(date +%s)-$$"
SSH_ARGS=(-p "$SSH_PORT")

if [ "$SSH_USER" = "root" ]; then
  SUDO=""
else
  SUDO="sudo"
fi

echo "使用包管理器：$PACKAGE_MANAGER"
echo "上传静态文件目录：$BUILD_DIR"
echo "Worker Origin：$WORKER_ORIGIN_CLEAN"

ssh "${SSH_ARGS[@]}" "$REMOTE" "rm -rf '$REMOTE_TMP' && mkdir -p '$REMOTE_TMP/client'"
RSYNC_RSH="ssh -p $SSH_PORT" rsync -az --delete "$BUILD_DIR"/ "$REMOTE:$REMOTE_TMP/client/"
scp -P "$SSH_PORT" "$rendered_nginx" "$REMOTE:$REMOTE_TMP/wenjian.conf" >/dev/null

ssh "${SSH_ARGS[@]}" "$REMOTE" "\
  $SUDO install -d -m 0755 -o www-data -g www-data /var/www/wenjian && \
  $SUDO rsync -a --delete '$REMOTE_TMP/client/' /var/www/wenjian/ && \
  $SUDO chown -R www-data:www-data /var/www/wenjian && \
  $SUDO install -m 0644 '$REMOTE_TMP/wenjian.conf' /etc/nginx/sites-available/wenjian && \
  $SUDO ln -sfn /etc/nginx/sites-available/wenjian /etc/nginx/sites-enabled/wenjian && \
  $SUDO nginx -t && \
  $SUDO systemctl reload nginx && \
  rm -rf '$REMOTE_TMP'"

if ! curl -fsSI --max-time 10 "http://${SERVER_IP}/" >/dev/null; then
  fail "部署后首页健康检查失败：无法访问 http://${SERVER_IP}/"
fi

if ! curl -fsS --max-time 15 "http://${SERVER_IP}/api/health" >"$health_body"; then
  fail "部署后 API 健康检查失败：无法访问 http://${SERVER_IP}/api/health"
fi

if ! grep -q '"success":true' "$health_body"; then
  fail "API 健康检查返回异常：$(cat "$health_body")"
fi

echo "文鉴已部署："
echo "http://${SERVER_IP}"
