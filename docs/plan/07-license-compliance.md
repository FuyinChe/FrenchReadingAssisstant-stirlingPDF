# 07 — 许可证与合规说明

> 基于 `stirling-upstream/` 当前版本审阅，实施前请再次核对上游 LICENSE 变更。

## 本仓库（FrenchPdfReader extensions）

| 组件 | 路径 | 建议许可证 |
|------|------|------------|
| 文档 | `docs/` | 与主仓库一致（待定，建议 MIT） |
| French Reader Engine | `extensions/french-reader-engine/` | MIT / Apache-2.0（自研） |
| French Reader Frontend | `extensions/french-reader-frontend/` | 与主仓库一致 |
| 补丁 | `patches/` | 与主仓库一致 |

## Stirling PDF 上游

根目录 [LICENSE](https://github.com/Stirling-Tools/Stirling-PDF/blob/main/LICENSE) 为 **混合许可**：

| 路径 | 许可 |
|------|------|
| 大部分 Java / 核心前端 | **MIT** |
| `engine/` | **[Stirling PDF User License](https://github.com/Stirling-Tools/Stirling-PDF/blob/main/engine/LICENSE)**（商业/试用条款） |
| `app/proprietary/`、`frontend/.../proprietary/` 等 | 各自目录 LICENSE |

### 对 French Reader 的影响

1. **Engine 侧car（当前 M0 方案）**  
   French Reader 运行在 **独立 FastAPI 服务**（`:5002`），**不修改** Stirling `engine/` 源码，降低对 engine 专有许可的触及面。

2. **前端补丁**  
   通过 `patches/frontend/` 修改 MIT 许可下的 `core/types/prototypeToolId.ts` 与 `usePrototypeToolRegistry.tsx`，变更面小且可 `git checkout` 回滚。

3. **生产 / 分发**  
   - 若分发包含 Stirling 整体（Docker / 安装包），须遵守 Stirling PDF User License 及订阅条款。  
   - **内部开发、试用、评估** 通常在 Stirling LICENSE 允许范围内；**生产商用** 需确认是否持有有效 User License。  
   - 本扩展 **不得** 被解读为 Stirling 官方产品；分发时需注明为第三方扩展/魔改版本。

4. **修改与衍生**  
   Stirling engine LICENSE 对修改、衍生、再分发有约束。本项目的策略是：  
   - 优先 **不修改 engine**；  
   - 扩展代码放在 `extensions/` 与本仓库；  
   - 对 Stirling 的改动限于 **文档化的 frontend patch**。

## 计划引入的第三方依赖

| 依赖 | 许可证 | 备注 |
|------|--------|------|
| PaddleOCR | Apache 2.0 | M2+ |
| edge-tts | MIT / GPL（以包为准） | M3+，使用前核对 |
| ultralytics (YOLO) | AGPL-3.0 | M5+，分发需注意 |
| PDF.js（经 Stirling） | Apache 2.0 | 基座自带 |

## 建议动作

- [ ] 正式发布前由法务/负责人确认 Stirling 订阅与分发方式  
- [ ] 在 README 与 About 页注明「基于 Stirling PDF 的扩展版，非官方」  
- [ ] 若向 Stirling 上游贡献 Tool，单独走 CONTRIBUTING / CLA  

## 参考

- [Stirling-PDF LICENSE](https://github.com/Stirling-Tools/Stirling-PDF/blob/main/LICENSE)
- [engine/LICENSE](https://github.com/Stirling-Tools/Stirling-PDF/blob/main/engine/LICENSE)
- [06-stirling-integration-strategy.md](06-stirling-integration-strategy.md)
