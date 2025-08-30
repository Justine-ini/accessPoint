from datetime import datetime
import random


def generate_order_number(pk, prefix="ORD", region="NG"):
    """
    Generates a unique order number string using a 
        prefix, region, current timestamp, primary key, and a random number.

    Args:
        pk (int or str): The primary key or unique identifier for the order.
        prefix (str, optional): The prefix to use for the order number. Defaults to "ORD".
        region (str, optional): The region code to include in the order number. Defaults to "NG".

    Returns:
        str: A unique order number in the format 
            '{PREFIX}-{REGION}-{YYYYMMDDHHMMSS}{pk}-{RANDOM6DIGITS}'.
    """
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = str(random.randint(100000, 999999))
    return f"{prefix.upper()}-{region.upper()}-{current_time}{pk}-{random_part}"
