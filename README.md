# 🤖 AI 智能问答系统

基于 **DeepSeek 大模型** 的智能问答网页系统，前后端分离架构，一键启动。

## 效果预览

- 💬 AI 对话（Markdown 渲染、代码高亮、历史记录）
- 👤 用户注册 / 登录（JWT 认证）
- 📋 对话历史管理（分页、批量删除）
- ⚙️ 管理员在线配置（修改 API 参数即时生效，无需重启）
- 🎨 现代化 UI（渐变色主题、加载动画、响应式布局）

## 项目架构

```
ai-chat/
├── backend/                     # FastAPI 后端
│   ├── main.py                  # 入口，启动时自动创建管理员账号
│   ├── requirements.txt         # Python 依赖
│   ├── .env.example             # 环境变量模板（复制为 .env 填入自己的 Key）
│   └── app/
│       ├── database.py          # 数据库连接（SQLite）
│       ├── models.py            # 数据模型（User / ChatRecord）
│       ├── schemas.py           # 请求响应模型
│       ├── crud.py              # 数据库操作
│       ├── auth.py              # JWT 认证 + 管理员权限
│       ├── config.py            # .env 读写，支持热更新
│       ├── llm.py               # 大模型调用（Anthropic Messages API）
│       └── routers/
│           ├── auth.py          # 认证路由（注册/登录/用户信息/管理员）
│           ├── chat.py          # 对话路由（发送/历史/删除/批量删除/统计）
│           └── admin.py         # 管理员配置路由（登录/查看/修改 AI 配置）
│
└── frontend/                    # Vue3 前端
    ├── package.json
    ├── vite.config.js           # Vite 构建配置
    └── src/
        ├── main.js              # 入口（Element Plus 全局注册）
        ├── App.vue              # 根组件（页面过渡动画）
        ├── api/index.js         # Axios 封装（Token 拦截、401 自动登出）
        ├── stores/auth.js       # 认证状态管理（sessionStorage）
        ├── router/index.js      # 路由 + 守卫（未登录重定向）
        └── views/
            ├── Login.vue         # 登录页
            ├── Register.vue      # 注册页
            ├── Chat.vue          # 对话页（Markdown 渲染、重试、快捷提问）
            ├── History.vue       # 历史记录（分页、批量删除、详情弹窗）
            ├── UserInfo.vue      # 个人信息（对话统计、管理员面板）
            └── AdminConfig.vue   # 管理员配置页（API 地址/密钥/模型/温度等）
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + Vue Router 4 + Axios + Marked |
| 后端 | Python 3.10+ + FastAPI + Uvicorn + SQLAlchemy |
| 数据库 | SQLite（开发） |
| 认证 | JWT（python-jose + passlib + bcrypt） |
| AI 集成 | DeepSeek Anthropic Messages API（兼容 OpenAI/硅基流动等） |

## 快速开始（一键启动）

### 1. 克隆项目

```bash
git clone https://github.com/MiracleLian/ai-chat.git
cd ai-chat
```

### 2. 配置环境变量

```bash
cd backend
# 复制模板为 .env
cp .env.example .env        # Linux/Mac
copy .env.example .env       # Windows
```

编辑 `.env`，填入你的 AI API 密钥：

```env
# 必填：API 地址和密钥（支持 Anthropic Messages API 兼容接口）
AI_API_URL=https://api.deepseek.com/anthropic/v1/messages
AI_API_KEY=你的DeepSeek-API-Key    # 在这填入你的真实 Key
AI_MODEL=DeepSeek-V4-pro

# 可选：模型参数
AI_TEMPERATURE=0.7        # 0=严谨, 1=创意
AI_MAX_TOKENS=1024         # 回复最大长度
AI_SYSTEM_PROMPT=你是一个智能助手

# 可选：管理员密码（启动时自动创建 admin 账号）
ADMIN_USERNAME=admin
ADMIN_PASSWORD=请修改为你的密码
```

> 🔑 **如何获取 API Key？** 注册 [DeepSeek 开放平台](https://platform.deepseek.com/)，充值任意金额，打开 API Keys 页面复制。

### 3. 构建前端（使用已提供的前端资源）

如果你需要修改前端代码：

```bash
cd frontend
npm install
npm run build      # 构建到 dist/ 目录
```

> 如果你不需要修改前端，`frontend/dist/` 目录已经包含在仓库中，无需额外构建。（如果仓库不含 dist，则需本地构建一次）

### 4. 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 一键启动（前后端合并，单端口）
python main.py
```

打开浏览器访问 **http://127.0.0.1:8000**

## 功能清单

