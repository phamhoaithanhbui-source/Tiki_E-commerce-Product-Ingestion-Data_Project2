import asyncio
import pandas as pd
import os
import time
from fetcher import fetch_batch
from src.config import SUCCESS_DIR
from transformer import clean_description
from writer import write_success, write_error
from config import (
    BATCH_SIZE,
    INPUT_FILE,
    SLEEP_BETWEEN_BATCH,
    SUCCESS_DIR
)


def transform_product(product):
    return {
        "id": product.get("id"),
        "name": product.get("name"),
        "url_key": product.get("url_key"),
        "price": product.get("price"),
        "description": clean_description(product.get("description", "")),
        "images": [
            img.get("base_url")
            for img in product.get("images", [])
            if img.get("base_url")
        ]
    }


async def process_batch(batch_ids, batch_number):
    print(f"Processing batch {batch_number}")
    print(f"   Batch size: {len(batch_ids)}")

    start_time = time.time()

    results = await fetch_batch(batch_ids)

    fetch_time = time.time() - start_time
    print(f"Fetch time: {fetch_time:.2f}s")

    success_data = []
    error_data = []

    for result in results:
        if result["success"]:
            transformed = transform_product(result["data"])
            success_data.append(transformed)
        else:
            error_data.append({
                "id": result["id"],
                "error": result["error"]
            })

    write_success(success_data, batch_number)
    write_error(error_data, batch_number)

    print(f"   --- Success: {len(success_data)}")
    print(f"   @@@ Failed: {len(error_data)}")

    #checkpoint
def batch_already_processed(batch_number):
    file_path = os.path.join(
    SUCCESS_DIR,
    f"products_{batch_number:03}.json"
    )
    return os.path.exists(file_path)


async def run_pipeline():
    print("Reading product IDs...")

    df = pd.read_csv("data/input/product_ids.csv")

    if "id" not in df.columns:
        raise ValueError("CSV must contain 'id' column")

    ids = df["id"].dropna().astype(int).tolist()

    print(f"Total IDs loaded: {len(ids)}")

    batch_number = 1

    for start in range(0, len(ids), BATCH_SIZE):
        batch_ids = ids[start:start + BATCH_SIZE]

        # RESUME LOGIC
        if batch_already_processed(batch_number):
            print(f"⏭ Skipping batch {batch_number} (already processed)")
            batch_number += 1
            continue

        await process_batch(batch_ids, batch_number)

        batch_number += 1

        # 1 mins break avoiding throttle
        await asyncio.sleep(0.5)

    print("Pipeline completed successfully!")

if __name__ == "__main__":
  asyncio.run(run_pipeline())

