"""
C8 早期验证物 · 端到端演示
用法: python demo.py
"""
import ontology
import agent
from graph import PropertyGraph


def main():
    print("=" * 62)
    print("企业本体 Agent 系统 · 电信运营商数字孪生 · 演示")
    print("=" * 62)

    # 1. 本体一致性校验
    issues = ontology.validate()
    print("\n[1] 本体一致性校验")
    print(f"  T-box 类数量: {len(ontology.TBOX['classes'])}")
    print(f"  对象属性数量: {len(ontology.TBOX['object_properties'])}")
    print(f"  数据属性数量: {len(ontology.TBOX['data_properties'])}")
    print("  校验结果:", "通过（0 问题）" if not issues else issues)

    # 2. 建属性图
    g = PropertyGraph().build_from_ontology()
    print(f"\n[2] 属性图已构建: {len(g.nodes)} 节点, {len(g.edges)} 边")

    # 3. 本体引导推理
    print("\n[3] 本体引导推理（自然语言 → 图遍历）")
    queries = [
        "光缆L1 发生了什么故障",
        "故障F1 影响哪些服务",
        "服务S1_宽带 由哪个链路承载",
        "路由器R1 位于哪里",
        "光缆L1 可用率",
    ]
    for q in queries:
        ans, trace = agent.answer_with_ontology(q, g)
        print(f"\n  问: {q}")
        for t in trace:
            print(f"    · {t}")
        print(f"  答: {ans}")

    # 4. 消歧对照：本体 vs 纯关键词
    print("\n[4] 消歧对照（证明本体价值）")
    naive = agent.answer_naive("B")
    onto = agent.disambiguate("B", "网络资源")
    print("  提及: B")
    print(f"  纯关键词（无本体）: {naive}")
    print(f"  本体消歧（限 网络资源）: {[i['id'] + '(' + i['type'] + ')' for i in onto]}")
    print("  结论: 本体用类型层级把「客户」B2C客户组 剔除，只保留「站点」基站B")

    print("\n" + "=" * 62)
    print("演示完成：端到端闭环 + 本体消歧优于纯关键词")
    print("=" * 62)


if __name__ == "__main__":
    main()
