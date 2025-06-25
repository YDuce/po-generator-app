from enum import Enum, unique


@unique
class OrderStatus(str, Enum):
    NEW = "new"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"
