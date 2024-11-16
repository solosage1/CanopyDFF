# src/Functions/LeafPrice.py

def get_leaf_price(month: int) -> float:
    """
    Returns the LEAF price for the given month.
    Currently, it returns a fixed value of 1.0.

    Args:
        month (int): The current month in the simulation.

    Returns:
        float: The LEAF price.
    """
    return 1.0