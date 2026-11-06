"""
本体引导的 Agent 工作流
流程：解析意图 → 本体消歧 → 图推理 → 生成答案
LLM 只承担两端（意图解析、答案生成）的不确定性工作；
中间实体消歧与图推理由确定性的本体 + 图完成（可审计、可回放）。
"""
import ontology

# 意图词 → 本体规格（domain 类型 / 对象属性 / 遍历方向）
# 注意：「影响」须排在「故障」之前——「故障F1」是实体名，若先匹配「故障」会吞掉「影响」意图。
INTENT = {
    "影响": {"domain": "故障", "rel": "影响", "dir": "out"},
    "承载": {"domain": "服务", "rel": "承载", "dir": "in"},
    "位于": {"domain": "网络资源", "rel": "位于", "dir": "out"},
    "订购": {"domain": "客户", "rel": "订购", "dir": "out"},
    "可用率": {"domain": "网络资源", "rel": None, "dir": "prop"},
    "故障": {"domain": "网络资源", "rel": "发生故障", "dir": "out"},
}


def find_instances(mention):
    """候选实例：实例 id 与 mention 互含。"""
    mention = (mention or "").strip()
    out = []
    for i in ontology.ABOX["instances"]:
        if mention and (mention in i["id"] or i["id"] in mention):
            out.append(i)
    return out


def disambiguate(mention, expected_type=None):
    """本体消歧：候选实例 + 本体类型层级过滤。"""
    hits = find_instances(mention)
    if expected_type:
        hits = [h for h in hits if ontology.is_subclass(h["type"], expected_type)]
    return hits


def answer_with_ontology(query, graph):
    """本体引导的回答，返回 (answers, trace)。"""
    trace = []
    intent = next((k for k in INTENT if k in query), None)
    if not intent:
        return "无法识别意图", trace
    spec = INTENT[intent]

    candidates = find_instances(query)
    trace.append(f"候选实例（消歧前）: {[i['id'] for i in candidates]}")
    narrowed = [i for i in candidates if ontology.is_subclass(i["type"], spec["domain"])]
    trace.append(f"本体消歧（限 {spec['domain']}）: {[i['id'] for i in narrowed]}")
    if not narrowed:
        return "未找到匹配实体", trace

    results = []
    for inst in narrowed:
        nid = inst["id"]
        if spec["dir"] == "prop":
            val = graph.nodes[nid]["props"].get(intent)
            results.append(f"{nid}.{intent} = {val}")
            trace.append(f"数据属性: {nid}.{intent} = {val}")
        else:
            for r, dst in graph.neighbors(nid, rel=spec["rel"], direction=spec["dir"]):
                if spec["dir"] == "in":
                    results.append(f"{dst} -[{spec['rel']}]-> {nid}")
                    trace.append(f"图遍历(反向): {dst} -[{spec['rel']}]-> {nid}")
                else:
                    results.append(f"{nid} -[{r}]-> {dst}")
                    trace.append(f"图遍历: {nid} -[{r}]-> {dst}")
    return (results if results else "无结果", trace)


def answer_naive(mention):
    """对照组：纯关键词，不做本体消歧。"""
    return [f"{i['id']}({i['type']})" for i in find_instances(mention)]
