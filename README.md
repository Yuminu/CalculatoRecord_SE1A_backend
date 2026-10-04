# studentID_calculator_backend

## 1. 项目简介（Project Introduction）

本项目是「前后端分离计算器系统」的**后端服务**。它负责：

- 接收前端发送的数学表达式并**安全地**解析、计算（不使用 `eval`/`exec`）；
- 对输入进行严格校验（非法字符、连续运算符、括号匹配等）；
- 将每次成功的计算结果持久化到 SQLite 数据库；
- 对外提供标准的 RESTful JSON 接口，并使用标准 HTTP 状态码；
- 提供历史记录的查询、单条删除与全部清除能力。

前端仓库负责界面交互，通过 HTTP/HTTPS 与后端通信，核心计算逻辑**全部在后端实现**。

## 2. 技术栈（Technology Stack）

| 组件 | 技术 | 版本 |
|------|------|------|
| Web 框架 | Flask | 3.0.3 |
| ORM | Flask-SQLAlchemy / SQLAlchemy | 3.1.1 / 2.0.31 |
| 数据库 | SQLite | 随 Python 内置 |
| 跨域 | Flask-Cors | 4.0.1 |
| 测试 | pytest | 8.3.2 |
| 生产服务器 | Gunicorn（Linux） | 22.0.0 |
| 表达式解析 | Python 标准库 `ast` + `decimal` | 内置 |

## 3. 运行环境（Runtime Environment）

- Python 3.10 及以上（开发环境使用 3.10.0）
- pip（随 Python 安装）
- 操作系统：Windows / macOS / Linux 均可（**生产部署使用 Linux**）

## 4. 安装方法（Installation Method）

```bash
# 进入后端仓库目录
cd studentID_calculator_backend

# 创建并激活虚拟环境（可选但推荐）
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 5. 启动方法（Startup Method）

### 开发模式

```bash
python run.py
```

后端将监听 `http://0.0.0.0:5000`。启动后访问
`http://localhost:5000/api/health` 应返回：

```json
{ "status": "ok", "message": "Calculator API is running" }
```

### 生产模式（Linux 服务器）

```bash
gunicorn --bind 0.0.0.0:5000 run:app
```

## 6. 配置说明（Configuration Instructions）

配置集中在 `app/config.py`，可通过环境变量覆盖：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `CORS_ORIGINS` | 允许跨域的来源，`*` 表示全部允许 | `*` |
| `SECRET_KEY` | 预留的会话密钥 | `calculator-dev-secret` |
| `MAX_HISTORY_RECORDS` | 历史记录上限 | `100`（代码内常量） |

复制 `.env.example` 为 `.env` 并按需修改即可。若前端与后端部署在同一
域名下（Nginx 反向代理），可将 `CORS_ORIGINS` 收紧为你的域名。

## 7. 数据库初始化方法（Database Initialization Method）

无需手动初始化。应用启动时（`create_app`）会自动：

1. 在项目根目录创建 `data/` 目录；
2. 在 `data/calculator.db` 创建 SQLite 数据库文件；
3. 检查并创建 `calculation_history` 表（若不存在）。

删除 `data/calculator.db` 后重启服务即可得到全新的空数据库。

### 数据表结构

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK AUTOINCREMENT | 主键 |
| expression | TEXT NOT NULL | 表达式 |
| result | REAL NOT NULL | 结果（8 位小数精度） |
| is_favorite | BOOLEAN DEFAULT 0 | 收藏标记（预留） |
| note | VARCHAR(50) | 备注（预留） |
| category | VARCHAR(50) | 分类（预留） |
| created_at | DATETIME | 计算时间 |

历史记录最多保留 **100 条**，超出时自动删除最旧的记录。

## 8. 前端/后端连接方法（Front-end/Back-end Connection Method）

后端不主动连接前端，只对外暴露 HTTP API。前端通过环境变量
`VITE_API_BASE_URL` 指定后端地址（默认 `http://localhost:5000`）。
后端已开启 CORS（`/api/*`），因此前端可直接跨端口访问，无需额外代理。

## 9. 项目目录结构（Project Structure）

```
studentID_calculator_backend/
├── app/
│   ├── __init__.py               # Flask 应用工厂
│   ├── config.py                 # 配置文件
│   ├── models/                   # 数据库模型
│   │   ├── calculation.py
│   │   └── history.py
│   ├── routes/                   # 路由
│   │   ├── calculate.py          # POST /api/calculate
│   │   ├── history.py            # GET/DELETE /api/history
│   │   └── health.py             # GET /api/health
│   ├── services/                 # 业务逻辑
│   │   ├── calculator.py         # 核心计算（安全解析）
│   │   └── history_service.py    # 历史记录服务
│   └── utils/
│       └── validators.py         # 输入验证
├── tests/
│   ├── test_calculator.py        # 计算服务单元测试
│   └── test_api.py               # API 接口测试
├── data/                         # SQLite 数据库（自动生成，不提交）
├── requirements.txt
├── run.py
├── nginx.conf
├── .env.example
├── README.md
└── codestyle.md
```

## API 接口一览

| 方法 | 路径 | 说明 | 成功状态码 |
|------|------|------|-----------|
| POST | `/api/calculate` | 计算表达式并保存 | 200 |
| GET | `/api/history` | 查询历史（`limit`/`offset`） | 200 |
| DELETE | `/api/history/{id}` | 删除单条历史 | 204 |
| DELETE | `/api/history` | 清空全部历史 | 204 |
| GET | `/api/health` | 健康检查 | 200 |

错误状态码：`400`（输入非法）、`404`（资源不存在）、`500`（服务器错误）。

## 测试方法

```bash
pytest -v
```

## 部署说明

1. SSH 登录 Linux 服务器，安装 Python 3 与 pip；
2. 克隆后端仓库并安装依赖：`pip install -r requirements.txt`；
3. 用 Gunicorn 启动：`gunicorn --bind 0.0.0.0:5000 run:app`；
4. 配置防火墙开放对应端口；
5. 参考 `nginx.conf` 使用 Nginx 反向代理 `/api/` 到后端（可选，用于生产）。
