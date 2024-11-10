import argparse
from typing import Optional


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
    if from_unit == "граммы":
        if to_unit == "килограммы":
            return value / 1000
        elif to_unit == "фунты":
            return value * 0.00220462
        elif to_unit == "унции":
            return value * 0.035274
    elif from_unit == "килограммы":
        if to_unit == "граммы":
            return value * 1000
        elif to_unit == "фунты":
            return value * 2.20462
        elif to_unit == "унции":
            return value * 35.274
    elif from_unit == "фунты":
        if to_unit == "граммы":
            return value / 0.00220462
        elif to_unit == "килограммы":
            return value / 2.20462
        elif to_unit == "унции":
            return value * 16
    elif from_unit == "унции":
        if to_unit == "граммы":
            return value / 0.035274
        elif to_unit == "килограммы":
            return value / 35.274
        elif to_unit == "фунты":
            return value / 16
    return None


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
    if from_unit == "Цельсий":
        if to_unit == "Фаренгейт":
            return (value * 9 / 5) + 32
        elif to_unit == "Кельвин":
            return value + 273.15
    elif from_unit == "Фаренгейт":
        if to_unit == "Цельсий":
            return (value - 32) * 5 / 9
        elif to_unit == "Кельвин":
            return (value - 32) * 5 / 9 + 273.15
    elif from_unit == "Кельвин":
        if to_unit == "Цельсий":
            return value - 273.15
        elif to_unit == "Фаренгейт":
            return (value - 273.15) * 9 / 5 + 32
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
    conversion_factors = {
        "метры": 1,
        "километры": 1000,
        "мили": 1609.34,
        "футы": 0.3048,
    }

    if from_unit in conversion_factors and to_unit in conversion_factors:
        return value * (conversion_factors[from_unit] / conversion_factors[to_unit])

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
