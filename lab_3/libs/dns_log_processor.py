import re
from typing import List


def process_dns_logs(input_file: str, output_file: str) -> None:
    """
    Обрабатывает DNS лог-файл, фильтруя ненужные строки и удаляя префиксы.

    Эта функция читает входной файл, ищет строки, содержащие информацию о получении (Rcv)
    и отправке (Snd) пакетов, и записывает очищенные строки в выходной файл.

    Аргументы:
    ----------
        input_file (str): Путь к входному лог-файлу, который будет обработан.
        output_file (str): Путь к выходному лог-файлу, в который будут записаны обработанные данные.

    Возвращает:
    ----------
    None
        Функция ничего не возвращает, но создает выходной файл с обработанными данными.
    """
    pattern = r"^\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2} .*?"

    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            if re.search(pattern, line):
                outfile.write(line)


def extract_unique_ip_addresses_dns_logs(input_file: str, output_file: str) -> None:
    """
    Извлекает уникальные IP-адреса из файла логов и записывает их в выходной файл.

    Аргументы:
        input_file (str): Путь к входному файлу, содержащему логи.
        output_file (str): Путь к выходному файлу, в который будут записаны найденные IP-адреса.

    Возвращает:
        None: Функция не возвращает значения, но создает или перезаписывает выходной файл с IP-адресами.
    """
    ip_pattern = r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
    unique_ips = set()

    with open(input_file, "r") as f_in:
        for line in f_in:
            found_ips = re.findall(ip_pattern, line)
            unique_ips.update(found_ips)

    with open(output_file, "w") as f_out:
        for ip in sorted(unique_ips):
            f_out.write(ip + "\n")


def extract_all_links_dns_logs(input_file: str, output_file: str) -> None:
    """
    Извлекает DNS имена из логов и преобразует их в правильный формат,
    заменяя числовые обозначения на точки.

    Аргументы:
        input_file (str): Путь к входному файлу, содержащему логи.
        output_file (str): Путь к выходному файлу, в который будут записаны извлеченные DNS имена.

    Возвращает:
        None: Функция не возвращает значений, но создает или перезаписывает выходной файл с извлеченными DNS именами.
    """

    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            dns_name_parts = re.findall(r"\((\d+)\)([a-zA-Z0-9-]+)", line)
            if dns_name_parts:
                dns_name = ".".join(part[1] for part in dns_name_parts)
                outfile.write(dns_name + "\n")


def filter_time_dns_logs(
    input_file: str, output_file: str, start_time: str, end_time: str
) -> None:
    """
    Фильтрует строки из входного файла по заданному диапазону времени и записывает
    отфильтрованные строки в выходной файл.

    Аргументы:
        input_file (str): Путь к входному файлу, содержащему логи.
        output_file (str): Путь к выходному файлу, в который будут записаны отфильтрованные строки.
        start_time (str): Начальное время (в формате 'DD.MM.YYYY HH:MM:SS') для фильтрации.
        end_time (str): Конечное время (в формате 'DD.MM.YYYY HH:MM:SS') для фильтрации.

    Возвращает:
        None: Функция не возвращает значений, но создает или перезаписывает выходной файл с отфильтрованными строками.
    """
    with open(output_file, "w") as output_file_handle:
        with open(input_file, "r") as input_file_handle:
            for line in input_file_handle:
                match = re.match(r"(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})", line)
                if match:
                    timestamp = match.group(1)
                    if start_time <= timestamp <= end_time:
                        output_file_handle.write(line)


def filter_contains_dns_logs(
    input_file: str, output_file: str, contains: List[str]
) -> None:
    """
    Фильтрует строки из входного файла логов по заданным наличию в строке из списка по шаблону.

    Аргументы:
        input_file (str): Путь к входному файлу, содержащему логи.
        output_file (str): Путь к выходному файлу, в который будут записаны отфильтрованные строки.
        contains (List[str]): Список того, что может находиться для фильтрации (например, ['A', 'PTR']).

    Возвращает:
        None: Функция не возвращает значений, но создает или перезаписывает выходной файл с отфильтрованными строками.
    """

    contains_pattern = "|".join(contains)
    regex_pattern = rf"\s({contains_pattern})\s"

    with open(output_file, "w") as outfile:
        with open(input_file, "r") as infile:
            for line in infile:
                if re.search(regex_pattern, line):
                    outfile.write(line)


