# 技术栈识别概览

> 由 stack-definitions.json 生成；修改识别元数据后运行 build。

保留 **53 个技术栈入口**，仅用于事实识别、版本报告与 UI/数据库工具路由。
个人库不提供技术栈编码规范，不默认下载官方通用规范，也不生成通用栈草案。
项目规范须从已有约束、真实代码和已确认架构中审核、沉淀；显式来源获取成功仍须项目核对。

命令：`python3 scripts/personal.py list-stacks`；加 `--format markdown` 阅读中文表格。

## 语言与运行时（15）

| ID / 名称 | 识别证据与缺口 | 条件工具路由 |
|---|---|---|
| `java` / Java | Maven 项目；Gradle Java 插件/工具链；官方 Java 镜像 | 基线工具 |
| `kotlin` / Kotlin | Kotlin JVM/Android/多平台插件或准确 Maven 依赖；Kotlin DSL 本身不命中 | 基线工具 |
| `javascript` / JavaScript | 实际 package.json | 基线工具 |
| `typescript` / TypeScript | 准确 npm typescript 依赖/对应锁文件 | 基线工具 |
| `python` / Python | requirements/pyproject 与 .python-version；官方 Python 镜像 | 基线工具 |
| `go` / Go | go.mod 的 go 声明；保持官方资料获取 | 基线工具 |
| `rust` / Rust | Cargo.toml 的 rust-version；保持官方资料获取 | 基线工具 |
| `csharp` / C# | csproj；语言版本只读 LangVersion，不从 TFM 推断 | 基线工具 |
| `dotnet` / .NET | csproj TargetFramework(s) 与 global.json SDK 分开记证据 | 基线工具 |
| `php` / PHP | composer.json 的 require.php 与锁文件 | 基线工具 |
| `swift` / Swift | Package.swift/Xcode；tools-version 和语言模式不当编译器版本 | 基线工具 |
| `dart` / Dart | pubspec environment.sdk；不当 Flutter SDK 版本 | 基线工具 |
| `node` / Node.js | engines.node、.nvmrc/.node-version 或官方 Node 镜像 | 基线工具 |
| `c` / C | CMake 显式 C/C 标准字段；其余需声明/源码确认 | 基线工具 |
| `cpp` / C++ | CMake 显式 CXX/C++ 标准字段；标准号不当编译器版本 | 基线工具 |

## Web 框架（8）

| ID / 名称 | 识别证据与缺口 | 条件工具路由 |
|---|---|---|
| `vue` / Vue | 准确 npm vue 依赖与对应锁文件 | UI 设计工具 |
| `react` / React | 准确 npm react 依赖与对应锁文件 | UI 设计工具 |
| `nextjs` / Next.js | 准确 npm next 依赖与对应锁文件 | UI 设计工具 |
| `nuxt` / Nuxt | 准确 npm nuxt 依赖与对应锁文件 | UI 设计工具 |
| `angular` / Angular | 准确 npm @angular/core 依赖与对应锁文件 | UI 设计工具 |
| `svelte` / Svelte | 准确 npm svelte 依赖与对应锁文件 | UI 设计工具 |
| `sveltekit` / SvelteKit | 准确 npm @sveltejs/kit 依赖与对应锁文件 | UI 设计工具 |
| `astro` / Astro | 准确 npm astro 依赖与对应锁文件 | UI 设计工具 |

## 后端框架（10）

| ID / 名称 | 识别证据与缺口 | 条件工具路由 |
|---|---|---|
| `spring` / Spring Boot | 准确 Boot parent/BOM/依赖/插件；核心 Spring 版本不当 Boot 版本 | 基线工具 |
| `django` / Django | 准确 Python 依赖；动态/间接配置需声明 | 基线工具 |
| `fastapi` / FastAPI | 准确 Python 依赖；动态/间接配置需声明 | 基线工具 |
| `flask` / Flask | 准确 Python 依赖；动态/间接配置需声明 | 基线工具 |
| `express` / Express | 准确 npm express 依赖 | 基线工具 |
| `nestjs` / NestJS | 准确 npm @nestjs/core 依赖 | 基线工具 |
| `fastify` / Fastify | 准确 npm fastify 依赖 | 基线工具 |
| `aspnet` / ASP.NET Core | Web SDK、Microsoft.AspNetCore.App FrameworkReference 或准确包 | 基线工具 |
| `laravel` / Laravel | Composer laravel/framework 与 composer.lock | 基线工具 |
| `gin` / Gin | go.mod 精确 github.com/gin-gonic/gin 依赖 | 基线工具 |

