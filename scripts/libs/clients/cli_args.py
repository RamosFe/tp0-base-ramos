import argparse


def check_if_positive(value):
    """
    Checks if a value is a positive number.

    Args:
        value: The value to check.

    Returns:
        int: The positive integer value.

    Raises:
        argparse.ArgumentTypeError: If the value is not a positive number.
    """
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError(f"The value {value} is not a positive number")
    return number


parser = argparse.ArgumentParser(description="Dynamic client builder")
parser.add_argument("clients", type=check_if_positive, help="A positive integer greater than 0 that represents the "
                                                            "number of clients to add")