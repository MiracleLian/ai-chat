# 🤖 AI智能问答系统

大模型智能问答网页系统 —— 前后端分离架构，集成大语言模型实现AI对话。

## 项目架构

```
AIchat_project/
├── backend/                  # 后端服务 (FastAPI)
│   ├── main.py              # 入口文件
│   ├── requirements.txt     # Python依赖
│   ├── .env                 # 环境变量配置
│   └── app/
│       ├── database.py      # 数据库连接
│       ├── models.py        # 数据模型 (User, ChatRecord)
│       ├── schemas.py       # 请求/响应模型
│       ├── crud.py          # 数据库操作
│       ├── auth.py          # JWT认证
│       ├── llm.py           # 大模型调用
│       └── routers/
│           ├── auth.py      # 认证路由 (注册/登录/用户信息)
│           └── chat.py      # 对话路由 (发送问题/历史/删除)
│
├── frontend/                 # 前端应用 (Vue3)
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.js          # 入口
│       ├── App.vue          # 根组件
│       ├── api/index.js     # Axios封装 + 拦截器
│       ├── stores/auth.js   # 认证状态管理
│       ├── router/index.js  # 路由 + 守卫
│       └── views/
│           ├── Login.vue    # 登录页
│           ├── Register.vue # 注册页
│           ├── Chat.vue     # 对话页
│           ├── History.vue  # 历史记录页
│           └── UserInfo.vue # 个人信息页
│
└── docx_extracted/           # 需求文档
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + Vue Router + Axios |
| 后端 | Python + FastAPI + Uvicorn |
| 数据库 | SQLite（开发）/ MySQL（生产） |
| 认证 | JWT (python-jose + passlib) |
| AI集成 | OpenAI兼容API（硅基流动/DeepSeek/通义千问等） |

## 快速开始

### 1. 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（修改 .env 文件中的 AI_API_KEY）
# 至少需要配置 AI_API_KEY 才能启用真实AI对话

# 启动后端服务
uvicorn main:app --reload --port 8000
```

后端API文档：http://localhost:8000/docs

### 2. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端访问：http://localhost:3000

## AI模型配置

编辑 `backend/.env` 文件：

```env
# 使用硅基流动免费API（推荐新手）
AI_API_URL=https://api.siliconflow.cn/v1/chat/completions
AI_API_KEY=你的API密钥
AI_MODEL=Qwen/Qwen2.5-7B-Instruct

# 使用DeepSeek
# AI_API_URL=https://api.deepseek.com/v1/chat/completions
# AI_API_KEY=你的API密钥
# AI_MODEL=deepseek-chat

# 使用通义千问
# AI_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
# AI_API_KEY=你的API密钥
# AI_MODEL=qwen-turbo
```

> 不配置AI_API_KEY时，系统会返回模拟回答，方便前端调试。

## 功能清单

- ✅ 用户注册（用户名/密码/邮箱校验）
- ✅ 用户登录（JWT Token认证）
- ✅ AI实时对话（消息气泡，思考状态提示）
- ✅ 对话历史记录（分页、删除、批量删除）
- ✅ 个人信息查看
- ✅ 路由守卫（未登录自动跳转）
- ✅ Token自动管理（请求拦截添加，401自动登出）
- ✅ CORS跨域支持
- ✅ 密码加密存储（bcrypt）

## API接口一览

| 方法 | 路径 | 说明 | 需Token |
|------|------|------|---------|
| POST | /api/auth/register | 用户注册 | ❌ |
| POST | /api/auth/login | 用户登录 | ❌ |
| GET  | /api/auth/me | 获取用户信息 | ✅ |
| POST | /api/chat/send | 发送问题 | ✅ |
| GET  | /api/chat/history | 获取历史记录（分页） | ✅ |
| DELETE | /api/chat/{id} | 删除单条记录 | ✅ |
| POST | /api/chat/batch-delete | 批量删除记录 | ✅ |
