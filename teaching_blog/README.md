# 师备云系统

一个专为教育工作者设计的现代化智能教学平台，集成了AI智能助手、学习进度管理、内容管理、用户交互和自动内容聚合等功能。支持教师发布教学笔记、分享教育资源、交流教育心得，并提供智能备课和课件优化等AI功能。

## ✨ 核心功能

### 📝 内容管理

- **📚 教学笔记** - 统一管理教学笔记、教育资源与教育心得
- **🗂️ 分类管理** - 灵活的文章分类系统
- **🏷️ 标签系统** - 便于内容检索和推荐

### 🤖 AI智能助手（智能体中心）

- **🧠 一键备课** - 上传教材文件，基于教材内容智能生成教案大纲（大模板），流式输出显示，对话式修改和优化
- **📊 课件优化器** - AI分析课件内容，提出优化建议，提升课件视觉效果与教学效果
- **💬 AI对话** - 智能问答，解答教学相关问题，支持流式输出
- **✍️ 文本优化** - 摘要生成、内容润色、标题优化

### 📈 学习进度管理

- **📊 进度跟踪** - 实时记录学习状态和时间，可视化展示学习路径
- **🎯 困难定位** - 自动识别理解程度低的内容节点，精准定位薄弱环节
- **📉 数据分析** - 多维度图表展示知识技能基础、认知能力、学习特点及趋势
- **💡 节奏建议** - 基于学习数据提供个性化学习节奏调整建议

### 🎓 一键备课（完整版）

- **📄 教材上传** - 支持上传 PDF/Word/TXT 格式的教材文件
- **🧠 知识提取** - 自动识别重点/难点/一般知识点，流式提取并实时跟踪
- **❓ 智能出题** - 对话驱动生成课题，支持自定义要求（数量、难度、题型），多格式导出（Word/PDF/TXT/HTML）
- **📋 复习卡片** - 知识点复习精卓卡片，图标化展示，支持打印和导出

<br />

### 👥 用户系统

- **👤 用户注册/登录** - 完整的用户认证系统
- **💖 收藏功能** - 收藏喜欢的文章和资源
- **📖 阅读历史** - 记录阅读轨迹和时长
- **💬 评论互动** - 读者评论和互动交流
- **👥 关注系统** - 关注喜爱的作者

### 🔧 管理后台

- **📊 数据统计** - 文章、用户、评论等数据概览
- **📝 内容管理** - 文章 CRUD 操作、分类管理
- **👥 用户管理** - 用户列表、权限设置
- **⏱️ 调度控制** - 控制定时爬取任务

## 🛠️ 技术栈

- **后端**: Flask + Python
- **数据库**: MySQL + SQLAlchemy ORM
- **模板**: Jinja2
- **前端**: Bootstrap 5 + 自定义 CSS + Chart.js
- **AI集成**: OpenAI API / 兼容接口
- **爬虫**: BeautifulSoup + 定时任务
- **前端框架**: OpenMAIC (Next.js) - AI课堂模块

## 📁 项目结构

```
teaching_blog/
├── app.py                          # 应用工厂入口
├── config.py                       # 配置管理
├── requirements.txt                # 依赖包列表
├── models/
│   └── __init__.py                # 数据库模型定义 (含 LearningProgress, ContentNode)
├── routes/
│   ├── client.py                   # 客户端路由
│   └── admin.py                    # 管理端路由
├── services/
│   ├── ai_service.py               # AI服务模块 (含备课/出题/进度管理等API)
│   ├── international_crawler.py    # 国际新闻爬虫
│   ├── news_service.py             # 新闻服务
│   └── scheduler.py                # 定时任务调度器
├── templates/
│   ├── client/                     # 客户端页面模板
│   │   ├── base.html               # 基础模板
│   │   ├── index.html              # 首页
│   │   ├── post.html               # 文章详情
│   │   ├── category.html           # 分类页面
│   │   ├── type.html               # 类型页面
│   │   ├── search.html             # 搜索页面
│   │   ├── login.html              # 登录页面
│   │   ├── register.html           # 注册页面
│   │   ├── publish.html            # 发布页面
│   │   ├── about.html              # 关于页面
│   │   ├── agent_center.html       # 智能体中心
│   │   ├── lesson_planner.html     # 备课助手 / 一键备课(完整版)
│   │   ├── courseware_optimizer.html # 课件优化器
│   │   ├── international_news.html # 国际动态
│   │   ├── learning_progress.html  # 学习进度管理
│   │   ├── ai_classroom.html       # AI课堂嵌入页
│   │   ├── openmaic_embed.html     # OpenMAIC嵌入组件
│   │   ├── favorites.html          # 我的收藏
│   │   ├── following.html          # 我的关注
│   │   ├── reading_history.html    # 阅读历史
│   │   └── subscriptions.html      # 订阅管理
│   └── admin/                      # 管理端页面模板
│       ├── base.html               # 管理端基础模板
│       ├── dashboard.html          # 管理仪表板
│       ├── login.html              # 管理员登录
│       ├── posts.html              # 文章管理
│       ├── post_form.html          # 文章编辑
│       ├── categories.html         # 分类管理
│       ├── comments.html           # 评论管理
│       ├── users.html              # 用户管理
│       ├── settings.html           # 系统设置
│       └── scheduler.html          # 调度器管理
├── static/                         # 静态资源文件
└── dataone/                        # 教学问答数据集
```

