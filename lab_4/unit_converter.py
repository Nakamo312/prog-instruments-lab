import argparse
from typing import Optional

from .consts import (
    conversion_factors_mass,
    conversion_functions_temperature,
    conversion_factors_length,
)


def convert_mass(value: float, from_unit: str, to_unit: str) -> Optional[float]:
    """
    Конвертация массы из одной единицы в другую.

    Parameters:
        value (float): Значение массы для конвертации.
        from_unit (str): Исходная единица измерения (граммы, килограммы, фунты, унции).
        to_unit (str): Единица измерения, в которую нужно конвертировать.

    Returns:
        Optional[float]: Конвертированное значение массы или None, если единицы измерения неверны.
    """

    if (
        from_unit not in conversion_factors_mass
        or to_unit not in conversion_factors_mass
    ):
        return None

    value_in_grams = value * conversion_factors_mass[from_unit]
    converted_value = value_in_grams / conversion_factors_mass[to_unit]

    return converted_value


def convert_temperature(value: float, from_unit: str, to_unit: str) -> Optional[float]:
    """
    Конвертация температуры из одной единицы в другую.

    Parameters:
        value (float): Значение температуры для конвертации.
        from_unit (str): Исходная единица измерения (Цельсий, Фаренгейт, Кельвин).
        to_unit (str): Единица измерения, в которую нужно конвертировать.

    Returns:
        Optional[float]: Конвертированное значение температуры или None, если единицы измерения неверны.
    """

    if (
        from_unit in conversion_functions_temperature
        and to_unit in conversion_functions_temperature[from_unit]
    ):
        return conversion_functions_temperature[from_unit][to_unit](value)

    return None


def convert_length(value: float, from_unit: str, to_unit: str) -> Optional[float]:
    """
    Конвертация длины из одной единицы в другую.

    Parameters:
        value (float): Значение длины для конвертации.
        from_unit (str): Исходная единица измерения (метры, километры, мили, футы).
        to_unit (str): Единица измерения, в которую нужно конвертировать.

    Returns:
        Optional[float]: Конвертированное значение длины или None, если единицы измерения неверны.
    """

    if from_unit in conversion_factors_length and to_unit in conversion_factors_length:
        return value * (
            conversion_factors_length[from_unit] / conversion_factors_length[to_unit]
        )

    return None


def main() -> None:
    """
    Основная функция, которая запускает конвертер единиц измерения.

    Обрабатывает аргументы командной строки и вызывает соответствующие функции конвертации.
    """
    parser = argparse.ArgumentParser(description="Конвертер единиц измерения.")
    parser.add_argument(
        "-unit",
        type=str,
        required=True,
        help="Исходная единица (граммы, килограммы, фунты, унции, Цельсий, Фаренгейт, Кельвин, метры, километры, мили, футы).",
    )
    parser.add_argument(
        "-translation",
        type=str,
        required=True,
        help="Единица для перевода (граммы, килограммы, фунты, унции, Цельсий, Фаренгейт, Кельвин, метры, километры, мили, футы).",
    )
    parser.add_argument("value", type=float, help="Числовое значение для конвертации.")

    args = parser.parse_args()

    # Определяем, какую функцию конвертации использовать
    if args.unit in ["граммы", "килограммы", "фунты", "унции"]:
        result = convert_mass(args.value, args.unit, args.translation)
    elif args.unit in ["Цельсий", "Фаренгейт", "Кельвин"]:
        result = convert_temperature(args.value, args.unit, args.translation)
    elif args.unit in ["метры", "километры", "мили", "футы"]:
        result = convert_length(args.value, args.unit, args.translation)
    else:
        result = None

    if result is not None:
        print("{} {} = {} {}".format(args.value, args.unit, result, args.translation))
    else:
        print("Ошибка: Неверные единицы измерения.")


if __name__ == "__main__":
    main()
