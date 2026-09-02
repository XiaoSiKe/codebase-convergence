# 代码整理修复大师

这是 Codex Skill `codebase-convergence` 的规范源仓库。它可在日常开发中频繁用于修复 Bug、审核代码、整理简化和收敛局部或整个项目，不限于任务的最后阶段。

Skill 以两项不可分割的原则为核心：

- 精准执行：显式假设、最简单的完整方案、可追溯的最小改动和可执行验证；
- 深 Module 收敛：用 Interface、Implementation、Depth、Seam、Adapter、Leverage 和 Locality 判断复杂度应收回哪里。

Finding、证据指纹、规范来源、文档收敛和专业路由是支撑机制，不取代这两个核心。

用户可见名称是“代码整理修复大师”；技术标识继续使用 `codebase-convergence`，以兼容 Codex 的 Skill 命名与 `$codebase-convergence` 调用方式。

## 常用调用

```text
使用 $codebase-convergence 修复这个 Bug，复现后检查相同根因在相关 Module、调用方和测试中是否还存在。
使用 $codebase-convergence 只读审核这个范围，报告 Bug、矛盾、重复知识、浅 Module 和未覆盖风险。
使用 $codebase-convergence 整理并收敛整个项目，只实施有证据、已授权且经验证的最小完整修复。
```

## 仓库结构

```text
codebase-convergence/
├── SKILL.md                  # 精简的协调接口与不可违反的约束
├── agents/openai.yaml       # 中文展示名与默认调用提示
├── references/              # 工作流、架构、文档、路由与 Finding 合同
└── scripts/                 # 只读证据采集与 Finding 指纹校验
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

采集器输出 schema v2。除原有清单外，`git` 对象还包含 `head`、`branch`、`dirty`、`worktree_fingerprint` 和 `fingerprint_method`。指纹由当前提交、已跟踪文件差异与未被忽略的未跟踪文件内容生成，用于标识 Finding 的证据基线；它不是不可变快照，也不证明仓库正确。被忽略的文件、跳过的符号链接、子模块内部状态、采集根目录外的生成物和外部运行时状态不在其覆盖范围内。

为一条 Finding 生成相关文件指纹，验证结构并重新判断证据新鲜度：

```bash
python3 codebase-convergence/scripts/finding_contract.py stamp --root /repository --finding /tmp/finding-draft.json > /tmp/finding.json
python3 codebase-convergence/scripts/finding_contract.py check --root /repository --finding /tmp/finding.json
```

Finding 合同是结构和新鲜度闸门，不机器判定业务正确性、规范来源、Depth、Locality 或修复授权。它无法发现未被声明为相关文件的新调用方，因此高风险修复前仍需重新搜索调用和契约。

物化一个不含期望答案的临时评测仓库：

```bash
python3 scripts/eval_cases.py materialize --case numeric-conflict --output /明确的/空目录
```

检查或预览本地安装时必须提供完整目标目录。`--check` 和 `--dry-run` 不写文件；`--install` 只接受空目标或由本工具管理且没有本地修改的目标。受管文件或安装清单被符号链接替换时会拒绝覆盖：

```bash
python3 scripts/install_local.py --check --target /明确的/codebase-convergence
python3 scripts/install_local.py --dry-run --target /明确的/codebase-convergence
python3 scripts/install_local.py --install --target /明确的/codebase-convergence
```
