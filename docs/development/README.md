# 开发文档

本目录存放 **随迭代更新** 的开发追踪文档。

| 文件 | 用途 |
|------|------|
| [backlog.md](backlog.md) | 可执行任务清单（按里程碑分组，带 ID） |
| [progress.md](progress.md) | Sprint / 周报进度与阻塞项 |

## 任务 ID 规则

```
TASK-{里程碑编号}{序号}
例：TASK-M001 = M0 第 1 项
    TASK-M210 = M2 第 10 项
```

## 更新流程

1. 从 backlog 选取 `[ ]` 任务 → 改为 `[~]`，写入 progress「进行中」
2. 完成后改为 `[x]`，在 progress 记录完成日期与 PR/commit
3. 新需求：在 backlog 对应里程碑下追加，必要时回溯更新 `plan/`

## 关联

- 计划文档：`../plan/`
- 架构/API 变更：同步更新 `../plan/02-architecture.md`
