import re
import sys
import xml.etree.ElementTree as ET

# Словарь для хранения глобальных переменных (констант)
variables = {}


# Функция для получения значения переменной или числа
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


# Функция для вычисления выражений в формате ?[операнд1 операнд2 операция]
def evaluate_expression(expression):
    """
    Вычисляет выражение вида ?{операция операнд1 операнд2}.
    """
    # Находим позиции символов ?[ и ]
    start_idx = expression.find("?[")  # Находим начало выражения
    end_idx = expression.find("]", start_idx)  # Находим конец выражения

    if start_idx == -1 or end_idx == -1:
        raise SyntaxError(f"Неверный синтаксис выражения: {expression}")

    # Извлекаем содержимое между ?[ и ]
    content = expression[start_idx + 2:end_idx].strip()

    if not content:
        raise SyntaxError(f"Пустое выражение: {expression}")

    # Разделяем строку по пробелам, при этом строки в кавычках не будут разделяться
    parts = re.findall(r'@"[^"]*"|\S+', content)
    if len(parts) < 2:
        raise SyntaxError(f"Неполное выражение: {expression}")

    operation = parts[-1]
    operands = parts[:-1]

    # Проверяем операцию
    if operation == '+':  # Сложение чисел
        return sum(get_value(operand) for operand in operands)
    elif operation == '-':
        result = get_value(operands[0])
        for operand in operands[1:]:
            result -= get_value(operand)
        return result
    elif operation == "len":
        #gen = (str(operand) for operand in operands)
        #lst = list(gen)
        if not isinstance( operands[0], str ):
            # if not string --> poka poka
            raise  SyntaxError ('Недопустимый формат операнда функции len')

        str_tmp = get_value(operands[0])
        if  not isinstance( str_tmp, str):
            raise SyntaxError ('недопустимый формат операнда функции len')

        if ( str_tmp != 0 ):
            ret_value = len(get_value(operands[0]))
        else:
            o_len = len (operands[0])
            if o_len <3 :
                raise SyntaxError ("неправильны йоперад для функции len")

            if operands[0][0] == '@' and operands[0][1] == '"' and operandsp[0][o_len-1] == '"':
                str_oper = operands[0][2:o_len-2]
                ret_value = len (str_oper)
            else:
                raise  SyntaxError ('Ошибка синтаксиса задания константной строки для функции len')
        return  ret_value
    elif operation == 'pow':  # Конкатенация строк
        base = get_value(operands[0])
        exponent = get_value(operands[1])
        return base ** exponent
    else:
        raise SyntaxError(f"Неизвестная операция: {operation}")


# Функция для обработки значений (массивы, строки и выражения)
def parse_value(value):
    """
    Обрабатывает значение: массивы, строки и выражения.
    """
    value = value.strip()

    # Проверяем, является ли это выражением
    start_idx = value.find("?[")  # Ищем начало выражения
    if start_idx != -1 and value.find("]", start_idx) != -1:  # Если есть ?
        return evaluate_expression(value)

    # Если это массив, обрабатываем его элементы, но не вычисляем
    value.replace(' ','')
    if value.startswith('list(') and value.endswith(')'):  # Если это массив
        elements = re.findall(r'@"[^"]*"|\S+', value[1:-1])  # Разделяем элементы массива

        elll = elements[1:]
        i=0
        for ee in elll:
            elll[i]=ee.replace(',', '')
            i = i+1

        return elll  # Просто возвращаем элементы массива, не вычисляя их

     # Если это словарь в формате [имя => значение, имя => значение, ...]
    if value.startswith('{') and value.endswith('}'):
        # Извлекаем пары ключ-значение
        dict_elements = re.findall(r'@"([^"]+)"\s*->\s*([^.]+)', value[1:-1])  # Пары ключ-значение!!!!!!!
        result_dict = {}
        for key, val in dict_elements:
            result_dict[key] = parse_value(val.strip())  # Рекурсивно обрабатываем значение
        return result_dict
    # Для всего остального — проверяем как простое значение
    return get_value(value)

# Функция для обработки многострочных комментариев
def remove_multiline_comments(config_text):
    """
    Удаляет многострочные комментарии в формате #= ... =#.
    """
    pattern = r'#=\s*(.*?)\s*=#'  # Регулярное выражение для поиска многострочных комментариев
    return re.sub(pattern, '', config_text, flags=re.DOTALL)

# Функция для обработки конфигурационного текста
def process_config(config_text):
    """
    Обрабатывает строки конфигурации.
    """
    # Убираем многострочные комментарии
    config_text = remove_multiline_comments(config_text)

    global variables  # Используем глобальные переменные

    for line in config_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue  # Пропускаем пустые строки


        # Обрабатываем объявление константы
        if 'is' in line and 'list' not in line:
            parts = line.split(" is ")
            if len(parts) != 2:
                raise SyntaxError(f"Неверный синтаксис константы: {line}")
            name, value = parts
            if bool(re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', name)):
                variables[name] = parse_value(value)
            else:
                raise SyntaxError(f"Неверное имя для константы: {line}")



        # Обрабатываем присваивание значения переменной
        else:
            parts = line.split(" = ", 1)
            if len(parts) == 2:
                name, value = parts
                name = name.strip()
                value = value.strip()
            else:
                # Обработайте случай, когда строка не соответствует ожидаемому формату
                print(f"Неверный формат строки: {line}")
                return  # или выполните другую обработку ошибки

            variables[name] = parse_value(value)  # Сохраняем результат в обычные переменные



# Функция для записи результата в XML-файл
# Функция для записи результата в XML-файл
def write_to_xml(output_file, data):
    """
    Записывает данные в XML-файл.
    """
    def add_value_to_element(parent, key, value):
        """
        Добавляет значение переменной в XML-элемент.
        """
        var_element = ET.SubElement(parent, "variable", name=key)
        if isinstance(value, dict):  # Если значение — словарь
            for sub_key, sub_value in value.items():
                sub_element = ET.SubElement(var_element, "item", key=sub_key)
                sub_element.text = str(sub_value)
        elif isinstance(value, list):  # Если значение — список
            for item in value:
                item_element = ET.SubElement(var_element, "item")
                item_element.text = str(item)
        else:  # Обычное значение
            var_element.text = str(value)

    # Создаём корневой элемент
    root = ET.Element("variables")

    # Добавляем переменные в корневой элемент
    for key, value in data.items():
        add_value_to_element(root, key, value)

    # Записываем дерево XML в файл
    tree = ET.ElementTree(root)
    ET.indent(tree, ' ')
    tree.write(output_file, encoding="utf-8", xml_declaration=True, method="xml",)


# Основная функция
def main():
    # Проверка аргументов командной строки
    if len(sys.argv) < 3:
        print("Ошибка: не указан путь к выходному файлу")
        sys.exit(1)

    # Путь к выходному файлу
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Печатаем инструкции для пользователя
    #print("Введите конфигурацию. Для завершения ввода используйте Ctrl+D (или Ctrl+Z на Windows).")

    # Считываем конфигурацию с ввода
    # Чтение конфигурации из файла
    with open(input_file, 'r', encoding='utf-8') as file:
        config_text = file.read()

    # Обрабатываем конфигурацию
    process_config(config_text)

    # Записываем результат в файл в формате XML
    write_to_xml(output_file, variables)

    print(f"Результат записан в файл: {output_file}")


if __name__ == "__main__":
    main()

