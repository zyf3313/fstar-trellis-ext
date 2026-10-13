# 技术栈覆盖总览

> 由 stack-definitions.json、catalog.json 和官方来源清单生成；修改源后运行 build。

当前提供 **53 个技术栈入口**。这里列出整个规范库，不是三个获取验收样例的范围。

COMMON 是不绑定发布版本的工程基线：覆盖资源、模块、数据/交互和验证机制；不能当作所有版本 API 保证。
版本专用规则只匹配登记的 major；React、Go、Rust保留固定提交/摘要的官方获取链路，离线需要已验证缓存。
每个项目仍需 AI 阅读真实源码与官方对应版本，补项目规范并运行实际检查。规则/识别/复制消费通过不等于 53 种业务运行已验收。

命令：`python3 scripts/personal.py list-stacks`（分组 JSON）；加 `--format markdown` 阅读中文表格。

## 语言与运行时（15）

| ID / 名称 | 具体覆盖 | 来源和版本边界 | 自动证据 / 缺口 |
|---|---|---|---|
| `java` / Java | JDK/编译目标、模块依赖和测试入口 | [stacks.java](specs/stacks/java/index.md)：major 8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26 | Maven 项目；Gradle Java 插件/工具链；官方 Java 镜像 |
| `kotlin` / Kotlin | 空值互操作、协程取消和编译器约束 | [stacks.kotlin](specs/stacks/kotlin/index.md)：COMMON | Kotlin JVM/Android/多平台插件或准确 Maven 依赖；Kotlin DSL 本身不命中 |
| `javascript` / JavaScript | 模块环境、异步错误和资源归属 | [stacks.javascript](specs/stacks/javascript/index.md)：COMMON<br>[official.javascript.common](specs/stacks/javascript/adaptation.md)：官方获取 COMMON | 实际 package.json |
| `typescript` / TypeScript | 真实 tsconfig、外部解码与类型检查 | [stacks.typescript](specs/stacks/typescript/index.md)：major 5,6<br>[official.typescript.common](specs/stacks/typescript/adaptation.md)：官方获取 major 5,6 | 准确 npm typescript 依赖/对应锁文件 |
| `python` / Python | 解释器范围、环境归属和 CLI 契约 | [stacks.python](specs/stacks/python/index.md)：major 3<br>[official.python.common](specs/stacks/python/adaptation.md)：官方获取 major 3 | requirements/pyproject 与 .python-version；官方 Python 镜像 |
| `go` / Go | 包边界、goroutine 取消和测试 | [official.go.common](specs/stacks/go/adaptation.md)：官方获取 major 1 | go.mod 的 go 声明；保持官方资料获取 |
| `rust` / Rust | 所有权、错误类型和 Cargo 工作区 | [official.rust.common](specs/stacks/rust/adaptation.md)：官方获取 major 1 | Cargo.toml 的 rust-version；保持官方资料获取 |
| `csharp` / C# | 可空引用、异步取消和资源释放 | [stacks.csharp](specs/stacks/csharp/index.md)：COMMON | csproj；语言版本只读 LangVersion，不从 TFM 推断 |
| `dotnet` / .NET | SDK/TFM、依赖注入生命周期和发布目标 | [stacks.dotnet](specs/stacks/dotnet/index.md)：COMMON | csproj TargetFramework(s) 与 global.json SDK 分开记证据 |
| `php` / PHP | 类型/错误、Composer 自动加载和请求资源 | [stacks.php](specs/stacks/php/index.md)：COMMON | composer.json 的 require.php 与锁文件 |
| `swift` / Swift | 值/引用语义、并发隔离和可选值 | [stacks.swift](specs/stacks/swift/index.md)：COMMON | Package.swift/Xcode；tools-version 和语言模式不当编译器版本 |
| `dart` / Dart | sound null safety、异步流和 isolate 边界 | [stacks.dart](specs/stacks/dart/index.md)：COMMON | pubspec environment.sdk；不当 Flutter SDK 版本 |
| `node` / Node.js | 进程生命周期、模块格式和非阻塞 IO | [stacks.node](specs/stacks/node/index.md)：COMMON | engines.node、.nvmrc/.node-version 或官方 Node 镜像 |
| `c` / C | 缓冲区长度、所有权和编译器检查 | [stacks.c](specs/stacks/c/index.md)：COMMON | CMake 显式 C/C 标准字段；其余需声明/源码确认 |
| `cpp` / C++ | RAII、值语义和构建目标契约 | [stacks.cpp](specs/stacks/cpp/index.md)：COMMON | CMake 显式 CXX/C++ 标准字段；标准号不当编译器版本 |

