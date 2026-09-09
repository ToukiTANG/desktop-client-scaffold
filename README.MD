# Desktop Client Scaffold

基于 **Python + PyWebView + Vue 3** 的 Windows 桌面应用基础脚手架。

该项目用于快速创建新的桌面业务应用，并集中维护与具体业务无关的基础能力，包括：

- PyWebView 桌面壳
- Python / JavaScript Bridge
- Vue 3 + TypeScript + Vite
- Element Plus
- SQLite
- Alembic 数据库迁移
- 应用配置持久化
- 日志
- Windows 7 SP1 兼容
- WebView2 Runtime 检查
- PyInstaller 打包
- ZIP 发布
- Inno Setup 安装包
- 统一项目身份配置
- 业务 API / Route / Menu 扩展点

Scaffold 不包含具体业务逻辑。

---

# 1. 技术栈

## Backend

- Python 3.8.10 x64
- uv
- PyWebView 4.2.2
- SQLite
- Alembic
- SQLAlchemy
- PyInstaller

## Frontend

- Vue 3
- TypeScript
- Vite
- Element Plus
- Vue Router

## Windows

目标运行环境：

- Windows 7 SP1 x64
- Windows 10
- Windows 11

Windows 7 使用：

- PyWebView 4.2.2
- WebView2 Runtime 109
- PyWebView Win7 compatibility patch

---

# 2. 项目结构

```text
desktop-client-scaffold/
├─ backend/
│  ├─ api/
│  │  └─ app_api.py
│  │
│  ├─ business/
│  │  ├─ __init__.py
│  │  └─ api_registry.py
│  │
│  ├─ core/
│  │  ├─ app_config.py
│  │  ├─ database.py
│  │  ├─ logging_config.py
│  │  ├─ paths.py
│  │  ├─ project_config.py
│  │  ├─ response.py
│  │  ├─ runtime_paths.py
│  │  ├─ schema.py
│  │  ├─ version.py
│  │  └─ webview2.py
│  │
│  ├─ alembic/
│  │  └─ versions/
│  │
│  ├─ services/
│  ├─ tools/
│  ├─ main.py
│  ├─ DesktopClient.spec
│  ├─ alembic.ini
│  └─ pyproject.toml
│
├─ frontend/
│  └─ src/
│     ├─ api/
│     │  ├─ app.ts
│     │  └─ bridge.ts
│     │
│     ├─ business/
│     │  ├─ menu.ts
│     │  └─ routes.ts
│     │
│     ├─ layouts/
│     │  └─ MainLayout.vue
│     │
│     ├─ router/
│     │  └─ index.ts
│     │
│     ├─ types/
│     └─ views/
│
├─ installer/
│  └─ DesktopClient.iss
│
├─ prerequisites/
├─ project.json
├─ build.ps1
└─ README.MD
```

---

# 3. Scaffold 与业务代码边界

这是本项目最重要的维护规则。

## Scaffold-owned

以下文件由 Scaffold 维护。

业务项目原则上不要修改这些文件：

```text
backend/api/app_api.py
backend/core/*
backend/main.py

frontend/src/api/bridge.ts
frontend/src/router/index.ts
frontend/src/layouts/MainLayout.vue

backend/DesktopClient.spec
installer/DesktopClient.iss
build.ps1
```

这些文件主要负责：

- 应用生命周期
- PyWebView Bridge
- API Dispatcher
- 路由框架
- 页面布局
- 配置基础设施
- 数据库基础设施
- 日志
- 打包
- 安装
- Windows 兼容

Scaffold 后续升级时，这些文件会通过 Git 合并进入业务项目。

## Business-owned

业务项目主要修改或新增以下内容：

```text
backend/business/api_registry.py

frontend/src/business/routes.ts
frontend/src/business/menu.ts

backend/api/<business_api>.py
backend/services/<business_service>.py

frontend/src/api/<business_api>.ts
frontend/src/views/<business_view>/
frontend/src/types/<business_type>.ts
frontend/src/stores/<business_store>.ts
```

数据库业务表和 Alembic migration 也属于业务项目：

```text
backend/alembic/versions/*
```

---

# 4. 项目身份配置

所有产品身份信息统一配置在：

```text
project.json
```

