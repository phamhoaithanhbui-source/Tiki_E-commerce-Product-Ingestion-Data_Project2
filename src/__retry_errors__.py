import os
import json
import asyncio
from fetcher import fetch_batch
from transformer import clean_description
from writer import write_success, write_error
from config import ERROR_DIR, BATCH_SIZE,  SLEEP_BETWEEN_BATCH, RETRY_SUCCESS_DIR, RETRY_ERROR_DIR

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


def collect_error_ids():
    error_ids = []

    for filename in os.listdir(ERROR_DIR):
        if filename.endswith(".json"):
            path = os.path.join(ERROR_DIR, filename)

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

                for item in data:
                    error_ids.append(item["id"])

    return list(set(error_ids))  # remove duplicates


async def retry_pipeline():

    print("Collecting error IDs...")
    ids = collect_error_ids()
    print(f"Total IDs to retry: {len(ids)}")

    batch_number = 1

    for start in range(0, len(ids), BATCH_SIZE):

        batch_ids = ids[start:start+BATCH_SIZE]
        print(f"Retrying batch {batch_number}")

        results = await fetch_batch(batch_ids)

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

        # Save successful retry
        if success_data:
            success_path = os.path.join(
                RETRY_SUCCESS_DIR,
                f"retry_success_{batch_number:03}.json"
            )
            with open(success_path, "w", encoding="utf-8") as f:
                json.dump(success_data, f, ensure_ascii=False)

        # Save failed retry
        if error_data:
            error_path = os.path.join(
                RETRY_ERROR_DIR,
                f"retry_error_{batch_number:03}.json"
            )
            with open(error_path, "w", encoding="utf-8") as f:
                json.dump(error_data, f, ensure_ascii=False)

        print(f"   --- Retry success: {len(success_data)}")
        print(f"   @@@ Still failed: {len(error_data)}")

        batch_number += 1

        # Exponential backoff between batch
        await asyncio.sleep(2)

    print("Retry process completed!")


if __name__ == "__main__":
    asyncio.run(retry_pipeline())