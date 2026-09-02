# 代码整理修复大师

这是 Codex Skill `codebase-convergence` 的规范源仓库。它用于发现并安全收敛代码、架构、测试、配置和 Markdown 文档之间的缺陷、重复、漂移与前后矛盾。

用户可见名称是“代码整理修复大师”；技术标识继续使用 `codebase-convergence`，以兼容 Codex 的 Skill 命名与 `$codebase-convergence` 调用方式。

## 仓库结构

```text
codebase-convergence/
├── SKILL.md                  # 精简的协调接口与不可违反的约束
├── agents/openai.yaml       # 中文展示名与默认调用提示
├── references/              # 按场景加载的工作流、文档、架构与路由细节
└── scripts/collect_evidence.py # 只读仓库证据采集
CONTEXT.md                   # 本仓库自己的领域术语和维护不变量
evals/cases.json             # 不向被测代理泄露答案的行为评测目录
scripts/                     # 评测夹具和安全安装工具
tests/                       # 无第三方依赖的包、工具和安全行为测试
```

Skill 的行为规范以 [`codebase-convergence/SKILL.md`](codebase-convergence/SKILL.md) 为准；本文件只负责仓库入口，不复制工作流规则。

## 本地验证

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py codebase-convergence
python3 scripts/eval_cases.py validate-cases
python3 scripts/eval_cases.py result-contract
```

第一条命令覆盖包结构、只读证据采集、评测夹具和安装保护；第二条使用 Codex `skill-creator` 自带校验器检查 Skill 包格式；第三条验证行为评测目录的结构与安全不变量；第四条输出不含案例答案的机器结果契约。

## 确定性工具

只读采集仓库证据：

```bash
python3 codebase-convergence/scripts/collect_evidence.py --root /明确的/仓库路径 --pretty
```

物化一个不含期望答案的临时评测仓库：

```bash
python3 scripts/eval_cases.py materialize --case numeric-conflict --output /明确的/空目录
```

检查或预览本地安装时必须提供完整目标目录。`--check` 和 `--dry-run` 不写文件；`--install` 只接受空目标或由本工具管理且没有本地修改的目标：

```bash
python3 scripts/install_local.py --check --target /明确的/codebase-convergence
python3 scripts/install_local.py --dry-run --target /明确的/codebase-convergence
python3 scripts/install_local.py --install --target /明确的/codebase-convergence
```
