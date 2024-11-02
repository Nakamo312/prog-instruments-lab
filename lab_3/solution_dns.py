import os
from typing import List

from libs.dns_log_processor import (
    process_dns_logs,
    extract_unique_ip_addresses_dns_logs,
    extract_all_links_dns_logs,
    filter_time_dns_logs,
    filter_contains_dns_logs,
    filter_dns_logs,
    convert_rcv_snd_ru_dns_logs,
    convert_dates_dns_logs,
)


# Путь к исходному файлу логов
input_file = "input/dns.log"

# Папка для выходных файлов
output_dir = "output_dns"

input_file_process = os.path.join(output_dir, "process_dns_logs.log")

# Создаем папку, если она не существует
os.makedirs(output_dir, exist_ok=True)

# solution 1
# Обработка логов
process_dns_logs(
    input_file,
    input_file_process
)

# solution 2
extract_unique_ip_addresses_dns_logs(
    input_file_process,
    os.path.join(output_dir, "unique_ips.log")
)

# solution 3
extract_all_links_dns_logs(
    input_file_process,
    os.path.join(output_dir, "all_links.log")
)

# solution 4
# Пример фильтрации по времени
filter_time_dns_logs(
    input_file_process,
    os.path.join(output_dir, "filtered_time.log"),
    start_time="12.04.2023 20:00:57",
    end_time="12.04.2023 20:01:02",
)

# solution 5
# Пример фильтрации по наличию
filter_contains_dns_logs(
    input_file_process,
    os.path.join(output_dir, "filtered_contains.log"),
    contains=["AAAA"],
)

# solution 6
# Пример фильтрации по исключениям
filter_dns_logs(
    input_file_process,
    os.path.join(output_dir, "filtered_exclude.log"),
    exclude_strings=["A", "PTR"],
)

# solution 7
# Замена Snd и Rcv
convert_rcv_snd_ru_dns_logs(
    input_file_process,
    os.path.join(output_dir, "converted_rcv_snd.log")
)

# solution 8
# Конвертация дат
convert_dates_dns_logs(
    input_file_process,
    os.path.join(output_dir, "converted_dates.log")
)

print(f"Обработка завершена. Результаты сохранены в папке {output_dir}.")