| 功能 | 说明 |
|------|------|
| ✅ 用户注册 | 用户名 6-20 位 / 密码 8-20 位含字母+数字 / 邮箱可选 |
| ✅ 用户登录 | JWT Token 认证，24 小时有效 |
| ✅ 个人信息 | 对话统计、管理员标识、退出登录 |
| ✅ AI 对话 | Markdown 渲染、代码高亮、一键重试、消息复制 |
| ✅ 历史记录 | 分页查询、单条删除、批量删除、详情弹窗 |
| ✅ 管理员配置 | 在线修改 API 地址/密钥/模型/温度/提示词，保存即时生效 |
| ✅ 路由守卫 | 未登录自动跳转登录页，401 自动清除 Token |
| ✅ 密码加密 | bcrypt 加密存储 |

## 使用教程

### 1. 注册账号

打开 `http://localhost:8000` → 点击「去注册」→ 填写信息：

- **用户名**：6-20 位，仅限字母和数字
- **密码**：8-20 位，必须同时包含字母和数字
- **邮箱**：选填

注册成功后自动登录，跳转至对话页面。

### 2. 开始 AI 对话

在输入框输入问题，按 `Enter` 发送（`Shift+Enter` 换行）：

- 支持 Markdown 渲染（代码块、表格、列表等）
- 代码块自动语法高亮
- 每条消息可以复制、失败可以重试
- 点击快捷提问标签可一键发送

### 3. 查看历史记录

点击顶部导航栏「历史记录」→ 查看所有对话：

- 点击卡片查看完整 Q&A 详情
- 支持单条删除和批量删除
- 分页浏览，支持跳转页码

### 4. 个人信息

点击顶部导航栏「个人信息」→ 查看：

- 用户 ID、用户名、邮箱、注册时间
- 对话总数统计
- 管理员状态标识

### 5. 管理员配置

点击对话页右上角 **⚙️** 图标：

- 输入管理员账号密码（默认 `admin` / 见 `.env` 配置）
- 进入配置页面，可修改：
  - **API 地址和密钥** — 切换不同 AI 服务商
  - **模型名称** — 切换模型版本
  - **温度参数** — 滑块调整 0（严谨）~ 1（创意）
  - **最大 Token** — 回复长度限制
  - **系统提示词** — 自定义 AI 角色和行为
- 保存后**即时生效**，无需重启服务

## API 接口一览

| 方法 | 路径 | 说明 | Token |
|------|------|------|-------|
| POST | `/api/auth/register` | 用户注册 | ❌ |
| POST | `/api/auth/login` | 用户登录 | ❌ |
| GET | `/api/auth/me` | 获取用户信息 | ✅ |
| POST | `/api/chat/send` | 发送问题 | ✅ |
| GET | `/api/chat/history` | 历史记录（分页） | ✅ |
| GET | `/api/chat/count` | 对话统计 | ✅ |
| DELETE | `/api/chat/{id}` | 删除单条记录 | ✅ |
| POST | `/api/chat/batch-delete` | 批量删除 | ✅ |
| POST | `/api/admin/login` | 管理员登录，返回 JWT | ❌ |
| GET | `/api/admin/config` | 获取 AI 配置 | ✅ (admin) |
| PUT | `/api/admin/config` | 修改 AI 配置（热更新） | ✅ (admin) |
| GET | `/api/admin/check` | 检查是否管理员 | ✅ |

## 管理员功能

对话页右上角点击 **⚙️** → 输入管理员账号密码 → 进入配置页面：

- 修改 API 地址和密钥（切换不同 AI 服务商）
- 调整模型温度（0=严谨 / 1=创意）
- 修改系统提示词（自定义 AI 角色）
- 保存后 **即时生效**，无需重启服务

## 常见问题

**Q: 启动后 AI 返回"模拟回答"？**
A: 检查 `backend/.env` 中 `AI_API_KEY` 是否正确填入。

**Q: 前端页面空白？**
A: 确认 `frontend/dist/` 目录存在。若不存在，需执行 `cd frontend && npm install && npm run build`。

**Q: 想用其他 AI 服务商？**
A: 修改 `.env` 中的 `AI_API_URL` 和 `AI_MODEL` 即可，项目使用 Anthropic Messages API 格式，兼容 DeepSeek 等平台。

**Q: 如何切换到 MySQL？**
A: 修改 `.env` 中 `DATABASE_URL=mysql+pymysql://用户名:密码@localhost/数据库名`，并安装 `pip install pymysql`。

## 开发环境要求

- Python ≥ 3.10
- Node.js ≥ 16
- Windows / Linux / macOS
