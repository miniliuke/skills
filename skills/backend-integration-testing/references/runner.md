# 可选的顺序运行器

仅在项目缺少合适入口时使用。Python 3.9+，标准库，无第三方运行依赖。复制 `scripts/run_suite.py` 到项目并纳入版本控制；不会要求安装本技能才能重跑。

`assets/suite.example.json` 是接口示例，里面的 env.py/data.py/业务脚本需要根据真实项目实现并替换；它本身不是可运行的项目测试。不要以示例流程通过声称被测产品通过。

```bash
python tests/integration/run_suite.py tests/integration/suite.json --root .
python tests/integration/run_suite.py tests/integration/suite.json --root . --case IT-001
```

默认产物目录为项目根目录 `.integration-artifacts/<run_id>/`，加入 `.gitignore`。可用 `--output` 覆盖；相对路径以 `--root` 为基准，suite 文件参数相对于启动命令的当前目录。

## 配置

JSON 顶层阶段：preflight、setup、ready、seed、cases、collect、cleanup。除 cases 外可以省略；cases 至少一条，每条包含唯一 `id` 和非空 `steps` 数组。每个阶段是步骤数组：

```json
{"id": "check-db", "cmd": ["python", "tests/integration/check_db.py"], "timeout": 30}
```

步骤 ID 在所属阶段/用例内唯一；ID 只允许字母、数字、下划线、连字符。`cmd` 是 argv，不进行 shell、通配符或 `$VAR` 插值。需要 shell/SQL 重定向时写入项目脚本，显式调用 `bash`/PowerShell 或 Python；凭据通过环境传入，不写命令参数。

每步默认超时 120 秒。退出码 0 表示成功，其他为失败。断言由用例脚本/现有框架执行，并将期望/实际的紧凑差异写入日志。运行器不会把打印“失败”当成失败，也不解析 JUnit 的内部用例；嵌套框架的细分结果仍看其原始报告。

脚本继承环境，额外得到：

| 变量 | 用途 |
| --- | --- |
| IT_RUN_ID | 本次运行的唯一命名空间，可直接用作 Compose project name |
| IT_CASE_ID | 当前用例 ID，环境阶段为空 |
| IT_ARTIFACT_DIR | 本次运行产物的绝对目录 |
| IT_PROJECT_ROOT | 项目绝对路径，也是所有命令的工作目录 |

跨步骤状态保存在 IT_ARTIFACT_DIR 中（如资源清单、请求返回 ID），子进程修改环境变量不会传播到下一步。跨用例业务依赖合并为同一 case 的 steps；本运行器不实现 DAG/后台服务管理/隐式重试。

## 结果与清理

预检/环境阶段失败使业务用例 BLOCKED。单个 case 内失败停止后续步骤，但继续独立 case。collect 和 cleanup 在成功、失败、超时及第一次中断后均尝试执行，包括部分 setup 失败；脚本必须容忍资源尚未创建。

用例需要的独立清理可写在用例脚本的 finally 中；全局 cleanup 根据归属记录兜底。独立用例不得污染彼此，重跑选中的 case 仍会执行全套环境阶段。

超时终止步骤进程及其进程组（Windows 尝试 taskkill /T）；环境脚本创建的 Docker 容器/长驻服务仍由 cleanup 回收。SIGKILL/断电不保证清理。终结阶段忽略后续 INT/TERM，每个步骤仍受 timeout 限制。

退出码：0 全部通过；1 用例失败；2 配置、环境、采集或清理失败/阻塞；130 中断。环境错误可能与业务失败并存，详细结果不会被后一个退出码覆盖。运行器不提供 SKIP，确需跳过使用现有框架并在报告中注明。

`results.json` 保存 case 状态、每步退出码/耗时/日志路径和失败片段；`summary.txt` 保存紧凑摘要（片段总预算 12000 字符）；stdout 只有计数和摘要路径。先读 summary，再针对性读结果或原始日志。原始日志不脱敏、不自动上传；`redact_env` 指定的环境值和部分常见字段只在摘要/结果片段中遮蔽，项目仍需负责个人数据和自定义格式的脱敏。

此运行器不调用 AI，也不修改业务代码。“自动迭代”由显式启用本技能的模型根据 SKILL.md 的预算和边界执行；每轮调用同一入口并保留不同 run_id。