def filter_dns_logs(input_file: str, output_file: str, exclude_strings: List[str]):
    """
    Фильтрует строки из входного файла, исключая те, которые содержат указанные подстроки.

    Функция открывает входной файл, считывает его построчно и записывает в выходной файл
    только те строки, которые не содержат ни одной из подстрок из списка исключений.

    Аргументы:
        input_file (str): Путь к входному файлу, который нужно фильтровать.
        output_file (str): Путь к выходному файлу, в который будут записаны отфильтрованные строки.
        exclude_strings (List[str]): Список строк, которые нужно исключить из выходного файла.

    Возвращает:
        None: Функция не возвращает значений, но создает или перезаписывает выходной файл
    с отфильтрованными строками.
    """
    exclude_pattern = "|".join(exclude_strings)
    regex_pattern = rf"\s({exclude_pattern})\s"

    with open(output_file, "w") as outfile:
        with open(input_file, "r") as infile:
            for line in infile:
                if not re.search(regex_pattern, line):
                    outfile.write(line)


def convert_rcv_snd_ru_dns_logs(input_file: str, output_file: str) -> None:
    """
    Заменяет в строках входного файла слова "Snd" и "Rcv" на "Отп" и "Пол" соответственно.

    Функция открывает входной файл, считывает его построчно, заменяет в каждой строке
    вхождения слов "Snd" и "Rcv" на их русские эквиваленты "Отп" и "Пол",
    а затем записывает измененные строки в выходной файл.

    Аргументы:
        input_file (str): Путь к входному файлу, содержащему текст для обработки.
        output_file (str): Путь к выходному файлу, в который будут записаны измененные строки.

    Возвращает:
        None: Функция не возвращает значений, но создает или перезаписывает выходной файл с измененными строками.
    """
    with open(input_file, "r", encoding="utf-8") as infile, open(
        output_file, "w", encoding="utf-8"
    ) as outfile:
        for line in infile:
            line = re.sub(r"\bSnd\b", "Отп", line)
            line = re.sub(r"\bRcv\b", "Пол", line)
            outfile.write(line)


def convert_dates_dns_logs(input_file: str, output_file: str) -> None:
    """
    Изменяет формат даты в строках входного файла на формат 'MMM DD YYYY HH:MM:SS'.

    Функция открывает входной файл, считывает его построчно, заменяет в каждой строке
    даты формата 'DD.MM.YYYY' на 'MMM DD YYYY' и записывает измененные строки в выходной файл.

    Аргументы:
        input_file (str): Путь к входному файлу, содержащему текст для обработки.
        output_file (str): Путь к выходному файлу, в который будут записаны измененные строки.

    Возвращает:
        None: Функция не возвращает значений, но создает или перезаписывает выходной файл с измененными строками.
    """
    month_map = {
        "01": "Jan",
        "02": "Feb",
        "03": "Mar",
        "04": "Apr",
        "05": "May",
        "06": "Jun",
        "07": "Jul",
        "08": "Aug",
        "09": "Sep",
        "10": "Oct",
        "11": "Nov",
        "12": "Dec",
    }

    date_pattern = r"(\d{2})\.(\d{2})\.(\d{4}) (\d{2}:\d{2}:\d{2})"

    with open(input_file, "r", encoding="utf-8") as infile, open(
        output_file, "w", encoding="utf-8"
    ) as outfile:
        for line in infile:
            line = re.sub(
                date_pattern,
                lambda m: f"{month_map[m.group(2)]} {m.group(1)} {m.group(3)} {m.group(4)}",
                line,
            )
            outfile.write(line)
