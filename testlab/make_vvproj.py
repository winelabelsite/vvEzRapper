import copy
import json
import re
from deepdiff import DeepDiff

def camel_to_snake(name: str) -> str:
    """Convert CamelCase or camelCase to snake_case."""
    if name.startswith('_'):
        return '_' + camel_to_snake(name[1:])
    name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)  # Handle camelCase
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)  # Handle CamelCase
    return name.lower()

def snake_to_pascal(name: str) -> str:
    """Convert snake_case to camelCase."""
    if name.startswith('_'):
        parts = name[1:].split('_')
        if parts[0].isdigit():
            numeric_prefix = parts[0]
            rest = [parts[1]] + [word.capitalize() for word in parts[2:]] if len(parts) > 1 else []
            return '_' + numeric_prefix + ''.join(rest)
        else:
            converted = [word.capitalize() for word in parts]
        return '_' + ''.join(converted)
    return ''.join(word.capitalize() for word in name.split('_'))

def snake_to_camel(name: str) -> str:
    """Convert snake_case to PascallCase."""
    pascal = snake_to_pascal(name)
    print(pascal)
    camel = pascal[0].lower() + pascal[1:]
    return camel


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

with open(r'jugem_processed.json', 'r', encoding="utf-8") as f:
    jugem = json.load(f)
    jugem_org = copy.deepcopy(jugem)

for ak in jugem['talk']['audioKeys']:
    # print(ak)
    query = jugem['talk']['audioItems'][ak]['query']
    # query書き替える
    snake_query = convert_dict_keys(query, camel_to_snake)
    # print(json.dumps(snake_query, indent=2))
    # camel_query = convert_dict_keys(query, snake_to_camel)
    # print(json.dumps(camel_query, indent=2))
    
    jugem['talk']['audioItems'][ak]['query'] = snake_query

# 深さ1までの要素を抽出
level = 5
dictorg_levelx = extract_level(jugem_org, level)
dictnew_levelx = extract_level(jugem, level)

diff = DeepDiff(dictorg_levelx, dictnew_levelx)
print(json.dumps(diff, indent=2, ensure_ascii=False))
# with open('diff.json', 'w', encoding='utf-8') as f:
#     json.dump(diff, f, ensure_ascii=False)
