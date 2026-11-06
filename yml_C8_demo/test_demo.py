"""
C8 早期验证物 · 自检（test_demo.py）
用法: python test_demo.py
"""
import ontology
from graph import PropertyGraph
from agent import answer_with_ontology, disambiguate


def test_schema_valid():
    assert ontology.validate() == [], "本体校验应零问题"


def test_graph_build():
    g = PropertyGraph().build_from_ontology()
    assert len(g.nodes) == len(ontology.ABOX["instances"])
    assert len(g.edges) == len(ontology.ABOX["assertions"])


def test_reasoning():
    g = PropertyGraph().build_from_ontology()
    ans, _ = answer_with_ontology("光缆L1 发生了什么故障", g)
    assert any("故障F1" in a for a in ans)
    ans, _ = answer_with_ontology("故障F1 影响哪些服务", g)
    assert any("服务S1_宽带" in a for a in ans)
    ans, _ = answer_with_ontology("服务S1_宽带 由哪个链路承载", g)
    assert any("光缆L1" in a for a in ans)


def test_disambiguation():
    naive = disambiguate("B")
    onto = disambiguate("B", "网络资源")
    assert len(naive) >= 2, "纯关键词应命中多个候选"
    assert [i["id"] for i in onto] == ["基站B"], "本体应只保留基站B"


if __name__ == "__main__":
    test_schema_valid()
    test_graph_build()
    test_reasoning()
    test_disambiguation()
    print("全部自检通过 ✅")
