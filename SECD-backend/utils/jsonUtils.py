import json


def snake_to_camel(snake_str):
    """将下划线命名转换为驼峰命名"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def to_dict(obj, ignore=(), require=None):
    """将一个Python对象转换为JSON对象"""
    if obj is None:
        return None

    custom_dict = {}

    for key, value in obj.__dict__.items():
        # 将自定义属性转化为驼峰格式的键值对
        if not (key.startswith('_') or key.endswith('_')) and key not in ignore:
            if require and key not in require:
                continue
            # 若值仍为对象，则作递归处理
            if hasattr(value, '__dict__'):
                value = to_dict(value)
            custom_dict[snake_to_camel(key)] = value

    return custom_dict


class CustomJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器"""
    def default(self, obj):
        if hasattr(obj, '__dict__'):
            return to_dict(obj)
        return super().default(obj)