## 🚀 快速开始

### 1. 环境准备

确保已安装 Python 3.8+ 和 MySQL 5.7+

### 2. 克隆项目

```bash
git clone https://github.com/4no11/teaching_blog.git
cd teaching_blog
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 数据库配置

#### 创建数据库

```sql
CREATE DATABASE teaching_blog DEFAULT CHARACTER SET utf8mb4;
```

#### 配置数据库连接

编辑 `config.py` 或设置环境变量：

```bash
# 方法1: 环境变量
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=teaching_blog

# 方法2: 直接编辑 config.py
```

### 5. AI配置 (可选)

配置AI功能需要有效的API密钥：

```bash
# OpenAI API
export AI_API_KEY=sk-your-api-key
export AI_BASE_URL=https://api.openai.com/v1
export AI_MODEL=gpt-3.5-turbo

# 或使用兼容的API服务
export AI_API_KEY=your-api-key
export AI_BASE_URL=https://your-api-endpoint.com/v1
export AI_MODEL=your-model-name
```

### 6. 启动应用

```bash
python app.py
```

应用将在 <http://localhost:5000> 启动

### 7. 访问系统

- **前端**: <http://localhost:5000>
- **管理后台**: <http://localhost:5000/admin>
- **学习进度**: <http://localhost:5000/learning-progress>
- **智能体中心**: <http://localhost:5000/agent-center>

#### 默认管理员账号

- 用户名: `admin`
- 密码: `admin123`

> **注意**: 首次启动时会自动创建默认数据，包括管理员账号和基础分类

## 🌐 API接口

### AI服务接口

| 接口                            | 方法   | 描述     |
| ----------------------------- | ---- | ------ |
| `/api/ai/chat`                | POST | AI对话交互 |
| `/api/ai/chat/stream`         | POST | AI流式对话 |
| `/api/ai/summarize`           | POST | 文本摘要生成 |
| `/api/ai/improve`             | POST | 文本润色优化 |
| `/api/ai/generate-title`      | POST | 智能标题生成 |
| `/api/ai/suggest-tags`        | POST | 标签推荐   |
| `/api/ai/lesson-plan`         | POST | 教案生成   |
| `/api/ai/courseware-analysis` | POST | 课件分析   |
| `/api/ai/quiz`                | POST | 练习题生成  |

### 学习进度管理接口

| 接口                               | 方法   | 描述       |
| -------------------------------- | ---- | -------- |
| `/api/ai/ensure-user`            | POST | 确保用户存在   |
| `/api/ai/get-learning-progress`  | POST | 获取学习进度数据 |
| `/api/ai/update-progress`        | POST | 更新学习进度   |
| `/api/ai/get-content-nodes`      | GET  | 获取内容节点列表 |
| `/api/ai/create-content-node`    | POST | 创建内容节点   |
| `/api/ai/locate-difficult-nodes` | POST | 定位困难节点   |

### 一键备课接口

| 接口                              | 方法   | 描述      |
| ------------------------------- | ---- | ------- |
| `/api/ai/upload-material`       | POST | 上传教材文件  |
| `/api/ai/extract-knowledge`     | POST | 提取重难点知识 |
| `/api/ai/generate-quiz`         | POST | 智能出题    |
| `/api/ai/generate-review-cards` | POST | 生成复习卡片  |

### 客户端接口

| 接口                | 方法   | 描述     |
| ----------------- | ---- | ------ |
| `/api/posts`      | GET  | 获取文章列表 |
| `/api/posts/{id}` | GET  | 获取文章详情 |
| `/api/comments`   | POST | 发表评论   |
| `/api/favorites`  | POST | 收藏文章   |
| `/api/search`     | GET  | 搜索内容   |
| `/api/categories` | GET  | 获取分类列表 |

## 📝 文章类型系统

| 类型           | 说明   | 标识 | 示例            |
| ------------ | ---- | -- | ------------- |
| `note`       | 教学笔记 | 📝 | 课堂教学反思、教案设计心得 |
| `resource`   | 教育资源 | 📚 | 课件下载、试题库、教学工具 |
| `experience` | 教育心得 | 💡 | 教育理念分享、班级管理经验 |

> 三种类型已统一在"教学笔记"入口中管理和访问。

## 📂 默认分类

- 📝 教学笔记 - 教师日常教学记录
- 📚 教育资源 - 优质教学资料分享
- 💡 教育心得 - 教育理念和方法
- 💻 技术教程 - 教学技术相关
- 🌱 生活感悟 - 教师生活体会

## 🗄️ 数据库设计

### 核心表结构

```sql
-- 用户系统
users (id, username, email, is_admin, created_at)
posts (id, title, content, post_type, category_id, author_id)
categories (id, name, slug, description)
comments (id, content, post_id, user_id, parent_id)

