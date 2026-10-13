---
name: 需求工作台
description: 需求管理示例的设计工具投影
colors:
  background: "#F4F6F8"
  surface: "#FFFFFF"
  text: "#182633"
  muted: "#5D6C7A"
  line: "#E2E8ED"
  primary: "#177E74"
  primaryText: "#116A60"
  primarySoft: "#E7F4F1"
  info: "#3264AB"
  infoSoft: "#EDF2FC"
  warning: "#865C16"
  warningSoft: "#FFF4D9"
  neutralSoft: "#EEF1F4"
  danger: "#B63838"
  dangerSoft: "#FCEDED"
  sidebar: "#162D35"
  sidebarText: "#E5F1F1"
  sidebarLine: "#35515B"
  sidebarMuted: "#C4D9DD"
typography:
  caption:
    fontFamily: "PingFang SC, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.6
  secondary:
    fontFamily: "PingFang SC, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.6
  body:
    fontFamily: "PingFang SC, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "PingFang SC, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.6
  control:
    fontFamily: "PingFang SC, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  section:
    fontFamily: "PingFang SC, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.6
  subheading:
    fontFamily: "PingFang SC, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.6
  brand:
    fontFamily: "PingFang SC, system-ui, sans-serif"
    fontSize: "19px"
    fontWeight: 400
    lineHeight: 1.6
  title:
    fontFamily: "PingFang SC, system-ui, sans-serif"
    fontSize: "26px"
    fontWeight: 400
    lineHeight: 1.6
rounded:
  field: "7px"
  control: "8px"
  surface: "10px"
  preview: "12px"
  dialog: "14px"
spacing:
  unit: "8px"
---

<!-- personal-ui-module-generated -->

权威来源：[design.json](design.json) 与 [PRD](docs/prd.zh-CN.md)，源版本 v1.2。本文件从设计源生成，不独立编辑。

## Overview

以快速完成任务为目标，沿用青绿色和深色侧栏，优先可扫描的信息和清晰操作。

## Colors

主色表示主要操作；推进状态使用 statusStyles 对应语义色，并保留文字。失败使用错误色，普通提示不抢占主操作。

## Typography

中文系统字体，标题、正文与辅助信息层级清晰。编号使用等宽数字特性，说明允许换行。

## Layout

桌面为侧栏、顶部导航和主内容；搜索与计数属于列表。760px 及以下列表改为条目，同一功能信息与操作保持一致。

## Shapes

沿用设计源中的圆角和间距尺度；同职责组件保持一致。

## Components

主操作、文本输入和需求列表引用设计源组件合同；提交互斥、首错聚焦、失败保留输入。

## Do's and Don'ts

沿用已有身份；不为了技能默认风格更换调色板；不增添无业务依据的图表或指标；不以检测通过代替真实行为验收。
