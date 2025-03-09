import copy
import json
import re
from deepdiff import DeepDiff

import make_rap_trial as MRT

def camel_to_snake(name: str) -> str:
    """CamelCase を snake_case に変換"""
    name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)  # 小文字+大文字の境目に `_` を追加
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)  # 連続大文字 + 小文字の境目に `_` を追加
    name = re.sub(r'([a-zA-Z])([0-9])', r'\1_\2', name)  # アルファベット + 数字の間に `_` を追加
    return name.lower()

def snake_to_camel(name: str) -> str:
    """snake_case を camelCase に変換"""
    return re.sub(r'_([a-zA-Z0-9])', lambda m: m.group(1).upper(), name)


def convert_dict_keys(data, convert_func):
    """Recursively convert dictionary keys using the given function."""
    if isinstance(data, dict):
        return {convert_func(k): convert_dict_keys(v, convert_func) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_dict_keys(item, convert_func) for item in data]
    else:
        return data

def extract_level(d, level):
    # print(level)
    if level == 0:
        return None
    if isinstance(d, dict):
        return {k: extract_level(v, level-1) for k, v in d.items()}
    return d

with open(r'jugem.vvproj', 'r', encoding="utf-8") as f:
    jugem = json.load(f)
    jugem_org = copy.deepcopy(jugem)

for ak in jugem['talk']['audioKeys']:
    query = jugem['talk']['audioItems'][ak]['query']
    text = jugem['talk']['audioItems'][ak]['text']
    print(f'ak = {ak}, text = {text}')
    if len(text) == 0:
        continue
    accent_phrases = {'accent_phrases' : query['accentPhrases']}
    accent_phrases = convert_dict_keys(accent_phrases, camel_to_snake)
    query.pop('accentPhrases')
    query.update(accent_phrases)
    # ここでqueryを書き換える
    query = MRT.make_rap(query)

    accent_phrases = {'accentPhrases' : query['accent_phrases']}
    accent_phrases = convert_dict_keys(accent_phrases, snake_to_camel)
    query.pop('accent_phrases')
    query.update(accent_phrases)
    
    jugem['talk']['audioItems'][ak]['query'] = query

# 深さ1までの要素を抽出
# for level in range(10):
#     print(f'level: {level}')
#     dictorg_levelx = extract_level(jugem_org, level)
#     dictnew_levelx = extract_level(jugem, level)

#     diff = DeepDiff(dictorg_levelx, dictnew_levelx)
#     print(json.dumps(diff, indent=2, ensure_ascii=False))
#     # if diff:
#     #     break

with open('new.vvproj', 'w', encoding='utf-8') as f:
    json.dump(jugem, f, ensure_ascii=False)
