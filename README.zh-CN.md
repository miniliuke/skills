# Agent Specialist Skills Bundle（中文说明）

这是一套面向 Coding Agent 的**专项工程 Skills** 集合。

新的职责边界很简单：

```text
Ponytail
  -> 常驻负责 YAGNI、复用优先、最小实现、避免过度工程

Minimal engineering guardrails
  -> 常驻负责架构安全底线 + 轻量 TDD 纪律

skills/
  -> 只处理真正需要专项方法论的任务
```

普通 Feature / Bug / UI / 配置修改不应该为了“走流程”而调用本仓库任何 Skill。

## 1. 先安装 Ponytail

本仓库不再复制 Ponytail，也不再用 Skill 重复实现它的复杂度控制规则。推荐直接使用官方插件：

[Ponytail](https://github.com/DietrichGebert/ponytail)

### Codex

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex
```

进入 Codex 后：

```text
/plugins -> 从 Ponytail marketplace 安装 Ponytail
/hooks   -> 检查并信任两个 lifecycle hooks
```

然后开启新 thread。Node.js 需要在非交互 shell 的 PATH 中，才能启用常驻 hook 注入。

### Claude Code

```text
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```

## 2. 安装本仓库的专项 Skills

查看可用 Skill：

```bash
npx skills add miniliuke/skills --list
```

如果希望全部安装：

```bash
npx skills add miniliuke/skills --skill '*'
```

现在 `skills/` 中只保留专项能力，因此全量安装不再意味着给普通开发附加默认 workflow。

Antigravity：

```bash
npx skills add miniliuke/skills --skill '*' --agent antigravity
```

Claude Code：

```bash
npx skills add miniliuke/skills --skill '*' --agent claude-code
```

## 3. 最小常驻工程约束

`guardrails/engineering.md` 是一个很短的、**非 Skill** 的规则片段，适合合并到全局或项目级 `AGENTS.md` / agent instructions。

它只补 Ponytail 不负责的两件事：

- 架构安全底线：ownership、dependency direction、public contract / seam；
- 轻量 TDD：已有测试设施时，优先最小失败测试 -> 最小实现 -> 相关回归测试。

它不会重复 Ponytail 的 YAGNI / 少写代码 / 复用规则，也不会启动额外 workflow。

## 4. 当前专项 Skills

### `architecture`

**显式架构入口。** 用于：

- 新项目 / 新 subsystem / 新模块架构设计；
- ownership、dependency、public seam、runtime/data flow 等结构性变更；
- 架构 Review；
- `ARCHITECTURE.md` Bootstrap / Update / Reconcile；
- 显式的架构健康检查。

它内部按请求选择 Design / Change / Review / Document / Health，一个任务只进入需要的模式。

### `codebase-design`

当问题本身就是 load-bearing module、interface、seam、deep module 如何设计时使用。

不要把它作为普通 Feature 的默认设计步骤。

### `domain-modeling`

当核心概念、术语、状态、生命周期 ownership 本身没有定义清楚时使用。

普通字段、DTO、接口参数变化不因此自动进入 domain modeling。

### `diagnosing-bugs`

用于真正需要系统诊断的难复现 Bug、复杂故障或性能回退。

明显的局部 Bug 应优先直接复现、修复、测试，不要为了一个简单错误进入完整 diagnosis workflow。

### `grilling`

用户明确希望对计划、设计或决策进行高强度追问 / stress-test 时使用。

### `writing-for-agents`

用于编写面向 Agent 的说明、规则或上下文材料。

## 5. 被移除的入口

### `architecture-guard`

删除。架构安全底线迁移到 `guardrails/engineering.md`，不再作为 Skill 占用默认技能空间。

### `tdd-guard`

删除。TDD 作为几条常驻工程纪律保留在 guardrail 中，而不是一个可触发的 workflow。

### `grill-me`

删除。它只是 `grilling` 的薄包装。

### `grill-with-docs`

删除。它只是 `grilling + domain-modeling` 的级联包装。确实同时需要两者时，由任务本身决定，而不是通过一个 wrapper 自动串联。

上游 `tdd` 和 `improve-codebase-architecture` 仍然不镜像。

## 6. 默认任务路由

```text
普通开发
  -> Ponytail
  -> Native Plan / Execute
  -> minimal engineering guardrails
  -> focused tests
  -> done

真正的专项任务
  -> Ponytail
  -> 选择一个最匹配的 Skill
  -> Native Plan / Execute
  -> done
```

关键规则：

```text
不要因为 Skill 已安装就调用它。
不要把多个 Skill 串成固定流水线。
默认一个任务最多一个主 Skill。
Supporting skill 只在它解决一个独立且真实的问题时才使用。
```

Ponytail 决定**事情应该做多简单**；专项 Skill 只决定**这个专项问题应该怎么做**。

## 7. 长期架构记忆

继续区分：

```text
CONTEXT.md
  领域语言：概念是什么？

docs/adr/
  重要决策：为什么这样决定？

ARCHITECTURE.md
  已经验证的当前结构事实与约束。
```

`ARCHITECTURE.md` 只描述已经落地的架构，不把计划中的目标状态提前写成当前事实。

## 8. 自动同步

`.github/workflows/sync-mattpocock-skills.yml` 每天同步仍有独立价值的 Matt Pocock Skills：

```text
codebase-design
domain-modeling
diagnosing-bugs
grilling
writing-for-agents
```

自定义 `architecture` 记录在 `.github/custom-skills.txt`，不会被上游同名内容覆盖。

## 最终心智模型

人只需要记住三句话：

```text
复杂度：Ponytail 管。
普通工程纪律：guardrail 管，不是 Skill。
专项问题：才调用 Skill。
```
