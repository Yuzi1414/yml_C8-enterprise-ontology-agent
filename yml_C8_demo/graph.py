"""
属性图（Property Graph）——节点 + 边
模拟 Neo4j / Apache AGE 的核心语义，纯标准库实现。
schema 强约束：节点 label、边关系必须命中本体注册表。
"""
import ontology


class PropertyGraph:
    def __init__(self):
        self.nodes = {}   # id -> {label, props}
        self.edges = []   # {src, rel, dst}

    def add_node(self, node_id, label, props=None):
        if label not in ontology.TBOX["classes"]:
            raise ValueError(f"节点 {node_id} 的 label {label} 未在本体注册")
        self.nodes[node_id] = {"label": label, "props": props or {}}

    def add_edge(self, src, rel, dst):
        if rel not in ontology.TBOX["object_properties"]:
            raise ValueError(f"关系 {rel} 未在本体注册")
        self.edges.append({"src": src, "rel": rel, "dst": dst})

    def neighbors(self, node_id, rel=None, direction="out"):
        """按关系类型取邻接。direction: out / in / both"""
        out = []
        for e in self.edges:
            if direction in ("out", "both") and e["src"] == node_id:
                if rel is None or e["rel"] == rel:
                    out.append((e["rel"], e["dst"]))
            if direction in ("in", "both") and e["dst"] == node_id:
                if rel is None or e["rel"] == rel:
                    out.append(("<-" + e["rel"], e["src"]))
        return out

    def build_from_ontology(self):
        for inst in ontology.ABOX["instances"]:
            props = {k: v for k, v in inst.items() if k not in ("id", "type")}
            self.add_node(inst["id"], inst["type"], props)
        for s, rel, o in ontology.ABOX["assertions"]:
            self.add_edge(s, rel, o)
        return self
