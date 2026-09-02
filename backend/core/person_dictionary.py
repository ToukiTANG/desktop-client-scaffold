"""
人员相关固定业务字典。

这些字典属于程序业务定义，不存储在 SQLite 中。

约定：
- key: 数据库存储值
- value: 用户界面显示文本
"""


# =========================
# 性别
# =========================

GENDER_OPTIONS = {0: "男", 1: "女"}


# =========================
# 身份类型
# =========================

IDENTITY_OPTIONS = {0: "干部", 1: "干部领导", 2: "工人", 3: "工人代干", 4: "工人锻炼"}


# =========================
# 专业分类
# =========================

SPECIALIZE_CLASSIFY_OPTIONS = {0: "段部", 1: "房建", 2: "公寓"}


# =========================
# 生产组分类
# =========================

PRODUCTION_GROUP_CLASSIFY_OPTIONS = {
    0: "普速铁路房建设备巡检维修人员",
    1: "高速铁路房建设备巡检维修人员",
    2: "行车公寓人员",
}


# =========================
# Excel 文本 -> 数据库存储值
# =========================

GENDER_MAP = {label: value for value, label in GENDER_OPTIONS.items()}

IDENTITY_MAP = {label: value for value, label in IDENTITY_OPTIONS.items()}

SPECIALIZE_CLASSIFY_MAP = {label: value for value, label in SPECIALIZE_CLASSIFY_OPTIONS.items()}

PRODUCTION_GROUP_CLASSIFY_MAP = {label: value for value, label in PRODUCTION_GROUP_CLASSIFY_OPTIONS.items()}
