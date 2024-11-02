import os

from libs.access_log_processor import (
    sum_url_data,
    extract_unique_urls
)

# Путь к исходному файлу логов
input_file = "input/access.log"

# Папка для выходных файлов
output_dir = "output_access"

os.makedirs(output_dir, exist_ok=True)

# solution 9
# URL, который мы хотим проверить
url = "www.malware-traffic-analysis.net"
bytes_count = sum_url_data(input_file, url)

output_message = f"Общая сумма данных для URL '{url}': {bytes_count} байт\n"

output_file = os.path.join(output_dir, "sum_malware_traffic.txt")

# Записываем результат в файл
with open(output_file, "w", encoding="utf-8") as f:
    f.write(output_message)

# solution 10
# Взять все уникальные url с выгрузки
extract_unique_urls(
    input_file,
    os.path.join(output_dir, "extracted_urls.log")
)
