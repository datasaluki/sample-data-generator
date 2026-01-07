import csv
import logging
import logging.config
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Sequence

from faker import Faker

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_PATH = Path(__file__).parent / "target"


@dataclass
class Product:
    name: str
    price: float


def write_to_csv(file_name: str, rows: Sequence[dict[str, Any]]) -> None:
    file_path = OUTPUT_PATH / file_name

    if len(rows) == 0:
        return

    field_names = rows[0].keys()

    with open(file_path, "w") as f:
        wtr = csv.DictWriter(f, field_names)
        wtr.writeheader()
        wtr.writerows(rows)


def write_list_to_csv(file_name: str, field_name: str, values: Sequence[str]) -> None:
    rows = [{"id": i + 1, field_name: item} for i, item in enumerate(values)]
    write_to_csv(file_name, rows)


def generate_shipping_methods() -> int:
    methods = ["Standard", "Next Business Day", "Saturday AM", "Saturday PM"]

    write_list_to_csv("shipping_method.csv", "name", methods)

    return len(methods)


def generate_couriers() -> int:
    couriers = [
        "Cheap & Cheerful Delivery",
        "Speedy Parcel Delivery",
        "Local Delivery Partners",
    ]
    write_list_to_csv(
        "courier.csv",
        "name",
        couriers,
    )

    return len(couriers)


def generate_customers(number_of_customers: int) -> None:
    faker = Faker()

    customers = []
    for i in range(0, number_of_customers):
        customers.append(
            {"id": i + 1, "city": faker.city(), "country": faker.country()}
        )

    write_to_csv("customer.csv", customers)


def get_product_hierarchy() -> dict[str, dict[str, Sequence[Product]]]:
    return {
        "Home & Garden": {
            "Garden Furniture": [
                Product("Table and chair set", 299.99),
                Product("Patio Heater", 199.99),
            ],
            "Home Furnishing": [
                Product("Curtains", 89.99),
                Product("Cushions", 19.99),
            ],
        },
        "Electronics": {
            "TV": [
                Product("50 inch 4K TV", 399.99),
                Product("TV Soundbar", 99.99),
            ],
            "Audio": [
                Product("Portable Bluetooth Speaker", 49.99),
                Product("Premium Smart Speaker", 399.99),
            ],
        },
        "Clothing": {
            "Menswear": [Product("Mens Jeans", 39.99), Product("Mens Shorts", 19.99)],
            "Womenswear": [Product("Womens Jeans", 39.99), Product("Blouse", 24.99)],
        },
    }


def generate_products() -> int:
    product_hierarchy = get_product_hierarchy()

    category_id = 1
    sub_category_id = 1
    product_id = 1

    categories = []
    sub_categories = []
    products = []

    for category_name, sub_category in product_hierarchy.items():
        categories.append({"id": category_id, "name": category_name})
        for sub_category_name, product_set in sub_category.items():
            sub_categories.append(
                {
                    "id": sub_category_id,
                    "category_id": category_id,
                    "name": sub_category_name,
                }
            )
            for product in product_set:
                products.append(
                    {
                        "id": product_id,
                        "sub_category_id": sub_category_id,
                        "name": product.name,
                        "price": product.price,
                    }
                )
                product_id += 1

            sub_category_id += 1

        category_id += 1

    write_to_csv("category.csv", categories)
    write_to_csv("sub_category.csv", sub_categories)
    write_to_csv("product.csv", products)

    return len(products)


def generate_orders(
    num_customers: int,
    num_products: int,
    num_shipping_methods: int,
    num_couriers: int,
    num_orders: int = 100,
    max_order_items: int = 3,
    start_datetime: datetime = datetime(2025, 1, 1),
    end_datetime: datetime = datetime(2026, 1, 1),
    max_quantity: int = 3,
) -> None:
    orders: list[dict[str, Any]] = []
    order_items: list[dict[str, Any]] = []

    fake = Faker()

    order_item_id = 1
    for i in range(0, num_orders):
        order_id = i + 1
        placed_timestamp = fake.date_time_between(start_datetime, end_datetime)
        shipped_timestamp = placed_timestamp + timedelta(days=fake.random_int(1, 4))
        orders.append(
            {
                "id": order_id,
                "customer_id": fake.random_int(1, num_customers),
                "shipping_method_id": fake.random_int(1, num_shipping_methods),
                "courier_id": fake.random_int(1, num_couriers),
                "placed_timestamp": placed_timestamp,
                "shipped_timestamp": shipped_timestamp,
            }
        )

        for j in range(0, fake.random_int(1, max_order_items)):
            order_items.append(
                {
                    "id": order_item_id,
                    "order_id": order_id,
                    "product_id": fake.random_int(1, num_products),
                    "quantity": fake.random_int(1, max_quantity),
                }
            )
            order_item_id += 1

    write_to_csv("order.csv", orders)
    write_to_csv("order_item.csv", order_items)


def main() -> None:
    logger.info(f"Creating clean output path at '{OUTPUT_PATH}'")
    if OUTPUT_PATH.exists():
        shutil.rmtree(OUTPUT_PATH)

    OUTPUT_PATH.mkdir()

    num_customers = 10
    num_orders = 100
    max_order_items = 3
    max_quantity = 2

    logger.info("Generating shipping methods")

    num_shipping_methods = generate_shipping_methods()
    num_couriers = generate_couriers()
    num_customers = generate_customers(num_customers)
    num_products = generate_products()

    logger.info("Generating orders")
    generate_orders(
        max_quantity,
        num_products,
        num_shipping_methods,
        num_couriers,
        num_orders,
        max_order_items,
    )

    logger.info("Generation complete.")


if __name__ == "__main__":
    main()
