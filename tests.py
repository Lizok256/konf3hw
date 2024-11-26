import unittest

# Предполагаем, что переменные определены где-то в коде
variables = {
    'var1': 42,
    'var2': 'Hello, World!'
}


def get_value(operand):
    """
    Возвращает значение переменной или преобразует операнд в число или строку.
    """
    # Проверка на число
    try:
        return int(operand)
    except ValueError:
        pass

    # Проверка на строку
    if operand.startswith('@"') and operand.endswith('"'):
        return operand[2:-1]  # Возвращаем строку без кавычек

    # Если это переменная, возвращаем ее значение
    if operand in variables:
        return variables[operand]

    raise SyntaxError(f"Неизвестный операнд: {operand}")


class TestGetValue(unittest.TestCase):

    def test_integer_conversion(self):
        self.assertEqual(get_value('100'), 100)
        self.assertEqual(get_value('-42'), -42)

    def test_string_conversion(self):
        self.assertEqual(get_value('@"Hello"'), 'Hello')
        self.assertEqual(get_value('@"Sample string"'), 'Sample string')

    def test_variable_value(self):
        self.assertEqual(get_value('var1'), 42)
        self.assertEqual(get_value('var2'), 'Hello, World!')

    def test_unknown_operand(self):
        with self.assertRaises(SyntaxError):
            get_value('unknown_var')

        with self.assertRaises(SyntaxError):
            get_value('123abc')  # Это не целое число и не переменная


# Запуск тестов
if __name__ == '__main__':
    unittest.main()