## Web 框架（8）

| ID / 名称 | 具体覆盖 | 来源和版本边界 | 自动证据 / 缺口 |
|---|---|---|---|
| `vue` / Vue | Vue 3 生命周期/响应式；Vue 2 独立兼容规则 | [stacks.vue](specs/stacks/vue/index.md)：major 3<br>[stacks.vue.legacy-v2](specs/stacks/vue/legacy-v2.md)：major 2<br>[official.vue.common](specs/stacks/vue/adaptation.md)：官方获取 major 3 | 准确 npm vue 依赖与对应锁文件 |
| `react` / React | 组件/状态/Effect 边界；官方获取后项目核对 | [official.react.common](specs/stacks/react/adaptation.md)：官方获取 major 18,19 | 准确 npm react 依赖与对应锁文件 |
| `nextjs` / Next.js | 实际 App/Pages Router、服务端边界与缓存 | [stacks.nextjs](specs/stacks/nextjs/index.md)：COMMON | 准确 npm next 依赖与对应锁文件 |
| `nuxt` / Nuxt | 服务端请求隔离、路由和部署 target | [stacks.nuxt](specs/stacks/nuxt/index.md)：COMMON | 准确 npm nuxt 依赖与对应锁文件 |
| `angular` / Angular | workspace target、依赖注入和订阅释放 | [stacks.angular](specs/stacks/angular/index.md)：COMMON | 准确 npm @angular/core 依赖与对应锁文件 |
| `svelte` / Svelte | 响应式模式、组件销毁和编译检查 | [stacks.svelte](specs/stacks/svelte/index.md)：COMMON | 准确 npm svelte 依赖与对应锁文件 |
| `sveltekit` / SvelteKit | 路由/load/action、服务端数据与 adapter | [stacks.sveltekit](specs/stacks/sveltekit/index.md)：COMMON | 准确 npm @sveltejs/kit 依赖与对应锁文件 |
| `astro` / Astro | 岛屿 hydration、内容边界和输出模式 | [stacks.astro](specs/stacks/astro/index.md)：COMMON | 准确 npm astro 依赖与对应锁文件 |

## 后端框架（10）

| ID / 名称 | 具体覆盖 | 来源和版本边界 | 自动证据 / 缺口 |
|---|---|---|---|
| `spring` / Spring Boot | Boot 3/4 与 Boot 2 独立规则；bean/事务边界 | [stacks.spring](specs/stacks/spring/index.md)：major 3,4<br>[stacks.spring.legacy-v2](specs/stacks/spring/legacy-v2.md)：major 2 | 准确 Boot parent/BOM/依赖/插件；核心 Spring 版本不当 Boot 版本 |
| `django` / Django | settings、ORM 事务、迁移与部署职责 | [stacks.django](specs/stacks/django/index.md)：COMMON | 准确 Python 依赖；动态/间接配置需声明 |
| `fastapi` / FastAPI | Pydantic/路由契约、lifespan 和 async IO | [stacks.fastapi](specs/stacks/fastapi/index.md)：COMMON | 准确 Python 依赖；动态/间接配置需声明 |
| `flask` / Flask | app factory、请求上下文和 WSGI 部署 | [stacks.flask](specs/stacks/flask/index.md)：COMMON | 准确 Python 依赖；动态/间接配置需声明 |
| `express` / Express | 中间件顺序、异步错误和服务关闭 | [stacks.express](specs/stacks/express/index.md)：COMMON | 准确 npm express 依赖 |
| `nestjs` / NestJS | module/provider 生命周期和传输边界 | [stacks.nestjs](specs/stacks/nestjs/index.md)：COMMON | 准确 npm @nestjs/core 依赖 |
| `fastify` / Fastify | 插件封装、schema、hook 与关闭 | [stacks.fastify](specs/stacks/fastify/index.md)：COMMON | 准确 npm fastify 依赖 |
| `aspnet` / ASP.NET Core | middleware、请求作用域、配置和宿主生命周期 | [stacks.aspnet](specs/stacks/aspnet/index.md)：COMMON | Web SDK、Microsoft.AspNetCore.App FrameworkReference 或准确包 |
| `laravel` / Laravel | 服务层、Eloquent、队列提交和迁移 | [stacks.laravel](specs/stacks/laravel/index.md)：COMMON | Composer laravel/framework 与 composer.lock |
| `gin` / Gin | 路由/绑定/代理、goroutine 与 HTTP 服务边界 | [stacks.gin](specs/stacks/gin/index.md)：COMMON | go.mod 精确 github.com/gin-gonic/gin 依赖 |

