import re

def camel_to_snake(name: str) -> str:
    """Convert CamelCase or camelCase to snake_case."""
    if name.startswith('_'):
        return '_' + camel_to_snake(name[1:])
    name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)  # Handle camelCase
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)  # Handle CamelCase
    return name.lower()

def snake_to_camel(name: str) -> str:
    """Convert snake_case to CamelCase."""
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

def convert_dict_keys(data, convert_func):
    """Recursively convert dictionary keys using the given function."""
    if isinstance(data, dict):
        return {convert_func(k): convert_dict_keys(v, convert_func) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_dict_keys(item, convert_func) for item in data]
    else:
        return data

# Test dictionary with CamelCase keys
test_data = {
    "UserName": "JohnDoe",
    "UserDetails": {
        "FirstName": "John",
        "LastName": "Doe",
        "Address": {
            "StreetName": "MainStreet",
            "PostalCode": "12345"
        }
    },
    "OrderList": [
        {"OrderId": 1, "ProductName": "Laptop"},
        {"OrderId": 2, "ProductName": "Mouse"}
    ],
    "MiscData": ["Item1", "Item2"],
    "_HiddenValue": "Secret",
    "_1NumericStart": "Value",
    "_000numeric_check": "TestValue"
}

# Convert CamelCase keys to snake_case
snake_case_data = convert_dict_keys(test_data, camel_to_snake)
print("Snake Case Data:", snake_case_data)

# Convert back to CamelCase
camel_case_data = convert_dict_keys(snake_case_data, snake_to_camel)
print("Camel Case Data:", camel_case_data)

# Unit tests
def test_camel_to_snake():
    print("Testing camel_to_snake...")
    print(camel_to_snake("CamelCase"))
    assert camel_to_snake("CamelCase") == "camel_case"
    print(camel_to_snake("camelCase"))
    assert camel_to_snake("camelCase") == "camel_case"
    print(camel_to_snake("_HiddenValue"))
    assert camel_to_snake("_HiddenValue") == "_hidden_value"
    print(camel_to_snake("_1NumericStart"))
    assert camel_to_snake("_1NumericStart") == "_1numeric_start"
    print(camel_to_snake("_000NumericCheck"))
    assert camel_to_snake("_000NumericCheck") == "_000_numeric_check"

def test_snake_to_camel():
    print("Testing snake_to_camel...")
    print(snake_to_camel("camel_case"))
    assert snake_to_camel("camel_case") == "CamelCase"
    print(snake_to_camel("_hidden_value"))
    assert snake_to_camel("_hidden_value") == "_HiddenValue"
    print(snake_to_camel("_1numeric_start"))
    assert snake_to_camel("_1numeric_start") == "_1NumericStart"
    print(snake_to_camel("_000_numeric_check"))
    assert snake_to_camel("_000_numeric_check") == "_000NumericCheck"

test_camel_to_snake()
test_snake_to_camel()
print("All tests passed!")
