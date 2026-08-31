STATUS_OPTIONS = {
    0: "待销号",
    1: "待整改",
    2: "已销号",
}

YES_NO_OPTIONS = {
    0: "否",
    1: "是",
}

CHECK_TYPE_OPTIONS = {
    0: "普通检查-经常性检查",
    1: "专项检查-其他专项",
}

CHECK_WAY_OPTIONS = {
    0: "监控调阅检查",
    1: "现场检查",
}

RISK_LEVEL_OPTIONS = {
    0: "低安全风险",
    1: "较大安全风险",
    2: "一般安全风险",
    3: "重大安全风险",
}

PROBLEM_CLASSIFY_OPTIONS = {
    0: "安全管理",
    1: "专业管理",
    2: "机动车",
    3: "劳动纪律",
    4: "生产作业",
    5: "特种设备",
    6: "消防",
    7: "其他设施设备",
    8: "其他",
}

PROBLEM_LABEL_OPTIONS = {
    0: "A",
    1: "B",
    2: "C",
    3: "D",
}

PROBLEM_DICTIONARY = {
    "status": STATUS_OPTIONS,
    "decomposed": YES_NO_OPTIONS,
    "revised": YES_NO_OPTIONS,
    "assessed": YES_NO_OPTIONS,
    "checkType": CHECK_TYPE_OPTIONS,
    "checkWay": CHECK_WAY_OPTIONS,
    "riskLevel": RISK_LEVEL_OPTIONS,
    "problemClassify": PROBLEM_CLASSIFY_OPTIONS,
    "problemLabel": PROBLEM_LABEL_OPTIONS,
    "redLine": YES_NO_OPTIONS,
    "crossUnit": YES_NO_OPTIONS,
    "businessGuidance": YES_NO_OPTIONS,
    "outside": YES_NO_OPTIONS,
}

STATUS_MAP = {label: value for value, label in STATUS_OPTIONS.items()}
YES_NO_MAP = {label: value for value, label in YES_NO_OPTIONS.items()}
CHECK_TYPE_MAP = {label: value for value, label in CHECK_TYPE_OPTIONS.items()}
CHECK_WAY_MAP = {label: value for value, label in CHECK_WAY_OPTIONS.items()}
RISK_LEVEL_MAP = {label: value for value, label in RISK_LEVEL_OPTIONS.items()}
PROBLEM_CLASSIFY_MAP = {label: value for value, label in PROBLEM_CLASSIFY_OPTIONS.items()}
PROBLEM_LABEL_MAP = {label: value for value, label in PROBLEM_LABEL_OPTIONS.items()}