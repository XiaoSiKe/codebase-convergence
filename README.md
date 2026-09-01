# 代码整理修复大师

这是 Codex Skill `codebase-convergence` 的规范源仓库。它用于发现并安全收敛代码、架构、测试、配置和 Markdown 文档之间的缺陷、重复、漂移与前后矛盾。

用户可见名称是“代码整理修复大师”；技术标识继续使用 `codebase-convergence`，以兼容 Codex 的 Skill 命名与 `$codebase-convergence` 调用方式。

## 仓库结构

```text
codebase-convergence/
├── SKILL.md                  # 精简的协调接口与不可违反的约束
├── agents/openai.yaml       # 中文展示名与默认调用提示
└── references/              # 按场景加载的工作流、文档、架构与路由细节
CONTEXT.md                   # 本仓库自己的领域术语和维护不变量
tests/test_skill_package.py  # 无第三方依赖的包结构与收敛性测试
```

Skill 的行为规范以 [`codebase-convergence/SKILL.md`](codebase-convergence/SKILL.md) 为准；本文件只负责仓库入口，不复制工作流规则。

## 本地验证

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py codebase-convergence
```

第一条命令验证技术标识、本地链接、渐进式披露可达性、中文 UI 元数据和跨文档重复；第二条使用 Codex `skill-creator` 自带校验器检查 Skill 包格式。
