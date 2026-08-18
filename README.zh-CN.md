# Architecture Skills Bundle（中文说明）

这是一套面向现代 Coding Agent 的**架构设计 + 开发 + Review + 文档维护 + 长期治理** Skills 集合。

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
architecture-documentation
new-project-architecture
new-module-architecture
architecture-change
architecture-review
architecture-health
```

其中：

- `architecture-workflow`：根据任务类型选择最轻量的架构流程；
- `architecture-documentation`：为已有项目建立、增量更新或校准架构文档；
- `new-project-architecture`：新建项目/大型子系统；
- `new-module-architecture`：新建模块、插件、子系统；
- `architecture-change`：架构变化前做影响分析和迁移设计；
- `architecture-review`：对实现结果做独立架构审查；
- `architecture-health`：周期性全局架构治理。

这些 Skill 名称记录在 `.github/custom-skills.txt`。如果未来 Matt 上游出现同名 Skill，CI 会直接失败，而不会静默覆盖你的自定义版本。

## `architecture-documentation`

这个 Skill 专门维护“**当前真实架构**”，不是架构优化器。

它会根据项目状态自动选择三种模式：

```text
Bootstrap
  已有项目没有权威架构文档
  -> 逆向代码建立架构文档

Update
  已验证的结构性修改已经落地
  -> 只更新变旧的章节/图

Reconcile
  怀疑架构文档与代码已经漂移
  -> 对照代码和文档进行校准
```

最重要的规则：

```text
ARCHITECTURE.md 描述现在已经存在并验证过的架构。
计划中的目标架构不能提前写成当前架构。
```

文档会尽量区分：

```text
Observed architecture
  当前代码实际是什么

Architectural invariants
  项目希望长期保持的结构约束

Known deviations
  当前代码已经违反约束的地方

Architectural debt
  不一定违规，但值得后续优化的结构问题
```

已有文档优先做局部修改，不默认整篇重写，也不会为了让文档“看起来合理”而掩盖代码中的架构偏差。

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

### 已有项目首次建立架构文档

```text
Existing codebase
 -> architecture-documentation (Bootstrap)
     -> 扫描模块/依赖/公共 seam/runtime/data flow
     -> 读取 CONTEXT / ADR / 已有设计文档
     -> 如实记录当前架构
     -> ARCHITECTURE.md（或项目已有权威架构文档）
```

如果只是梳理架构，不会顺手重构项目。

### 已有架构文档需要校准

```text
Architecture docs + current code
 -> architecture-documentation (Reconcile)
     -> DOC_STALE
     -> CODE_DEVIATION
     -> AMBIGUOUS
     -> PLANNED_NOT_LANDED
```

代码需要改造的问题交给 `architecture-change`，不会在文档同步过程中偷偷修改代码。

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
 -> architecture-documentation (Update)
```

注意顺序：**先实现并通过架构审查，再更新“当前架构”文档**。不能因为方案已经批准，就提前把目标架构写进 `ARCHITECTURE.md`。

### 周期性架构优化

```text
若干 Feature / 一个 Milestone
 -> architecture-health
     -> improve-codebase-architecture
     -> 只选择高价值候选
 -> architecture-change
 -> Execute
 -> architecture-review
 -> architecture-documentation（如果真实结构发生变化）
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

### `ARCHITECTURE.md`（或项目已有权威架构文档）

记录**当前已经验证的结构事实 + 有效结构约束**：

```text
“现在实际是怎样的？后续修改要保持哪些规则？”
```

`architecture-documentation` 负责长期维护这一层。

推荐记录：

```text
模块职责
实际依赖
允许/禁止依赖
稳定 seam
扩展点
关键 runtime/data flow
架构 invariant
known deviations
architecture debt
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