## 移动、桌面与小程序（6）

| ID / 名称 | 具体覆盖 | 来源和版本边界 | 自动证据 / 缺口 |
|---|---|---|---|
| `flutter` / Flutter | widget 生命周期、路由、平台插件与测试 | [stacks.flutter](specs/stacks/flutter/index.md)：COMMON | pubspec 的 flutter sdk 依赖；版本只取 environment.flutter/显式声明 |
| `react-native` / React Native | JS/native 边界、导航、平台构建和设备验证 | [stacks.react-native](specs/stacks/react-native/index.md)：COMMON | 准确 react-native npm 依赖 |
| `swiftui` / SwiftUI | 状态归属、视图 identity、task 取消和 actor 隔离 | [stacks.swiftui](specs/stacks/swiftui/index.md)：COMMON | 实际 .swift 的 import SwiftUI；SDK 可用性不当 Swift 版本 |
| `electron` / Electron | main/preload/renderer、IPC 校验和窗口资源 | [stacks.electron](specs/stacks/electron/index.md)：COMMON | 准确 electron npm 依赖 |
| `tauri` / Tauri | Rust/前端命令边界、capabilities 和打包 | [stacks.tauri](specs/stacks/tauri/index.md)：COMMON | 准确 tauri Cargo 或 @tauri-apps/api/cli npm 依赖；v1/v2 配置需核实 |
| `wechat` / 微信小程序 | 页面/session 生命周期、请求状态和平台约束 | [stacks.wechat](specs/stacks/wechat/index.md)：COMMON | project.config.json compileType=miniprogram；不凭任意 app.json 猜测 |

## 数据存储（6）

| ID / 名称 | 具体覆盖 | 来源和版本边界 | 自动证据 / 缺口 |
|---|---|---|---|
| `postgres` / PostgreSQL | schema/search_path、隔离、索引与恢复 | [stacks.postgres](specs/stacks/postgres/index.md)：COMMON | 精确驱动依赖仅识别引擎；官方配置镜像 tag 可作目标证据；实际服务器待确认；DBHub 候选，连接/运行待确认 |
| `mysql` / MySQL | SQL mode、collation、隐式提交与读回 | [stacks.mysql](specs/stacks/mysql/index.md)：COMMON | 精确驱动依赖仅识别引擎；官方配置镜像 tag 可作目标证据；实际服务器待确认；DBHub 候选，连接/运行待确认 |
| `sqlite` / SQLite | 文件归属、外键、并发/journal 和迁移 | [stacks.sqlite](specs/stacks/sqlite/index.md)：COMMON | 精确驱动依赖仅识别引擎；官方配置镜像 tag 可作目标证据；实际服务器待确认；DBHub 候选，连接/运行待确认 |
| `mariadb` / MariaDB | 引擎身份、SQL mode、锁与迁移兼容 | [stacks.mariadb](specs/stacks/mariadb/index.md)：COMMON | 精确驱动依赖仅识别引擎；官方配置镜像 tag 可作目标证据；实际服务器待确认；DBHub 候选，连接/运行待确认 |
| `mongodb` / MongoDB | document/schema、索引、session 和一致性 | [stacks.mongodb](specs/stacks/mongodb/index.md)：COMMON | 精确驱动依赖仅识别引擎；官方配置镜像 tag 可作目标证据；实际服务器待确认；兼容 provider 待选择，不默认 DBHub |
| `redis` / Redis | key/TTL、原子更新、缓存/持久化边界 | [stacks.redis](specs/stacks/redis/index.md)：COMMON | 精确驱动依赖仅识别引擎；官方配置镜像 tag 可作目标证据；实际服务器待确认；兼容 provider 待选择，不默认 DBHub |

