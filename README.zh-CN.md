# Agent Engineering Skills Bundle（中文说明）

这是一套面向 Coding Agent 的轻量工程 Skills 集合。目标不是建立更多流程，而是让 Agent 在默认开发流程中遵守少量关键约束，只在确实需要时进入深度设计。

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

## 默认开发原则

普通 Feature / Bug 不启动额外 architecture 或 TDD workflow：

```text
Requirement
  -> Agent Plan Mode
  -> Execute
       + architecture-guard
       + tdd-guard
  -> Tests
  -> Review
```

`architecture-guard` 和 `tdd-guard` 是轻量行为约束，不应该产生额外的设计会话、文档或长篇分析。

## 架构 Skills：只保留两个入口

### `architecture-guard`

默认隐式使用。

它只检查普通修改是否意外破坏：

- 模块 ownership；
- dependency direction；
- public contract / seam；
- abstraction 边界。

没有冲突时不输出架构分析，也不自动调用其他架构 Skill。

### `architecture`

唯一需要人主动记住的架构 Skill。

当用户明确要做架构工作时使用，例如：

```text
设计新项目架构
设计新模块/插件
调整现有模块边界
做架构 Review
建立或更新 ARCHITECTURE.md
分析项目架构问题并提出优化方向
```

内部会根据请求自动选择模式：

```text
Design    新项目 / 新模块 / 新 subsystem
Change    ownership / dependency / seam / runtime flow 变化
Review    plan / diff / branch / PR 的架构检查
Document  Bootstrap / Update / Reconcile 架构文档
Health    结构健康检查和优化候选
```

用户不需要再选择 `architecture-change`、`new-module-architecture`、`architecture-review` 等多个近似 Skill。

`architecture` 默认也不会级联调用一串其他 Skill。只有领域含义本身需要重新建模时才考虑 `domain-modeling`，只有核心 module/interface 需要深入设计时才考虑 `codebase-design`。

## TDD

### `tdd-guard`

默认隐式使用，把 TDD 作为开发纪律，而不是独立推理流程：

```text
可测试的行为
  -> 最小失败测试
  -> 确认失败原因
  -> 最小实现
  -> 测试通过
  -> 必要的附近回归测试
```

不会默认创建 TDD plan、测试策略文档、seam 设计会话，也不会为了普通测试自动引入 `codebase-design`。

对于没有合适测试设施、简单配置/文档或测试脚手架成本明显超过修改本身的任务，不强制执行仪式化 test-first。

## 保留的 Matt Pocock Skills

CI 只同步当前仍有独立价值的上游 Skills：

```text
codebase-design
domain-modeling
diagnosing-bugs
grill-with-docs
grill-me
grilling
writing-for-agents
```

不再同步功能已被本仓库轻量 guard / unified architecture 覆盖的 `tdd` 和 `improve-codebase-architecture`。

### 什么时候直接使用 `codebase-design`

当问题本身就是模块/interface/seam 如何设计，而不是泛化的架构流程时使用。

### 什么时候直接使用 `domain-modeling`

当核心概念、术语、状态或生命周期 ownership 本身不清楚时使用。

它们都不是普通 Feature 的默认步骤。

## 长期架构记忆

推荐继续区分三类信息：

```text
CONTEXT.md
  领域语言：概念是什么？

docs/adr/
  重要决策：为什么这样决定？

ARCHITECTURE.md
  当前已经验证的结构事实和约束：系统现在如何划分？
```

重要规则：

```text
ARCHITECTURE.md 描述已经落地的当前架构。
计划中的目标架构不能提前写成当前事实。
```

`architecture` 的 Document 模式负责 Bootstrap / Update / Reconcile。

## 自动同步

`.github/workflows/sync-mattpocock-skills.yml`：

- 每天同步一次，也支持手动触发；
- 只同步明确列出的 Matt Skills；
- 不执行上游脚本；
- 自定义 Skill 名称记录在 `.github/custom-skills.txt`，禁止被上游同名内容静默覆盖；
- 校验 vendored `SKILL.md` 的名称；
- 保留上游 commit SHA 和 MIT License；
- 没有内容变化时不产生空 commit。

## 最终心智模型

人只需要记住：

```text
普通开发：不用选 architecture skill
真正的架构任务：architecture
```

其余复杂度由 Skill 内部按需处理，而不是暴露成一串工作流名称。
