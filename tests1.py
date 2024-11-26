import unittest
import re

# Предполагаем, что get_value реализована где-то в вашем коде.
def get_value(operand):
    # Пример реализации get_value для тестирования
    if operand.isdigit():
        return int(operand)
    elif operand.startswith('@'):
        return operand[2:-1]  # Убираем @" и "
    return operand

def evaluate_expression(expression):
    start_idx = expression.find("?[")
    end_idx = expression.find("]", start_idx)

    if start_idx == -1 or end_idx == -1:
        raise SyntaxError(f"Неверный синтаксис выражения: {expression}")
    content = expression[start_idx + 2:end_idx].strip()

    if not content:
        raise SyntaxError(f"Пустое выражение: {expression}")

    parts = re.findall(r'@"[^"]*"|\S+', content)
    if len(parts) < 2:
        raise SyntaxError(f"Неполное выражение: {expression}")

    operation = parts[-1]
    operands = parts[:-1]

    if operation == '+':
        return sum(get_value(operand) for operand in operands)
    elif operation == '-':
        result = get_value(operands[0])
        for operand in operands[1:]:
            result -= get_value(operand)
        return result
    elif operation == "len":
        if not isinstance(operands[0], str):
            raise SyntaxError('Недопустимый формат операнда функции len')

        str_tmp = get_value(operands[0])
        if not isinstance(str_tmp, str):
            raise SyntaxError('недопустимый формат операнда функции len')

        if str_tmp != 0:
            ret_value = len(get_value(operands[0]))
        else:
            o_len = len(operands[0])
            if o_len < 3:
                raise SyntaxError("неправильны йоперад для функции len")

            if operands[0][0] == '@' and operands[0][1] == '"' and operands[0][o_len-1] == '"':
                str_oper = operands[0][2:o_len-2]
                ret_value = len(str_oper)
            else:
                raise SyntaxError('Ошибка синтаксиса задания константной строки для функции len')
        return ret_value
    elif operation == 'pow':
        base = get_value(operands[0])
        exponent = get_value(operands[1])
        return base ** exponent
    else:
        raise SyntaxError(f"Неизвестная операция: {operation}")

class TestEvaluateExpression(unittest.TestCase):

    def test_addition(self):
        result = evaluate_expression("?[3 5 +]")
        self.assertEqual(result, 8)

    def test_subtraction(self):
        result = evaluate_expression("?[10 4 -]")
        self.assertEqual(result, 6)

    def test_length(self):
        result = evaluate_expression('?[@"Hello" len]')
        self.assertEqual(result, 5)

    def test_power(self):
        result = evaluate_expression("?[2 3 pow]")
        self.assertEqual(result, 8)

    """def test_invalid_syntax(self):
        with self.assertRaises(SyntaxError) as context:
            evaluate_expression("?[3 +]")
        self.assertEqual(str(context.exception), "Неполное выражение: ?[3 +]")"""

    def test_empty_expression(self):
        with self.assertRaises(SyntaxError) as context:
            evaluate_expression("?[ ]")
        self.assertEqual(str(context.exception), "Пустое выражение: ?[ ]")

    def test_unknown_operation(self):
        with self.assertRaises(SyntaxError) as context:
            evaluate_expression("?[3 4 unknown_op]")
        self.assertEqual(str(context.exception), "Неизвестная операция: unknown_op")

if __name__ == '__main__':
    unittest.main()