#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "请使用 root 执行：bash /root/server-init.sh" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y nginx curl ca-certificates rsync unzip

install -d -m 0755 -o www-data -g www-data /var/www/wenjian

cat >/var/www/wenjian/index.html <<'HTML'
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>文鉴服务器已初始化</title>
  <style>
    body{margin:0;min-height:100vh;display:grid;place-items:center;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f7f4ed;color:#1f2933}
    main{max-width:560px;padding:32px;line-height:1.7}
  </style>
</head>
<body>
  <main>
    <h1>文鉴服务器已初始化</h1>
    <p>请在本地项目根目录运行 deploy/scripts/deploy.sh 上传正式构建产物。</p>
  </main>
</body>
</html>
HTML

rm -f /etc/nginx/sites-enabled/default

cat >/etc/nginx/sites-available/wenjian <<'NGINX'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;
    root /var/www/wenjian;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        add_header Content-Type text/plain;
        return 503 "文鉴静态服务器已初始化，API 代理将在 deploy.sh 上传配置后启用。\n";
    }
}
NGINX

ln -sfn /etc/nginx/sites-available/wenjian /etc/nginx/sites-enabled/wenjian
chown -R www-data:www-data /var/www/wenjian

nginx -t
systemctl enable nginx
systemctl restart nginx

echo "文鉴服务器基础环境已完成。下一步在本地项目根目录运行 deploy/scripts/deploy.sh。"
