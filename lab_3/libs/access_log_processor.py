import os
import re


def sum_url_data(log_file: str, url: str) -> int:
    """
    Суммирует общее количество байт, переданных от указанного URL в лог-файле.

    Функция открывает лог-файл, считывает его построчно и ищет строки, содержащие указанный URL.
    Для каждой найденной строки она извлекает количество переданных байт из 7-го столбца и
    суммирует эти значения.

    Аргументы:
        log_file (str): Путь к лог-файлу, содержащему данные о трафике.
        url (str): URL, для которого необходимо подсчитать общее количество переданных байт.

    Возвращает:
        int: Общее количество байт, переданных от указанного URL.
        Если файл не найден, выбрасывается исключение FileNotFoundError.
    """
    total_bytes = 0

    if not os.path.isfile(log_file):
        raise FileNotFoundError(f"Файл {log_file} не найден.")

    pattern = re.compile(re.escape(url))

    with open(log_file, "r") as file:
        for line in file:
            if pattern.search(line):
                parts = line.split()
                if len(parts) >= 8:
                    try:
                        bytes_transferred = int(parts[-7])
                        total_bytes += bytes_transferred
                    except ValueError:
                        raise ValueError(
                            f"Ошибка при преобразовании строки: {line.strip()}"
                        )

    return total_bytes


def extract_unique_urls(log_file: str, output_file: str) -> None:
    """
    Извлекает уникальные URL-адреса из лог-файла и записывает их в выходной файл.

    Аргументы:
        log_file (str): Путь к лог-файлу, содержащему данные о трафике.
        output_file (str): Путь к выходному файлу, в который будут записаны уникальные URL-адреса.

    Исключения:
        FileNotFoundError: Если лог-файл не найден.
        IOError: Если возникла ошибка при записи в выходной файл.
    """
    if not os.path.isfile(log_file):
        raise FileNotFoundError(f"Файл {log_file} не найден.")

    unique_urls = set()

    url_pattern = re.compile(r"CONNECT\s+([\w.-]+:\d+)")

    with open(log_file, "r") as file:
        for line in file:
            match = url_pattern.search(line)
            if match:
                matched_url = match.group(1)  # Извлекаем URL
                unique_urls.add(matched_url)  # Добавляем URL в множество

    try:
        with open(output_file, "w") as out_file:
            for url in unique_urls:
                out_file.write(url + "\n")
    except IOError as e:
        raise IOError(f"Ошибка при записи в файл {output_file}: {e}")
