"""
电信运营商数字孪生 · 本体（Ontology）定义
T-box（术语层）：类层级 + 对象属性 + 数据属性
A-box（断言层）：实例 + 关系断言
纯标准库实现，零第三方依赖（延续 C9 原则）。
"""

TBOX = {
    "classes": {
        "网络资源": {"subclass_of": None, "注释": "可管理、监控、调度的物理/逻辑资源"},
        "站点": {"subclass_of": "网络资源", "注释": "物理位置（机房/基站等）"},
        "机房": {"subclass_of": "站点", "注释": "数据中心机房"},
        "基站": {"subclass_of": "站点", "注释": "无线基站站点"},
        "网络设备": {"subclass_of": "网络资源", "注释": "路由器/交换机等"},
        "链路": {"subclass_of": "网络资源", "注释": "光缆等连接"},
        "服务": {"subclass_of": None, "注释": "面向客户的业务服务"},
        "故障": {"subclass_of": None, "注释": "网络异常事件"},
        "客户": {"subclass_of": None, "注释": "使用服务的对象"},
    },
    "object_properties": {
        "位于": {"domain": "网络资源", "range": "站点", "注释": "资源部署位置"},
        "承载": {"domain": "链路", "range": "服务", "注释": "链路承载业务"},
        "连接": {"domain": "网络资源", "range": "网络资源", "注释": "拓扑连接"},
        "发生故障": {"domain": "网络资源", "range": "故障"},
        "影响": {"domain": "故障", "range": "服务"},
        "订购": {"domain": "客户", "range": "服务"},
    },
    "data_properties": {
        "容量": {"domain": "链路", "range": "float", "单位": "Gbps"},
        "可用率": {"domain": "网络资源", "range": "float", "单位": "%"},
        "严重度": {"domain": "故障", "range": "str", "枚举": ["P1", "P2", "P3", "P4"]},
    },
}

ABOX = {
    "instances": [
        {"id": "核心机房A", "type": "机房", "可用率": 0.9999},
        {"id": "基站B", "type": "基站", "可用率": 0.998},
        {"id": "光缆L1", "type": "链路", "容量": 100.0, "可用率": 0.997},
        {"id": "路由器R1", "type": "网络设备", "可用率": 0.9995},
        {"id": "故障F1", "type": "故障", "严重度": "P1"},
        {"id": "客户YML", "type": "客户"},
        {"id": "B2C客户组", "type": "客户"},
        {"id": "服务S1_宽带", "type": "服务"},
    ],
    "assertions": [
        ("路由器R1", "位于", "核心机房A"),
        ("基站B", "位于", "核心机房A"),
        ("光缆L1", "连接", "核心机房A"),
        ("光缆L1", "连接", "基站B"),
        ("光缆L1", "承载", "服务S1_宽带"),
        ("客户YML", "订购", "服务S1_宽带"),
        ("B2C客户组", "订购", "服务S1_宽带"),
        ("光缆L1", "发生故障", "故障F1"),
        ("故障F1", "影响", "服务S1_宽带"),
    ],
}


def class_of(instance_id):
    """返回实例的本体类型。"""
    for inst in ABOX["instances"]:
        if inst["id"] == instance_id:
            return inst["type"]
    return None


def is_subclass(child, parent):
    """本体类层级判定（含传递性）。"""
    cur = child
    while cur is not None:
        if cur == parent:
            return True
        cur = TBOX["classes"].get(cur, {}).get("subclass_of")
    return False


def validate(instances=None):
    """校验 A-box 与 T-box 一致：类型存在、断言 domain/range 合规。"""
    issues = []
    for inst in instances or ABOX["instances"]:
        if inst["type"] not in TBOX["classes"]:
            issues.append(f"实例 {inst['id']} 类型 {inst['type']} 未在本体注册")
    for s, rel, o in ABOX["assertions"]:
        if rel not in TBOX["object_properties"]:
            issues.append(f"关系 {rel} 未在本体注册")
            continue
        op = TBOX["object_properties"][rel]
        s_type, o_type = class_of(s), class_of(o)
        if s_type and op.get("domain") and not is_subclass(s_type, op["domain"]):
            issues.append(f"断言 ({s},{rel},{o}) domain 不符：{s_type} 非 {op['domain']} 子类")
        if o_type and op.get("range") and not is_subclass(o_type, op["range"]):
            issues.append(f"断言 ({s},{rel},{o}) range 不符：{o_type} 非 {op['range']} 子类")
    return issues
