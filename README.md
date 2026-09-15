# 文鉴

古文阅读与研读应用。Vue 前端与同源 HTTP 接口可通过一次启动运行；生产构建输出可部署的 Cloudflare Worker，无需一直开启本机。

## 运行

需要 Node.js 22.12+（或兼容的更新版本）。

```bash
npm ci
npm run dev
```

访问 `http://127.0.0.1:5173`。默认使用内置篇目资料，阅读、译注、语法、资料问答及笔记不需要 API 密钥。

```bash
npm run build
npm test
npm run preview
```

生产预览为 `http://127.0.0.1:4173`。构建产物位于 `dist/server/index.js` 与 `dist/client`，托管身份保存在 `.openai/hosting.json`。

## 已实现的功能

- 七篇阅读材料，包含明确标注的全文与选段，分别提供原文、段落译文、字词、语法、背景和赏析。
- 全文关键词与作者搜索、篇目切换、最近阅读和更多篇目。
- 鼠标划词、触摸选文和键盘可用的段落研读按钮；字词、语法、段落译文、知识、提问、摘录笔记。
- 基于本篇资料的主题问答；问题超出资料范围时明确说明，不伪装成通用 AI。
- 浏览器本地笔记的新建、编辑、删除、Markdown 导出。笔记不会自动跨设备同步，请定期导出。
- 深浅色主题、字号设置、移动端侧栏、键盘焦点管理、减少动态效果偏好。
- 真实 AI 兼容接口与知乎代理、超时/错误/限流提示、知乎站内搜索入口。
- 知识面板中的关联语料与出处；`/api/corpus` 及兼容搜索路径。
- 阅读设置内可显式切换 Mock 讨论，无密钥体验四类卡片，不冒充真实内容。

## 页面配置 AI

打开“设置 → AI API Key 配置”，选择 DeepSeek 或 OpenAI，填写模型 ID 与密钥，点击“测试连接并启用”。测试会发送一次可能计费的请求；成功后即可划词分析和追问。密钥仅保留在当前页面内存，刷新后重新填写；可点击“清除页面密钥”切回资料模式。页面凭据经后端转发，应用不记录密钥、不保存为全站配置，也不写入 Git。模型须支持现有聊天接口和 JSON 输出。

## 可选服务

开发与本地生产预览从 `backend/.env` 读取服务配置。线上通过托管平台的环境变量设置敏感值，不将密钥打包到前端。

```dotenv
AI_API_KEY=
AI_BASE_URL=
AI_MODEL=
USE_MOCK_AI=false
ZHIHU_API_KEY=
ZHIHU_BASE_URL=https://developer.zhihu.com
USE_MOCK_ZHIHU=false
```

AI 接口须支持 `${AI_BASE_URL}/chat/completions` 和 JSON 输出。配置后在“阅读设置”中选择 AI。没有有效密钥时开放式 AI 问答不可用。知乎可能受账号配额限制，应用不会绕过配额或用虚假结果代替。线上不配置密钥也能使用内置阅读资料。

原 Flask 服务保留在 `backend/`，适用于单独部署或继续使用 Jiayan 的场景；它不是当前托管版本的运行依赖。前端固定调用同源 `/api/*`，生产环境应由托管平台或 Nginx 反向代理到实际后端，避免浏览器直接请求远端 Worker。

```bash
cd backend
../.venv/bin/python -m unittest discover -s tests -v
../.venv/bin/python app.py
```

## 内容说明

古文原文为公有领域作品，各篇附原典链接。现代译注为本站整理的学习参考，可能存在异文或解释差异，不等同于审定教材。长篇的节选范围在标题旁标明。篇目资料模式返回所在段落译文，并明确标注范围，避免将整段译文误认为所选单字的解释。

## 上线与域名

公开 Demo：[文鉴](https://wenjian-reading.garyhu9527.chatgpt.site)。2026-09-15 已检查匿名访问，无需登录。

Sites 项目身份保存在 `.openai/hosting.json`。发布时保存与源码一致的构建版本。自定义 `www` 域名需要注册域名及 DNS 管理权限；平台生成的 HTTPS 地址不需要另购域名。

阿里云香港 Ubuntu 快速部署说明见 [deploy/README-SERVER.md](deploy/README-SERVER.md)。该方案由香港服务器托管 `dist/client` 静态文件，并把 `/api/*` 反向代理到现有 Worker origin。

## 项目书核对

详见 [核对修正版](docs/项目书-核对修正版.md) 与 [逐项核对清单](docs/项目书-逐项核对清单.md)。真实 AI 的外部验收与线上 Flask 架构不能标记为已完成。