默认配置：

```json
{
  "app_name": "Desktop Client",
  "app_id": "F8A49F6C-8A19-4A0E-9D29-4C8F45A9583E",
  "internal_name": "DesktopClient",
  "executable_name": "DesktopClient",
  "data_dir_name": "DesktopClient",
  "installer_name": "DesktopClientSetup"
}
```

字段说明：

| 字段              | 作用                            |
|-------------------|---------------------------------|
| `app_name`        | 用户可见的软件名称              |
| `app_id`          | Inno Setup 产品唯一 ID          |
| `internal_name`   | Windows EXE 内部名称            |
| `executable_name` | EXE 名称和 PyInstaller 输出目录 |
| `data_dir_name`   | `%LOCALAPPDATA%` 下的数据目录   |
| `installer_name`  | Setup 安装包名称                |

创建新业务项目时，这些字段必须根据产品修改。

其中 `app_id` 必须为每个独立产品生成新的 GUID。

PowerShell：

```powershell
[guid]::NewGuid().ToString("D").ToUpper()
```

例如：

```json
{
  "app_name": "公寓成本核算",
  "app_id": "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE",
  "internal_name": "ApartmentCostAccounting",
  "executable_name": "ApartmentCostAccounting",
  "data_dir_name": "ApartmentCostAccounting",
  "installer_name": "ApartmentCostAccountingSetup"
}
```

不要让两个独立产品共用同一个：

```text
app_id
data_dir_name
```

否则可能出现安装覆盖或本地数据互相污染。

---

# 5. 创建新的业务项目

推荐从 Scaffold 仓库直接 clone，保留共同 Git 历史。

例如：

```powershell
git clone <scaffold-repository> my-business-client
```

然后进入新项目：

```powershell
cd my-business-client
```

业务项目应配置自己的远程仓库为 `origin`，同时保留 Scaffold 作为上游 remote。

例如：

```powershell
git remote rename origin scaffold
```

然后添加业务仓库：

```powershell
git remote add origin <business-repository>
```

最终关系：

```text
origin
→ 当前业务项目

scaffold
→ desktop-client-scaffold
```

业务开发从 Scaffold 当前稳定版本开始。

---

# 6. Backend 业务 API

PyWebView 4.2.2 不使用嵌套 JS API。

所有业务 API 通过统一 Dispatcher：

```text
AppApi.invoke()
```

调用。

业务模块统一注册在：

```text
backend/business/api_registry.py
```

默认：

```python
from __future__ import annotations

from typing import Any


def create_business_apis() -> dict[str, Any]:
    return {}
```

例如新增：

```python
from api.material_price_api import MaterialPriceApi


def create_business_apis():
    return {
        "material_price": MaterialPriceApi(),
    }
```

前端调用：

```ts
callApi(
  'material_price',
  'get_material_prices',
)
```

业务 API 中：

- 公共方法允许前端调用；
- 私有辅助方法必须以 `_` 开头。

例如：

```python
class MaterialPriceApi:
    def get_material_prices(self):
        ...

    def _convert_row(self):
        ...
```

`_convert_row()` 不允许通过 Dispatcher 调用。

---

# 7. Frontend 业务路由

业务路由统一配置：

```text
frontend/src/business/routes.ts
```

默认：

```ts
import type { RouteRecordRaw } from 'vue-router'

export const businessRoutes: RouteRecordRaw[] = []
```

例如：

```ts
import type { RouteRecordRaw } from 'vue-router'

export const businessRoutes: RouteRecordRaw[] = [
  {
    path: 'material-price',
    name: 'material-price',
    component: () =>
      import('@/views/MaterialPrice/MaterialPriceView.vue'),
  },
]
```

业务路由会自动作为 `MainLayout` 的 child route 注册。

因此 child path 不需要 `/`：

```text
material-price
```

最终访问地址仍然是：

```text
/material-price
```

业务项目不要为了增加页面而修改：

```text
frontend/src/router/index.ts
```

---

# 8. Frontend 业务菜单

左侧业务菜单统一配置：

```text
frontend/src/business/menu.ts
```

默认：

```ts
import type { Component } from 'vue'

export interface BusinessMenuItem {
  index: string
  label: string
  icon?: Component
}

export const businessMenuItems: BusinessMenuItem[] = []
```

