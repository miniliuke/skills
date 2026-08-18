# Architecture Skills Bundle（中文说明）

这是一套面向现代 Coding Agent 的**架构设计 + 开发 + Review + 长期治理** Skills 集合。

仓库现在同时包含两部分：

1. 你自己的架构工作流 Skills；
2. 自动从 [`mattpocock/skills`](https://github.com/mattpocock/skills) 同步的稳定 Skills。

目标是做到：

```text
只安装 miniliuke/skills
        ↓
自定义架构能力 + Matt 核心工程能力
        ↓
开箱即用
```

## 安装

查看全部 Skill：

```bash
npx skills add miniliuke/skills --list
```

安装完整集合：

```bash
npx skills add miniliuke/skills --skill '*'
```

Antigravity：

```bash
npx skills add miniliuke/skills --skill '*' --agent antigravity
```

Claude Code：

```bash
npx skills add miniliuke/skills --skill '*' --agent claude-code
```

完整安装后，不需要再单独安装 `mattpocock/skills`。

## 自定义架构 Skills

```text
architecture-workflow
new-project-architecture
new-module-architecture
architecture-change
architecture-review
architecture-health
```

它们负责把 Agent 原生 Plan Mode 和架构约束结合起来，而不是重新制造一套冗长的 planning 流水线。

这些 Skill 名称记录在 `.github/custom-skills.txt`。如果未来 Matt 上游出现同名 Skill，CI 会直接失败，而不会静默覆盖你的自定义版本。

## 自动同步的 Matt Skills

CI 会同步 Matt 上游中两个稳定分组下的**全部 Skill**：

```text
skills/engineering/*
skills/productivity/*
```

只同步包含 `SKILL.md` 的目录，并完整复制整个 Skill 目录，因此其中的：

```text
agents/
scripts/
参考 Markdown
其他 companion files
```

都会一起保留。

其中包括：

```text
domain-modeling
codebase-design
grilling
grill-with-docs
grill-me
to-spec
to-tickets
implement
tdd
code-review
improve-codebase-architecture
diagnosing-bugs
research
prototype
...
```

`deprecated`、`in-progress`、`misc` 不进入稳定 bundle，避免实验性、废弃或无关 Skill 自动污染安装集合。

## 推荐开发流程

### 普通需求 / Bug

```text
需求
 -> Agent Plan Mode
 -> Execute
 -> Tests
 -> Review
```

默认不额外增加流程。

### 新建项目

```text
需求沟通
 -> new-project-architecture
     -> domain-modeling
     -> codebase-design
     -> Agent Plan Mode
     -> ARCHITECTURE.md / 必要 ADR
 -> Execute
 -> architecture-review
```

### 新建模块 / 插件 / 子系统

```text
需求
 -> new-module-architecture
     -> 读取 CONTEXT / ADR / ARCHITECTURE
     -> 判断新模块是否真的有必要
     -> domain-modeling（概念变化时）
     -> codebase-design
     -> Agent Plan Mode
 -> Execute
 -> architecture-review
```

### 会改变现有架构的 Feature

```text
需求
 -> architecture-change
     -> Architecture Impact
     -> domain-modeling（语义变化时）
     -> codebase-design（seam/interface 变化时）
     -> compatibility / migration plan
     -> Agent Plan Mode
 -> Execute
 -> architecture-review
```

### 周期性架构优化

```text
若干 Feature / 一个 Milestone
 -> architecture-health
     -> improve-codebase-architecture
     -> 只选择高价值候选
 -> architecture-change
 -> Execute
 -> architecture-review
```

## `to-spec` / `to-tickets`

它们会随 bundle 一起安装，但不再是默认开发流程。

`to-spec` 更适合：

- 跨多个 session；
- 多 Agent / 多开发者协作；
- 核心 SPI / public contract 变化；
- 设计意图需要长期保存。

`to-tickets` 更适合：

- 多 Agent 并行；
- 明确 blocking dependency；
- 每个 ticket 作为独立 context boundary；
- 任务需要多次恢复继续执行。

普通单 Agent Feature 直接使用 Plan Mode 即可。

## 三种长期架构记忆

### `CONTEXT.md`

记录领域语言：

```text
“概念是什么？”
```

### `docs/adr/`

记录真正重要、未来可能重新争论的决策：

```text
“为什么当时这样决定？”
```

### `ARCHITECTURE.md`

记录当前有效结构合同：

```text
“现在模块如何划分，后续修改必须遵守什么？”
```

推荐记录：

```text
模块职责
允许依赖
禁止依赖
稳定 seam
扩展点
关键 runtime/data flow
架构 invariant
```

尽量写成明确规则，例如：

```text
Allowed: application -> dataset-api
Forbidden: dataset-api -> connector-mysql
Rule: application must not branch on connector type
```

而不是泛泛的“降低耦合”。

## 自动同步机制

`.github/workflows/sync-mattpocock-skills.yml`：

- 每天自动运行一次；
- 支持 GitHub Actions 手动运行；
- 拉取 Matt 上游 `main`；
- 不执行上游脚本，只复制文件；
- 同步全部稳定 engineering + productivity Skill；
- 上游删除的 vendored Skill 会在本仓库同步删除；
- 发现 symlink 时拒绝自动同步；
- 发现与自定义 Skill 同名时拒绝覆盖；
- 校验 `SKILL.md` 中的 `name` 与目录名一致；
- 在 `vendor/mattpocock/UPSTREAM_COMMIT` 记录精确上游 SHA；
- 在 `vendor/mattpocock/LICENSE` 保留上游 MIT License；
- 内容没有变化时不会产生空 commit。

## 许可

Matt Pocock 上游仓库使用 MIT License。第三方说明见：

```text
THIRD_PARTY_NOTICES.md
vendor/mattpocock/LICENSE
```

自定义架构 Skills 与自动镜像的 Matt 内容分开维护。
