# -*- coding: utf-8 -*-
"""分析viewData.json找出商品信息"""
import json

def find_keys(obj, target_keys, path="", results=None):
    """递归查找包含目标关键字的键"""
    if results is None:
        results = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            # 检查键名是否包含目标关键字
            if any(target in key.lower() for target in target_keys):
                results.append({
                    'path': current_path,
                    'key': key,
                    'value': str(value)[:200] if not isinstance(value, (dict, list)) else f"<{type(value).__name__}>"
                })
            # 递归搜索
            if isinstance(value, (dict, list)):
                find_keys(value, target_keys, current_path, results)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            current_path = f"{path}[{i}]"
            find_keys(item, target_keys, current_path, results)

    return results

# 读取JSON文件
with open("D:/spider/logs/viewData.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 60)
print("搜索商品标题相关字段")
print("=" * 60)
title_results = find_keys(data, ['title', 'name', '标题'])
for r in title_results[:10]:
    print(f"\n路径: {r['path']}")
    print(f"值: {r['value']}")

print("\n" + "=" * 60)
print("搜索商品价格相关字段")
print("=" * 60)
price_results = find_keys(data, ['price', 'amount', '价格'])
for r in price_results[:10]:
    print(f"\n路径: {r['path']}")
    print(f"值: {r['value']}")