例如：

```ts
import type { Component } from 'vue'
import { Coin } from '@element-plus/icons-vue'

export interface BusinessMenuItem {
  index: string
  label: string
  icon?: Component
}

export const businessMenuItems: BusinessMenuItem[] = [
  {
    index: '/material-price',
    label: '材料价格',
    icon: Coin,
  },
]
```

业务项目不要为了增加菜单而修改：

```text
frontend/src/layouts/MainLayout.vue
```

---

# 9. 应用配置

基础配置文件：

```text
config.json
```

开发环境：

```text
backend/data/config.json
```

打包环境：

```text
%LOCALAPPDATA%\<data_dir_name>\data\config.json
```

Scaffold 只负责：

- JSON 读取
- JSON 保存
- 配置路径
- 基础异常处理

Scaffold 不规定具体配置字段。

例如业务项目可以保存：

```json
{
  "workshop": "一车间",
  "apartment": "一公寓"
}
```

另一个业务也可以保存：

```json
{
  "server_url": "https://example.com",
  "department": "1001"
}
```

业务字段定义和校验应由具体业务实现。

---

# 10. 数据库

数据库默认使用 SQLite。

开发环境：

```text
backend/data/desktop.db
```

打包环境：

```text
%LOCALAPPDATA%\<data_dir_name>\data\desktop.db
```

数据库初始化时自动执行：

```text
alembic upgrade head
```

Scaffold 本身不包含任何业务表。

```text
backend/alembic/versions/
```

默认为空。

业务项目创建自己的数据库结构后生成 migration。

Scaffold 当前提供：

```text
SQLite connection
transaction
Alembic
SQLAlchemy MetaData
```

不强制业务必须使用 SQLAlchemy ORM。

---

# 11. 前置依赖

在进行正式构建前，需要准备以下运行环境和工具。

#### 1、[Win7 运行环境下载](https://www.catalog.update.microsoft.com/Search.aspx?q=Microsoft+Edge-WebView2+Runtime+109+x64)

用于 Windows 7 SP1 x64 环境下的 WebView2 Runtime 109。

下载后，将对应的安装文件放入项目根目录：

```text
prerequisites/
```

当前构建脚本默认查找：

```text
prerequisites/MicrosoftEdge_X64_109.0.1518.140.exe
```

该二进制文件不会提交到 Git，需要在本地自行准备。

#### 2、[Inno Setup 6 下载](https://github.com/jrsoftware/issrc/releases/download/is-6_7_3/innosetup-6.7.3.exe)

用于生成 Windows Setup 安装包。

默认安装即可。

当前构建脚本默认查找：

```text
C:\Program Files (x86)\Inno Setup 6\ISCC.exe
```

如果安装在其他路径，需要同步修改：

```text
build.ps1
```

中的：

```powershell
$InnoSetupCompiler
```

---

# 12. 开发环境

## Python

Windows 7 构建要求：

```text
Official CPython 3.8.10 x64
```

不要使用 uv 自动下载的 Python runtime 构建 Win7 版本。

项目仍然使用 uv 管理依赖。

Backend：

```powershell
cd backend; uv sync
```

## Frontend

安装依赖：

```powershell
cd frontend; npm install
```

启动 Vite：

```powershell
cd frontend; npm run dev
```

开发模式启动 Desktop Client：

```powershell
cd backend; uv run python main.py --dev
```

---

# 13. Windows 7 compatibility

当前 Win7 compatibility baseline：

```text
Windows 7 SP1 x64
Python 3.8.10 x64
PyWebView 4.2.2
WebView2 Runtime 109
```

PyWebView 4.2.2 在 Windows 7 上存在：

```text
shcore.GetScaleFactorForDevice
```

兼容问题。

构建前：

```text
backend/tools/patch_pywebview_win7.py
```

会自动应用兼容补丁。

该补丁只针对当前指定版本的 PyWebView。

不要在没有重新验证 Win7 的情况下直接升级 PyWebView。

---

# 14. WebView2 Runtime

Win7 使用 WebView2 Runtime 109。

安装文件：

```text
prerequisites/MicrosoftEdge_X64_109.0.1518.140.exe
```

