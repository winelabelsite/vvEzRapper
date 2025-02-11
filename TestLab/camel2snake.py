import re

def camel_to_snake(name: str) -> str:
    if not name:
        return name
    prefix = re.match(r'^_+', name)
    prefix = prefix.group(0) if prefix else ''
    name = name[len(prefix):]  # プレフィックスを取り除く
    name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
    return prefix + name.lower()

def snake_to_camel(name: str) -> str:
    if not name:
        return name
    prefix = re.match(r'^_+', name)
    prefix = prefix.group(0) if prefix else ''
    if re.match(r'^_+\d', name):  # 先頭がアンスコ+数字の場合はそのまま返す
        return name
    name = name[len(prefix):]  # プレフィックスを取り除く
    name = re.sub(r'_([a-zA-Z])', lambda m: m.group(1).upper(), name)
    return prefix + name

# テストケース
examples = [
    "camelCaseExample",
    "snake_case_example",
    "_leadingUnderscore",
    "__double_leading_underscore",
    "_123numeric_prefix",
    "camelCaseWithNumbers123",
    "snake_case_with_numbers_123"
]

for example in examples:
    if '_' in example:
        print(f"{example} -> {snake_to_camel(example)}")
    else:
        print(f"{example} -> {camel_to_snake(example)}")
