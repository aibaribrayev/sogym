import os
import csv
from config import ANIMALS_DATA, ORDER_DATA

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)


def save_order_to_csv(chat_id):
    order = ORDER_DATA[chat_id]
    animal_key = order["animal_key"]
    animal_name = ANIMALS_DATA[animal_key]["name"]
    file_name = f"data/{animal_name.replace(' ', '_').lower()}_orders.csv"
    file_exists = os.path.isfile(file_name)

    with open(file_name, "a", newline="") as csvfile:
        fieldnames = ["name", "phone", "address", "animal", "jiliks", "total_price"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()
        writer.writerow(
            {
                "name": order["name"],
                "phone": order["phone"],
                "address": order["address"],
                "animal": ANIMALS_DATA[order["animal_key"]]["name"],
                "jiliks": order["jiliks"],
                "total_price": order["total_price"],
            }
        )
