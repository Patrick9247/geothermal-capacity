# 地热产能计算

前后端分离的地热产能计算脚手架。

## 技术栈

- 后端：FastAPI、SQLAlchemy、SQLite、Pydantic
- 前端：Vue 3、Vite、Element Plus、ECharts

## 目录

```
backend/     # API 与领域计算逻辑
frontend/    # Vue 单页应用
docs/        # 接口与模型说明
```

## 快速启动

后端（Python 3.11+）：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

前端（Node.js 20+）：

```powershell
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173`；API 文档位于 `http://localhost:8000/docs`。

## 设计原则

- `domain/` 不依赖 FastAPI、数据库或 HTTP，计算模型可单独测试和复用。
- API 层只做请求编排与序列化；持久化细节隔离于 `repositories/`。
- 新计算模型只需实现 `CalculationModel` 协议并注册到服务中。

## 认证与用户

- 先使用唯一用户名和邮箱注册账号；系统中首位注册用户会自动成为管理员。登录支持用户名或邮箱。
- 登录后 API 使用 JWT Bearer 鉴权，计算接口需要登录。
- 管理员可在前端的“用户管理”页管理用户角色和启用状态；系统始终至少保留一名管理员。
- 部署前请在 `backend/.env` 设置强随机的 `JWT_SECRET_KEY`，不要使用示例默认值。
- 用户 ID 使用 64 位雪花 ID。多实例部署时，请为各实例分配不同的 `SNOWFLAKE_WORKER_ID`（0–1023）。
