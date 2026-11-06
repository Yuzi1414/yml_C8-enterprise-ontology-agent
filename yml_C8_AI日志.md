# C8 AI 日志（yml_C8_AI日志.md）

> 记录 C8「企业本体 Agent 系统」项目中 AI 的每一轮协作：我做什么、AI 做什么、哪里出过问题、怎么修的。

---

## 第 1 轮：选题论证与结构对齐

- **我**：从 C8 材料的 A/B/C 三方向里选 B（企业本体 Agent 系统），并确认五段式提案结构 + KSTAR 执行方案字段。
- **AI**：把「企业本体 Agent 系统」拆成四层工程能力（本体建模 / 知识图谱 / Agent Workflow / 企业场景），并给出可复用的技术栈映射（OWL/RDF/SKOS、Neo4j/AGE、pgvector、KSTAR 回路 + NL2SQL）。
- **我的取舍**：采纳四层拆解；否决「先上 Neo4j/pgvector 真实依赖」的路径，定死「零第三方依赖」底线（延续 C9 可复现原则）。

## 第 2 轮：拿来主义分析

- **AI**：给出 4 个参考来源（OWL 2、Neo4j LPG、GraphRAG、ReAct/LangGraph），每个都含采纳/舍弃/改进。
- **我**：逐条核对——OWL 只保留 T/A-box 语义、舍弃描述逻辑分类器；GraphRAG 只留「本体引导检索」思想、舍弃社区检测管线。最终把四个来源缝成「零依赖、schema 强约束、推理可审计」的组合。

## 第 3 轮：demo 骨架搭建

- **AI**：生成 `ontology.py`（T-box+A-box+校验）、`graph.py`（属性图）、`agent.py`（本体引导推理）、`demo.py`、`test_demo.py`。
- **我**：设计本体类层级（网络资源→站点→机房/基站，链路/服务/故障/客户）和 9 条断言；为消歧对照特意加了一个「B2C客户组」实例，制造真实歧义。

## 第 4 轮：两个 bug 的定位与修复（真实踩坑）

**Bug 1 — NameError（demo.py）**
- 现象：`python demo.py` 报 `NameError: name 'answer_with_ontology' is not defined`。
- 根因：demo.py 里 `import agent` 后却裸调 `answer_with_ontology(q, g)`，漏了 `agent.` 前缀。
- 修复：改为 `agent.answer_with_ontology(q, g)`。

**Bug 2 — 意图词吞并（agent.py，语义级）**
- 现象：`故障F1 影响哪些服务` 返回「未找到匹配实体」，自检断言失败。
- 根因：意图词典里「故障」排在「影响」之前，而「故障F1」是实体名、包含「故障」二字，导致意图被误判成「故障」（其 domain 是「网络资源」，把「故障」类型的 F1 过滤掉了）。
- 修复：把「影响」等动词意图排在「故障」等名词意图之前，并加注释说明这是实体名子串碰撞问题。
- **教训**：意图识别不能只看子串命中，实体名会污染意图词。这一条写进 AAR 改进项。

## 第 5 轮：验证

- `python test_demo.py` → 全部自检通过（schema 校验 0 问题 / 图规模一致 / 推理正确 / 消歧正确）。
- `python demo.py` → 5 条本体引导推理 + 消歧对照全部符合预期。

---

**AI 使用结论**：AI 负责「生成代码 / 提供候选来源」两端，我负责「架构决策 / 本体 schema / 验收标准 / bug 根因判断」。不是一次性让 AI 出全稿，而是多轮结对：AI 产出 → 我评审 → 跑测试 → 定位根因 → 修复回环。