-- 交互系统  
favorites (id, user_id, post_id, created_at)
reading_history (id, user_id, post_id, read_at, read_duration)
follows (id, user_id, author_id, created_at)

-- 内容系统
resources (id, name, file_path, post_id)
international_education (id, title, organization, country, source_url)

-- 学习进度系统
content_nodes (id, title, content, level, order_index, parent_id)
learning_progress (id, user_id, content_node_id, completed, comprehension_level, time_spent, last_accessed)
```

## ✨ 特色功能

### 🤖 AI智能助手

- **一键备课**: 上传教材文件，自动生成完整教案框架，支持对话式修改
- **智能出题**: 基于知识点自动生成选择题、填空题、简答题
- **课件优化**: AI分析课件，提出改进建议
- **内容润色**: 自动优化文章表达和逻辑
- **流式输出**: SSE技术实现实时响应体验

### 📈 学习进度管理

- **学习路径可视化**: 树形结构展示学习内容和进度
- **困难内容定位**: 自动识别理解程度低于60%的内容
- **多维度数据分析**: Chart.js 图表展示知识技能、认知能力、学习特点及趋势
- **个性化建议**: 基于学习数据提供节奏调整建议

### 🌐 自动内容聚合

- **国际教育资讯**: 实时获取 UNESCO、OECD 等权威组织信息
- **智能去重**: 自动过滤重复和低质量内容

### 🔧 开发特性

- **模块化设计**: 清晰的服务层和路由分离
- **扩展性强**: 易于添加新的AI功能和爬虫源
- **安全可靠**: 完整的用户认证和权限控制
- **响应式UI**: 现代化的渐变设计和动画效果

## 🤝 关联项目

### OpenMAIC (AI课堂)

- **地址**: [OpenMAIC](https://github.com/4no11/OpenMAIC)
- **描述**: 基于 Next.js 的沉浸式AI互动课堂，支持幻灯片、测验、交互式模拟、PBL项目制学习等多种教学形式
- **端口**: <http://localhost:3000> (或 3003)

两个项目可配合使用：teaching博客 提供内容管理和AI辅助功能，OpenMAIC 提供沉浸式AI课堂教学体验。

## 🛠️ 开发指南

### 本地开发

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. 安装开发依赖
pip install -r requirements.txt

# 3. 运行开发服务器
python app.py
```

### 代码结构

```
services/          # 业务逻辑层
├── ai_service.py     # AI功能实现 (含备课/出题/进度管理等)
├── international_crawler.py # 国际新闻爬虫
└── scheduler.py      # 定时任务

routes/            # 路由控制层
├── client.py        # 前端路由
└── admin.py         # 后台路由

models/            # 数据模型层
└── __init__.py     # SQLAlchemy模型定义 (含ContentNode, LearningProgress)

templates/         # 视图模板层
├── client/         # 前端页面
└── admin/          # 后台页面
```

### 添加新的AI功能

1. 在 `services/ai_service.py` 中添加新方法
2. 在 `routes/client.py` 中添加对应的API路由
3. 在前端模板中添加相应的UI组件

### 添加新的爬虫源

1. 在 `services/` 目录下创建新的爬虫文件
2. 在 `scheduler.py` 中注册定时任务
3. 在管理后台添加相应的配置界面

## 🔒 安全特性

- **用户认证**: 基于session的用户登录验证
- **权限控制**: 管理员和普通用户角色区分
- **数据验证**: 完整的输入验证和SQL注入防护
- **XSS防护**: Jinja2模板自动转义机制

## 📈 性能优化

- **数据库索引**: 关键字段建立索引提升查询效率
- **分页加载**: 文章列表采用分页减少页面负载
- **缓存机制**: 爬虫数据缓存避免重复请求
- **异步处理**: 定时任务异步执行不阻塞主进程
- **流式输出**: SSE技术实现AI响应实时展示

##

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)

## 📞 联系我们

- 项目地址: [GitHub Repository](https://github.com/4no11/teaching_blog)
- 问题反馈: [Issues](https://github.com/4no11/teaching_blog/issues)

***

⭐ 如果这个项目对您有帮助，请给我们一个Star！
