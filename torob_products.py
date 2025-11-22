import pandas as pd
import requests
import aiohttp
import asyncio
import csv
import os
from tqdm.asyncio import tqdm

pd.set_option('display.max_columns', None)

def get_last_processed_batch(final_filename):
    """Determine the last successfully processed batch by checking the final CSV file."""
    if not os.path.exists(final_filename):
        return 0
    
    try:
        df = pd.read_csv(final_filename)
        if len(df) == 0:
            return 0
        
        # Calculate how many complete batches we have
        batch_size = 5000
        completed_rows = len(df)
        completed_batches = completed_rows // batch_size
        
        print(f"Found {completed_rows} rows in existing file")
        print(f"This represents {completed_batches} complete batches")
        
        return completed_batches
    except Exception as e:
        print(f"Error reading existing file: {e}")
        return 0

shops = pd.read_csv('torob_shops.csv')
print(f"Loaded {len(shops)} shops")

products_url = 'https://api.torob.com/v4/internet-shop/base-product/list/?shop_id={shop_id}&&page={page}&size=30000&source=next_desktop'

shop_info_url = 'https://api.torob.com/v4/internet-shop/details/?id={shop_id}&source=next_desktop'

async def fetch_shop_info(session, shop_id, semaphore):
    async with semaphore:  # Limit concurrent requests
        url = shop_info_url.format(shop_id=shop_id)
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8,fa;q=0.7',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'referer': 'https://api.torob.com/v4/internet-shop/base-product/list/?shop_id=47587&&page=5&size=30000&source=next_desktop',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        cookies = {
            'search_session': 'xvyfejzduucnvttomwxoemzkeqjuohob',
            'new_question_bucket': '0.083029',
            'display_mode': '',
            'new_question_visibility': 'false',
            'is_torob_user_logged_in': 'False',
            'trb_clearance': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTQ2OTU0MzMsIm5iZiI6MTc1NDY5MzYzMywic3ViIjoiYzZkZTZhZWYxNDkxZGFjOWUzOGI5MzdhMDMwMjZjMTRhZTY5ZGU1OGRkZDdkZjQ2MTM5NmJlYjIxYzIyNmJmMyJ9.n9j1BubYXALuch2JseTVk2F6RYzv87oaMtMHCaBCJu8'
        }
        try:
            # Add small random delay to avoid overwhelming the server
            await asyncio.sleep(0.05)  # 50ms delay
            
            async with session.get(url, headers=headers, cookies=cookies) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Failed to fetch shop {shop_id}: HTTP {response.status}")
                    return None
        except Exception as e:
            print(f"Error fetching shop {shop_id}: {e}")
            return None

def flatten_shop_info(shop_info):
    """Flatten the nested shop_info JSON into a flat dictionary."""
    flattened = {
        "id": shop_info.get("id"),
        "name": shop_info.get("name"),
        "domain": shop_info.get("domain"),
        "block_partner": shop_info.get("block_partner"),
        "block_description": shop_info.get("block_description"),
        "shop_logo": shop_info.get("shop_logo"),
        "is_marketplace": shop_info.get("is_marketplace"),
        "enamad_expire_date": shop_info.get("enamad_expire_date"),
        "enamad_level": shop_info.get("enamad_level"),
        "province": shop_info.get("province"),
        "city": shop_info.get("city"),
        "address": shop_info.get("address"),
        "phone": shop_info.get("phone"),
        "second_phone": shop_info.get("second_phone"),
        "last_updated": shop_info.get("last_updated"),
        "active_time": shop_info.get("active_time"),
        "shop_type": shop_info.get("shop_type"),
        "shop_score": shop_info.get("shop_score"),
        "date_added": shop_info.get("date_added"),
        "upvotes": shop_info.get("upvotes"),
        "downvotes": shop_info.get("downvotes"),
        "score_percentile": shop_info.get("score_percentile"),
    }

    # Extract additional_infos
    if shop_info.get("additional_infos"):
        for info in shop_info["additional_infos"]:
            flattened[f"additional_info_{info['title']}"] = info.get("text", "")

    # Extract customer_support_info
    if shop_info.get("customer_support_info"):
        support_info = shop_info["customer_support_info"]
        flattened["customer_support_schedule"] = support_info.get("schedule", "")
        flattened["customer_support_more_info"] = support_info.get("more_info", "")
        if support_info.get("phones"):
            flattened["customer_support_phone"] = support_info["phones"][0].get("number", "")
        if support_info.get("emails"):
            flattened["customer_support_email"] = support_info["emails"][0].get("email", "")

    # Extract delivery_info
    if shop_info.get("delivery_info"):
        delivery_info = shop_info["delivery_info"]
        more_info = delivery_info.get("more_info")
        flattened["delivery_more_info"] = more_info.get("text", "") if more_info else ""
        if delivery_info.get("items"):
            flattened["delivery_items"] = ", ".join(delivery_info["items"])

    # Extract payment_info
    if shop_info.get("payment_info"):
        payment_info = shop_info["payment_info"]
        if payment_info.get("items"):
            flattened["payment_methods"] = ", ".join(payment_info["items"])

    return flattened

