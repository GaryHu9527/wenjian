# 5分钟上线

假设阿里云香港 Ubuntu 服务器公网 IP 是 `1.2.3.4`。

第一步，在本地把初始化脚本传到服务器：

```bash
scp deploy/scripts/server-init.sh root@1.2.3.4:/root/
```

第二步，登录服务器并执行一次初始化：

```bash
ssh root@1.2.3.4
bash /root/server-init.sh
```

第三步，回到 Mac 的项目根目录，上传构建产物并启用 Nginx 代理：

```bash
SERVER_IP=1.2.3.4 \
WORKER_ORIGIN=https://真实地址.workers.dev \
bash deploy/scripts/deploy.sh
```

第四步，浏览器打开：

```text
http://1.2.3.4
```

## WORKER_ORIGIN 怎么填

仓库里没有发现 `wrangler.toml`、`wrangler.json` 或 `wrangler.jsonc`，也没有发现真实的 `workers.dev` origin，所以这里不硬编码 Worker 地址。

`WORKER_ORIGIN` 只能填 origin，不能带路径：

```text
https://xxx.workers.dev
```

不要写成：

```text
https://xxx.workers.dev/api
https://xxx.workers.dev/api/health
```

当前项目的 Worker API 路径就是 `/api/*`，例如 `/api/health`、`/api/analyze`、`/api/chat`、`/api/zhihu/search`。Nginx 配置会把用户浏览器访问的 `http://SERVER_IP/api/...` 原样转发到 `WORKER_ORIGIN/api/...`。

如果只是临时赶 Demo，也可以把 `WORKER_ORIGIN` 填成当前可用的完整线上 origin。浏览器仍然只访问香港服务器的 `http://SERVER_IP` 和 `http://SERVER_IP/api/*`。

## 服务器安全组

阿里云轻量应用服务器或 ECS 安全组至少开放：

```text
22/TCP
80/TCP
```

不要把开发端口开放到公网，例如：

```text
5000
5173
3000
```

这套部署暂时不做域名、不做 ICP 备案、不做 HTTPS。最终访问地址是 `http://SERVER_IP`。

## 脚本说明

`deploy/scripts/server-init.sh` 在全新的 Ubuntu 22.04 / 24.04 服务器上执行一次。它会安装 `nginx`、`curl`、`ca-certificates`、`rsync`、`unzip`，创建 `/var/www/wenjian`，删除 Ubuntu 默认站点，启用文鉴站点并重启 Nginx。

`deploy/scripts/deploy.sh` 在 Mac 项目根目录执行。它会自动识别 `pnpm`、`yarn` 或 `npm`，安装依赖，执行生产构建，上传静态文件到 `/var/www/wenjian/`，上传 Nginx 配置，执行 `nginx -t`，重载 Nginx，并检查：

```text
http://SERVER_IP/
http://SERVER_IP/api/health
```

默认 SSH 用户是 `root`。如果服务器不是 root 登录，可以这样执行，但该用户需要免密 `sudo`：

```bash
SERVER_IP=1.2.3.4 \
SSH_USER=ubuntu \
WORKER_ORIGIN=https://真实地址.workers.dev \
bash deploy/scripts/deploy.sh
```

如需非 22 端口：

```bash
SERVER_IP=1.2.3.4 \
SSH_PORT=2222 \
WORKER_ORIGIN=https://真实地址.workers.dev \
bash deploy/scripts/deploy.sh
```

## 当前项目结构判断

- 前端项目目录：项目根目录。
- 包管理器：当前仓库存在 `package-lock.json`，默认使用 `npm`。
- Vite 配置：`vite.config.js`，开发环境把 `/api` 交给本地 Worker API 处理。
- 前端 API 调用：`src/services/api.js`，固定使用同源 `/api/*`。
- Worker 代码目录：`server/`，入口是 `server/worker.js`，业务 API 在 `server/api.js`。
- 构建输出：`dist/client` 是 Nginx 静态文件目录，`dist/server/index.js` 是自包含 Worker 产物。
- 真实 Worker origin：仓库内未发现 `workers.dev` origin；部署时用 `WORKER_ORIGIN` 显式传入。
- 硬编码地址：源码中没有浏览器会直接请求的 `workers.dev`、`localhost` 或 `127.0.0.1` API 地址。`localhost` 只存在于开发服务器、预览说明和 Flask CORS 默认配置。

## 环境变量和密钥

前端不会打包 API 密钥。AI 与知乎服务密钥应继续放在 Worker 或后端运行环境中，例如：

```text
AI_API_KEY
AI_BASE_URL
AI_MODEL
ZHIHU_API_KEY
ZHIHU_BASE_URL
```

不要把这些值写入 `.env.local`、`VITE_*` 或任何会进入 Vue 构建产物的配置。