该二进制文件不提交 Git。

`.gitignore` 会忽略：

```text
prerequisites/*.exe
```

构建正式安装包前，需要自行将对应 Runtime 安装文件放入：

```text
prerequisites/
```

Windows 10 / 11 不强制安装 Runtime 109，使用系统当前 WebView2 Runtime。

---

# 15. 构建

完整构建：

```powershell
.\build.ps1
```

构建流程：

```text
0. 校验 Python 3.8.10 x64
1. 应用 PyWebView Win7 compatibility patch
2. 构建 Vue frontend
3. 读取应用版本
4. PyInstaller
5. 准备 release
6. 生成 ZIP
7. Inno Setup
8. 完成
```

版本号来自：

```text
backend/pyproject.toml
```

产品身份来自：

```text
project.json
```

最终产物位于：

```text
release/
```

例如：

```text
release/
├─ DesktopClient-0.1.0/
├─ DesktopClient-0.1.0.zip
└─ DesktopClientSetup-0.1.0.exe
```

---

# 16. ZIP 与 Setup

ZIP：

```text
DesktopClient-<version>.zip
```

主要用于：

- 开发测试
- 内部测试
- 免安装运行

Setup：

```text
DesktopClientSetup-<version>.exe
```

推荐用于正式用户。

Setup 提供：

- 安装目录
- 开始菜单
- 桌面快捷方式
- 卸载
- 升级安装
- Win7 WebView2 prerequisite 检查

---

# 17. Scaffold 更新同步到业务项目

基础设施修改必须优先进入：

```text
desktop-client-scaffold
```

例如：

```text
Win7 compatibility
build.ps1
PyInstaller
Inno Setup
logging
paths
database infrastructure
Bridge
Router infrastructure
MainLayout infrastructure
```

完成并验证后，再同步到各业务项目。

业务项目执行：

```powershell
git fetch scaffold
```

然后：

```powershell
git merge scaffold/main
```

建议 Scaffold 使用 Git Tag 发布稳定版本，例如：

```text
v0.1.0
v0.2.0
v0.3.0
```

业务项目可以明确选择升级版本，而不是始终追踪最新 commit。

---

# 18. Merge 冲突控制

为了让 Scaffold 更新能够稳定合并到业务项目：

业务代码应尽量只修改 Business-owned 文件。

不要因为新增业务功能直接修改：

```text
backend/api/app_api.py
frontend/src/router/index.ts
frontend/src/layouts/MainLayout.vue
backend/main.py
backend/core/*
build.ps1
DesktopClient.spec
DesktopClient.iss
```

如果业务开发过程中发现需要修改这些文件，应先判断：

> 这是业务能力，还是所有 Desktop Client 都可能需要的通用能力？

如果属于通用能力：

```text
业务发现需求
    ↓
回 Scaffold 实现
    ↓
Scaffold 测试
    ↓
发布新版本
    ↓
业务项目 merge
```

不要只在单个业务仓库里长期维护基础设施补丁。

---

# 19. 新业务项目 Checklist

创建新项目后至少完成：

```text
[ ] 修改 project.json
[ ] 为 app_id 生成新的 GUID
[ ] 修改 app_name
[ ] 修改 internal_name
[ ] 修改 executable_name
[ ] 修改 data_dir_name
[ ] 修改 installer_name
[ ] 根据需要替换 app.ico
[ ] 注册 backend business API
[ ] 注册 frontend business routes
[ ] 注册 frontend business menu
[ ] 创建业务 Service / View / Type
[ ] 创建业务数据库 migration
[ ] 准备 Win7 WebView2 prerequisite
[ ] 开发环境测试
[ ] PyInstaller 测试
[ ] Setup 安装测试
[ ] Win7 / Win10 / Win11 按目标环境测试
```

---

# 20. 基本原则

Scaffold 的核心目标不是减少第一次写代码的数量，而是：

> 让多个桌面业务项目共享同一套经过验证的基础设施，并能够持续从 Scaffold 获得升级。

因此维护时优先保证：

```text
基础设施与业务逻辑分离
项目身份集中配置
扩展点明确
Git 历史连续
Scaffold 可独立运行
业务项目可持续合并 Scaffold 更新
```
