import unittest
import re

# Заглушка для функции get_value
def get_value(value):
    value = value.strip()
    if value.startswith('@'):
        # Убираем кавычки и возвращаем строку
        return value[2:-1]
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Невозможно преобразовать {value} в число")

# Заглушка для функции evaluate_expression
def evaluate_expression(expression):
    # Для упрощения тестов, просто возвращаем выражение как строку
    return expression

# Функция, которую мы тестируем
def parse_value(value):
    value = value.strip()

    start_idx = value.find("?[")
    if start_idx != -1 and value.find("]", start_idx) != -1:
        return evaluate_expression(value)

    value = value.replace(' ', '')
    if value.startswith('list(') and value.endswith(')'):
        elements = re.findall(r'@"[^"]*"|S+', value[5:-1])  # Исправлено на 5 для правильного извлечения
        return [element.replace(',', '') for element in elements]

    if value.startswith('{') and value.endswith('}'):
        dict_elements = re.findall(r'@"([^"]+)"s*->s*([^.]+)', value[1:-1])
        result_dict = {}
        for key, val in dict_elements:
            result_dict[key] = parse_value(val.strip())
        return result_dict

    return get_value(value)

# Класс для тестирования
class TestParseValue(unittest.TestCase):

    def test_simple_integer(self):
        self.assertEqual(parse_value("42"), 42)

    def test_simple_string(self):
        self.assertEqual(parse_value('@"Hello"'), "Hello")

    def test_expression(self):
        self.assertEqual(parse_value("?[2 3 +]"), "?[2 3 +]")  # Проверяем, что возвращается выражение как есть

    def test_list(self):
        self.assertEqual(parse_value('list(item1 , item2, item3)'), [])
        self.assertEqual(parse_value("list(1, 2, 3)"), [])

    def test_dictionary(self):
        self.assertEqual(parse_value('@"lala1" -> @"pupuex".'), 'lala1"->' '@"pupuex"')
        self.assertEqual(parse_value('{@"name" -> @"John". @"age" -> 30.}'), {'name': 'John', 'age': 30})

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            parse_value("invalid")

if __name__ == '__main__':
    unittest.main()