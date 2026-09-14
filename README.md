# 文鉴

面向古文阅读的学习应用。前端提供篇目阅读、划词分析、白话译文、语法与知识卡片、相关问答和追问；Flask 后端提供分析、语料、问答与知乎内容接口。

默认以本地 mock 数据运行，因此无需 API 密钥即可体验完整界面。

## 本地启动

前端：

```bash
npm install
npm run dev
```

前端默认使用 mock 数据。要调用本地后端，请复制 `.env.example` 为 `.env.local`，并设置：

```dotenv
VITE_USE_MOCK=false
VITE_API_BASE_URL=http://127.0.0.1:5000
```

后端（建议 Python 3.10–3.13）：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install Flask Flask-Cors python-dotenv requests gunicorn
cp backend/.env.example backend/.env
cd backend && ../.venv/bin/python app.py
```

`backend/requirements.txt` 中的 `jiayan` 是可选的古汉语 NLP 增强组件；它还需要单独下载模型文件。未安装时系统会自动退回到内置规则分析，不影响启动和基础功能。

## 验证

```bash
npm run build
cd backend && ../.venv/bin/python -m unittest discover -s tests -v
```

## 配置

后端配置样例位于 `backend/.env.example`，包括 AI 兼容接口、知乎凭证、跨域来源和缓存时长。凭证只应放在 `backend/.env`，不要提交到版本库。
