def get_measurement(product_width) -> str:
    if product_width != "":
        width = float(product_width.replace(",", "."))
        if width < 50:
            return "дюймовая"
        return "метрическая"
    return ""
