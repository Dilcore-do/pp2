import re
import json


def clean_price(price_str):
    """
    Convert price string like '1 200,00' to float 1200.00
    """
    price_str = price_str.replace(" ", "").replace(",", ".")
    return float(price_str)


def parse_receipt(text):
    data = {}

    # 1. Extract all prices

    price_pattern = r'\b\d{1,3}(?: \d{3})*,\d{2}\b'
    all_prices_raw = re.findall(price_pattern, text)

    # Convert to float
    all_prices = [clean_price(p) for p in all_prices_raw]
    data["all_prices"] = all_prices

    # 2. Extract product names

    product_pattern = r'\d+\.\n(.+?)\n\d+,\d{3} x'
    products = re.findall(product_pattern, text)
    data["products"] = [p.strip() for p in products]

    # 3. Extract TOTAL amount

    total_pattern = r'ИТОГО:\n([\d ]+,\d{2})'
    total_match = re.search(total_pattern, text)
    if total_match:
        data["total_amount"] = clean_price(total_match.group(1))
    else:
        data["total_amount"] = None

    # 4. Extract date and time

    datetime_pattern = r'Время:\s*(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})'
    datetime_match = re.search(datetime_pattern, text)
    if datetime_match:
        data["datetime"] = datetime_match.group(1)
    else:
        data["datetime"] = None

    # 5. Extract payment method

    payment_pattern = r'(Банковская карта|Наличные)'
    payment_match = re.search(payment_pattern, text)
    if payment_match:
        data["payment_method"] = payment_match.group(1)
    else:
        data["payment_method"] = "Unknown"

    return data


def main():
    with open("raw.txt", "r", encoding="utf-8") as f:
        receipt_text = f.read()

    parsed_data = parse_receipt(receipt_text)

    print(json.dumps(parsed_data, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()