## ORM 与数据映射（4）

| ID / 名称 | 具体覆盖 | 来源和版本边界 | 自动证据 / 缺口 |
|---|---|---|---|
| `prisma` / Prisma | schema/client 生成、事务边界和迁移漂移 | [stacks.prisma](specs/stacks/prisma/index.md)：COMMON | 准确 prisma/@prisma/client 等依赖；不据 ORM 猜引擎 |
| `sqlalchemy` / SQLAlchemy | Session 单元工作、async 归属和事务释放 | [stacks.sqlalchemy](specs/stacks/sqlalchemy/index.md)：COMMON | 准确 Python sqlalchemy 依赖 |
| `mybatis` / MyBatis | mapper/XML 参数、事务与批处理 | [stacks.mybatis](specs/stacks/mybatis/index.md)：COMMON | 准确 MyBatis/MyBatis Spring/Boot Maven/Gradle 坐标 |
| `hibernate` / Hibernate ORM | 持久化上下文、懒加载、flush 和乐观锁 | [stacks.hibernate](specs/stacks/hibernate/index.md)：COMMON | 准确 Hibernate core 坐标；JPA/Boot 本身不猜 provider |

## 构建与容器（4）

| ID / 名称 | 具体覆盖 | 来源和版本边界 | 自动证据 / 缺口 |
|---|---|---|---|
| `maven` / Maven | reactor、plugin/BOM 和干净验证 | [stacks.maven](specs/stacks/maven/index.md)：COMMON | 有效 pom.xml；版本需要 wrapper/显式确认 |
| `gradle` / Gradle | wrapper/toolchain、任务图和多项目边界 | [stacks.gradle](specs/stacks/gradle/index.md)：COMMON | build.gradle(.kts) 与 wrapper distributionUrl；不推断 Kotlin 应用 |
| `vite` / Vite | 开发/构建差异、env 和插件/产物 | [stacks.vite](specs/stacks/vite/index.md)：COMMON | 准确 npm vite 依赖 |
| `docker` / Docker | 镜像/构建上下文、权限、健康与数据卷 | [stacks.docker](specs/stacks/docker/index.md)：COMMON | Dockerfile/Compose；不执行 build/up/下载镜像 |

## 配置、边界与扩展

- 识别定义使用 schema_version=1、groups/stacks、精确依赖 markers（kind/names/prefixes/version）及能力/provider 元数据。原生 index.json 保持独立。
- 空白或动态配置项目可用 --stacks / --stack-versions 声明；原始配置与版本证据保留，冲突不覆盖实际事实。
- 读取有字节上限，跳过 symlink/依赖/缓存目录和登记预览；不执行依赖、构建脚本、Docker 或下载资料中的命令。
- packageManager/对应锁文件决定 npm/pnpm/yarn/bun 命令；没有配置时 npm 仅为待确认示例。pnpm 常见 importer、Yarn descriptor 与 npm 锁解析有范围，未支持格式保留声明/诊断。
- Python 3.9/3.10 没有 tomli 时只支持静态单行 TOML；完整结构请使用 Python 3.11+ 或项目已有 tomli。Gradle alias/继承、复杂 YAML、CMake 动态语言等需显式声明/源码复核。
- Java 1.8/VERSION_1_8 归一化为 8 并保留原值；Kotlin DSL 不等于 Kotlin 应用；C# LangVersion 与 .NET TFM/SDK 分开。
- Dart 与 Flutter SDK、Swift 编译器与 tools-version/语言模式/SwiftUI SDK 分开；数据库驱动版本不当服务端版本，配置镜像只证明目标声明。
- 新增栈：维护定义与具体规则/catalog 或官方 profile/适配指南，保留来源/覆盖/版本边界，再 build/validate 与独立消费。安装器复制这些元数据与 helper，保护本地改动。

本轮保留的缺口：所有栈真实业务/设备/发布验证、未声明版本、动态/不支持清单、非 SQL provider，以及已有父任务的远程发布、客户端/模型/外部探索接入。
