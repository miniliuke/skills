# Architecture Skills（中文说明）

这套 Skills 面向现在具备较强 Plan Mode 的 coding agent。目标不是重复制造一套 `spec -> tickets -> implement` 流程，而是把 **架构设计和架构约束** 插到真正需要的位置。

## 推荐使用方式

### 普通需求 / Bug

```text
需求 -> Agent Plan Mode -> Execute -> Tests -> Review
```

默认不触发额外架构 Skill。

### 新建项目

```text
需求沟通
  -> /new-project-architecture
      -> domain-modeling（概念建模）
      -> codebase-design（模块/seam/interface）
      -> Agent Plan Mode
      -> ARCHITECTURE.md
  -> Execute
  -> /architecture-review
```

### 新建模块 / 插件 / 子系统

```text
需求
  -> /new-module-architecture
      -> 读取现有 CONTEXT / ADR / ARCHITECTURE
      -> 判断模块是否真的有必要
      -> 设计 module seam / interface
      -> Agent Plan Mode
  -> Execute
  -> /architecture-review
```

### 会改变现有架构的需求

```text
需求
  -> /architecture-change
      -> Architecture Impact
      -> domain-modeling（语义改变时）
      -> codebase-design（seam/interface 改变时）
      -> 兼容 / 迁移方案
      -> Agent Plan Mode
  -> Execute
  -> /architecture-review
```

### 周期性架构优化

```text
每若干 Feature / 一个 Milestone
  -> /architecture-health
      -> improve-codebase-architecture
      -> 只选择 1~3 个高价值候选
  -> /architecture-change
  -> Execute
  -> /architecture-review
```

## 三种长期架构记忆

### `CONTEXT.md`

只记录领域语言：

- Dataset 是什么
- Connector 是什么
- Subscription 与 Dataset 的关系
- Checkpoint 的 owner 是谁

不要记录实现细节。

### `docs/adr/`

只记录真正值得未来重新理解的决策，例如：

- 为什么 Dataset API 不暴露 JDBC
- 为什么 checkpoint 属于 subscription
- 为什么 core 不依赖 concrete connector

### `ARCHITECTURE.md`

记录当前有效的结构约束：

```text
模块职责
允许依赖
禁止依赖
稳定 seam
扩展点
关键 runtime/data flow
架构 invariant
```

它是后续 Agent 开发时最直接的架构合同。

## 与 mattpocock/skills 的关系

这套自定义 Skills 不复制 Matt 的完整 workflow，而是重点复用：

- `domain-modeling`：领域概念变化时
- `codebase-design`：module / interface / seam 设计时
- `code-review`：普通代码与 spec review
- `improve-codebase-architecture`：周期性寻找 deepening opportunities
- `tdd`：可选，针对稳定 seam 做行为测试

`to-spec` / `to-tickets` 不作为默认流程。

只有在以下情况下才建议使用：

- 多 Agent 并行；
- 一个任务跨多个 context/session；
- 核心 SPI / public contract 需要持久化；
- 需要 GitHub Issues 做长期任务边界；
- 设计意图几周后仍需要恢复。

## 安装

先安装 Matt 的核心 Skill：

```bash
npx skills add mattpocock/skills \
  --skill domain-modeling \
  --skill codebase-design \
  --skill code-review \
  --skill improve-codebase-architecture
```

安装本仓库：

```bash
npx skills add miniliuke/skills --skill '*'
```

如果只想装最常用的：

```bash
npx skills add miniliuke/skills \
  --skill architecture-workflow \
  --skill architecture-review
```