def save_batch_to_csv(batch_shop_infos, batch_num, final_filename):
    """Save batch data to a temporary CSV file."""
    if not batch_shop_infos:
        return
    
    # Collect all possible fieldnames from this batch
    all_fieldnames = set()
    for shop_info in batch_shop_infos:
        all_fieldnames.update(shop_info.keys())
    
    fieldnames = sorted(all_fieldnames)
    batch_filename = f"shopinfo_batch_{batch_num}.csv"
    
    # Write batch to temporary file
    with open(batch_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(batch_shop_infos)
    
    print(f"Saved batch {batch_num} to {batch_filename}")
    
    # Append to final file
    append_to_final_csv(batch_filename, final_filename)
    
    # Remove temporary batch file
    os.remove(batch_filename)

def append_to_final_csv(batch_filename, final_filename):
    """Append batch CSV to the final CSV file."""
    # Read the batch file
    batch_df = pd.read_csv(batch_filename)
    
    # Check if final file exists
    if os.path.exists(final_filename):
        # Read existing final file and append
        existing_df = pd.read_csv(final_filename)
        combined_df = pd.concat([existing_df, batch_df], ignore_index=True, sort=False)
    else:
        combined_df = batch_df
    
    # Save combined data
    combined_df.to_csv(final_filename, index=False, encoding='utf-8')

async def main():
    # Process shops in batches to avoid overwhelming the API
    batch_size = 5000  # Reduce batch size for better memory management
    concurrent_requests = 50  # Limit concurrent requests
    total_shops = len(shops)
    final_filename = './shopinfo_detail.csv'
    
    print(f"Total shops to process: {total_shops}")
    print(f"Concurrent requests limit: {concurrent_requests}")
    
    # Check for existing progress and determine where to resume
    last_completed_batch = get_last_processed_batch(final_filename)
    start_batch = last_completed_batch
    start_shop_index = start_batch * batch_size
    
    if start_shop_index > 0:
        print(f"Resuming from batch {start_batch + 1} (shop index {start_shop_index + 1})")
    else:
        print("Starting from the beginning")
        # Remove existing final file if starting fresh
        if os.path.exists(final_filename):
            os.remove(final_filename)
            print(f"Removed existing {final_filename}")
    
    total_successful_fetches = 0
    
    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(concurrent_requests)
    
    # Configure session with connection limits
    connector = aiohttp.TCPConnector(limit=50, limit_per_host=25)
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # Skip the test if resuming
        if start_shop_index == 0:
            # Test with just one shop ID first
            test_shop_id = shops.iloc[0]['id']
            print(f"Testing with shop ID: {test_shop_id}")
            
            shop_info = await fetch_shop_info(session, test_shop_id, semaphore)
            if shop_info:
                print("Successfully fetched shop info!")
                print(f"Shop name: {shop_info.get('name', 'Unknown')}")
            else:
                print("Failed to fetch shop info - stopping execution")
                return
        
        # Process shops in batches starting from the resume point
        for batch_start in range(start_shop_index, total_shops, batch_size):
            batch_end = min(batch_start + batch_size, total_shops)
            batch_shops = shops.iloc[batch_start:batch_end]
            batch_num = batch_start//batch_size + 1
            
            print(f"\nProcessing batch {batch_num}/{(total_shops + batch_size - 1)//batch_size}")
            print(f"Shops {batch_start + 1} to {batch_end} of {total_shops}")
            
            # Create tasks for this batch with concurrent execution
            tasks = []
            for _, shop in batch_shops.iterrows():
                tasks.append(fetch_shop_info(session, shop['id'], semaphore))
            
            # Process this batch concurrently
            batch_shop_infos = []
            successful_fetches = 0
            
            # Execute all tasks concurrently with progress bar
            for task in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"Batch {batch_num}"):
                shop_info = await task
                if shop_info:
                    batch_shop_infos.append(flatten_shop_info(shop_info))
                    successful_fetches += 1
            
            print(f"Batch {batch_num}: Successfully fetched {successful_fetches} out of {len(tasks)} shop infos")
            
            # Save this batch to CSV immediately
            save_batch_to_csv(batch_shop_infos, batch_num, final_filename)
            
            total_successful_fetches += successful_fetches
            
            # Add a shorter delay between batches since we're using rate limiting
            if batch_end < total_shops:
                print("Waiting 2 seconds before next batch...")
                await asyncio.sleep(2)
    
    print(f"\nTotal: Successfully fetched {total_successful_fetches} out of {total_shops - start_shop_index} shop infos (from resume point)")
    print(f"All data saved to {final_filename}")

# Run the asyncio event loop
asyncio.run(main())