## 移动、桌面与小程序（6）

| ID / 名称 | 识别证据与缺口 | 条件工具路由 |
|---|---|---|
| `flutter` / Flutter | pubspec 的 flutter sdk 依赖；版本只取 environment.flutter/显式声明 | UI 设计工具 |
| `react-native` / React Native | 准确 react-native npm 依赖 | UI 设计工具 |
| `swiftui` / SwiftUI | 实际 .swift 的 import SwiftUI；SDK 可用性不当 Swift 版本 | UI 设计工具 |
| `electron` / Electron | 准确 electron npm 依赖 | UI 设计工具 |
| `tauri` / Tauri | 准确 tauri Cargo 或 @tauri-apps/api/cli npm 依赖；v1/v2 配置需核实 | UI 设计工具 |
| `wechat` / 微信小程序 | project.config.json compileType=miniprogram；不凭任意 app.json 猜测 | UI 设计工具 |

## 数据存储（6）

| ID / 名称 | 识别证据与缺口 | 条件工具路由 |
|---|---|---|
| `postgres` / PostgreSQL | 精确驱动依赖仅识别引擎；官方配置镜像 tag 可作目标证据；实际服务器待确认 | DBHub 候选，连接/运行待确认 |
| `mysql` / MySQL | 精确驱动依赖仅识别引擎；官方配置镜像 tag 可作目标证据；实际服务器待确认 | DBHub 候选，连接/运行待确认 |
| `sqlite` / SQLite | 精确驱动依赖仅识别引擎；官方配置镜像 tag 可作目标证据；实际服务器待确认 | DBHub 候选，连接/运行待确认 |
| `mariadb` / MariaDB | 精确驱动依赖仅识别引擎；官方配置镜像 tag 可作目标证据；实际服务器待确认 | DBHub 候选，连接/运行待确认 |
| `mongodb` / MongoDB | 精确驱动依赖仅识别引擎；官方配置镜像 tag 可作目标证据；实际服务器待确认 | 兼容数据库 provider 待选择 |
| `redis` / Redis | 精确驱动依赖仅识别引擎；官方配置镜像 tag 可作目标证据；实际服务器待确认 | 兼容数据库 provider 待选择 |

## ORM 与数据映射（4）

| ID / 名称 | 识别证据与缺口 | 条件工具路由 |
|---|---|---|
| `prisma` / Prisma | 准确 prisma/@prisma/client 等依赖；不据 ORM 猜引擎 | 基线工具 |
| `sqlalchemy` / SQLAlchemy | 准确 Python sqlalchemy 依赖 | 基线工具 |
| `mybatis` / MyBatis | 准确 MyBatis/MyBatis Spring/Boot Maven/Gradle 坐标 | 基线工具 |
| `hibernate` / Hibernate ORM | 准确 Hibernate core 坐标；JPA/Boot 本身不猜 provider | 基线工具 |

## 构建与容器（4）

| ID / 名称 | 识别证据与缺口 | 条件工具路由 |
|---|---|---|
| `maven` / Maven | 有效 pom.xml；版本需要 wrapper/显式确认 | 基线工具 |
| `gradle` / Gradle | build.gradle(.kts) 与 wrapper distributionUrl；不推断 Kotlin 应用 | 基线工具 |
| `vite` / Vite | 准确 npm vite 依赖 | 基线工具 |
| `docker` / Docker | Dockerfile/Compose；不执行 build/up/下载镜像 | 基线工具 |

## 事实边界

- 空白项目先讨论目标，再用 --stacks / --stack-versions 声明；声明不覆盖冲突的实际版本。
- 不执行依赖、构建脚本或容器。动态清单、未知版本、未解析锁文件与语言/SDK差异保留诊断。
- 数据库驱动版本不充当服务端版本；镜像只证明配置目标。
- 识别元数据不构成编码规则覆盖，也不证明业务、设备或真实客户端验收。
- 默认来源 profiles 为空。自选规范用 --stack-registry，记录 ref/hash/版本、离线及本地修改状态。
