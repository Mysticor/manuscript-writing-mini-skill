---
name: manuscript-writing-mini
description: >
  Manuscript Writing Mini：承接蓝图或蓝图mini的真实证据，用简洁写作方案、早期样稿和逐章图文协作完成论文初稿。
  用于写作mini、轻量论文写作、按章节继续和局部修改；保留来源核验与审稿交接，不做正式审稿或排版。
---
# Manuscript Writing Mini

Research Workflow Skills · 02 · Writing. See the repository README for the four-stage series and installation.

承接已选研究方向与实际证据，不重新选题。完成可交给 manuscript-review-mini（或兼容的 manuscript-review）的完整 Markdown 初稿。

## 开始
定位实际研究目录。恢复先读 state.json、resume.md（如有）及当前章节；初次读交接就绪状态、核心主张/结果、方法与限制。脚本检查全部文件与哈希不等于 Agent 已读懂全部内容；相关原文在使用时查证。
交接含100篇候选→20篇核心精读任务时，核对实际筛选/阅读记录、全文笔记和跨文献综合，沿用据此形成的内容方案；不能把期刊数量对照当作科学精读。缺额返回上游待办并说明内容判断限制，仍可写不依赖缺证据的部分；不擅自重跑全部检索或把未完成准备说成就绪。
用 Python 3.11+ 运行本 Skill 的 scripts/manuscriptctl.py；新项目 `init DEST --handoff SOURCE --paper-type TYPE`，已有目录不重建。原版和 mini 不并发编辑同一论文。
运行 scripts/projectctl.py open PROJECT；首次处理 Gate、版本或交接时读[共享契约](../../../workflow-contract/README.md)，按需读取[阶段规则](references/workflow.md)。

## 尽早让用户看到文章
先写一份简洁的 manuscript_blueprint/writing_plan.md：文章定位、章节与证据、必要图表与来源、边界及交付。目标期刊明确时按[期刊全文对照](references/journal-benchmarking.md)复用或补齐目标刊约10篇、同领域同文类且水平相近的其他期刊合计约10篇真实全文，用分组结果校准论文体量、图表及引用方案。按[文献覆盖](references/citation-planning.md)落实引用，按[全篇图表规划](references/display-architecture.md)确定图表作用和正文/SI安排；有实质收益时充分安排，不套固定张数或倍率。源自研究交接的方向直接沿用；新的重大写作取舍才询问，不用 AUTO 替用户改变研究方向。
方向一致后尽早给一个代表性小节，让用户看到组织方式、细节深度和表达。已有认可范例直接复用；没有范例时先展示样稿并收集反馈，再展开大量同类正文，不要求每节重复确认。
样稿可以在全部图表制作之前完成，但只能用已核实证据；它不是整篇就绪标记。不要等十份规划或所有图表做好才给用户正文。

## 按章节推进
默认每批完成一个实质小节及其所需图表。按[写作与工具规则](references/adapters.md)调用 nature-writing；只读当前论文类型、章节和必要资源。
方案沿用 claim_evidence_map.csv 和 section_registry.csv，方案写引用和论证关系，不再另抄一份主张账本。全篇规划保持简短，确定制作的图表才展开[绘图简报与交接要求](references/figure-planning.md)或[表格说明](references/table-planning.md)。先定科学内容与证据组织，再选单面板或多面板及对应简报；不能为保持 compact 而删减必要信息。将具体表达要求传给 nature-figure，沿用认可基准，并检查信息是否充分、科学关系是否正确，而不只检查配色和导出。
选中文献图表、公式与具体数值，按[原文核验](references/targeted-source-verification.md)回查，不重新精读整个文献库。图表与正文可交替推进；必需图表未完成可继续独立正文，但不能宣称完整初稿就绪。
每批把长材料留在文件里，只返回关键成果与定位；更新 state.next_actions 和根目录 resume.md（当前章节、完成文件、待办/阻塞、已有决定，通常一页内）。resume 不放进 manuscript_blueprint，避免进度更新使科学方案失效。
新图表简报或科学方案变化需更新并重新记录受影响的 Gate C/lock；沿用已定方向，不重新让用户批准整套方案。

## 完成
整合到 manuscript.md。通读全稿，检查数字/引用/主张、术语、章节衔接、图表及图注；回查关键内容是否缺少必要的视觉证据、现有图是否重复或表达不足，按[就绪规则](references/readiness-gates.md) check/finalize。无补充材料时 supplementary.md 简述不需要的理由，不制造 SI。
保留原来的真实证据、数值追溯、资产来源/权限、MOCK 隔离和[审稿交接](references/handoff-contract.md)。关键证据不足明确阻塞，只继续不依赖它的工作。
A/B/C/D 是记录检查点，技术选择按共享契约 AUTO；不虚构用户同意。这里只完成初稿，不调用正式 reviewer/polishing/LaTeX，不承诺消除远程压缩故障。
