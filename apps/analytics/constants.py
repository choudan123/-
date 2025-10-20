import math

# 行为事件类型
EVENT_VIEW = 'VIEW'                 # 浏览/预览
EVENT_SELECT_TYPE = 'SELECT_TYPE'   # 选择了某个海报类型
EVENT_SELECT_STYLE = 'SELECT_STYLE' # 选择了某个风格
EVENT_GENERATE = 'GENERATE'         # 点击生成
EVENT_DOWNLOAD = 'DOWNLOAD'         # 下载

EVENT_CHOICES = [
    (EVENT_VIEW, 'View'),
    (EVENT_SELECT_TYPE, 'Select Type'),
    (EVENT_SELECT_STYLE, 'Select Style'),
    (EVENT_GENERATE, 'Generate'),
    (EVENT_DOWNLOAD, 'Download'),
]

# 事件权重（可按业务调参）
EVENT_WEIGHTS = {
    EVENT_VIEW: 0.2,
    EVENT_SELECT_TYPE: 0.5,
    EVENT_SELECT_STYLE: 0.3,
    EVENT_GENERATE: 1.0,
    EVENT_DOWNLOAD: 1.2,
}

# 时间衰减：半衰期（天）
HALF_LIFE_DAYS = 14.0
LAMBDA = math.log(2) / HALF_LIFE_DAYS