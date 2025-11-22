import pandas as pd
import aiohttp
import asyncio
import csv
import os
from tqdm.asyncio import tqdm
import json

pd.set_option('display.max_columns', None)

# Configuration
RESET_CRAWL = False  # Set to True to start fresh, False to resume

# Load shops data and get top 1000 companies first
shops = pd.read_csv('torob_shops.csv')  # Start with top 1010 shops
print(f"Loaded {len(shops)} shops for product crawling")

products_url = 'https://api.torob.com/v4/internet-shop/base-product/list/?shop_id={shop_id}&available=true&page={page}&size=30000&source=next_desktop'

async def fetch_shop_products(session, shop_id, page, semaphore):
    """Fetch products for a specific shop and page"""
    async with semaphore:
        url = products_url.format(shop_id=shop_id, page=page)
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
            await asyncio.sleep(0.1)  # Small delay to avoid overwhelming
            
            async with session.get(url, headers=headers, cookies=cookies) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'shop_id': shop_id,
                        'page': page,
                        'data': data,
                        'success': True
                    }
                else:
                    # Removed detailed error print to avoid tqdm interference
                    return {
                        'shop_id': shop_id,
                        'page': page,
                        'data': None,
                        'success': False,
                        'error': f"HTTP {response.status}"
                    }
        except Exception as e:
            # Removed detailed error print to avoid tqdm interference
            return {
                'shop_id': shop_id,
                'page': page,
                'data': None,
                'success': False,
                'error': str(e)
            }

async def crawl_all_pages_for_shop(session, shop_id, shop_name, semaphore):
    """Crawl all pages for a specific shop until 'next' is null"""
    # Removed print statement to avoid tqdm interference
    
    all_products = []
    page = 0
    has_next = True
    
    while has_next:
        result = await fetch_shop_products(session, shop_id, page, semaphore)
        
        if result['success'] and result['data']:
            data = result['data']
            
            # Extract products from results
            if 'results' in data and data['results']:
                products = data['results']
                for product in products:
                    # Flatten the product data and add shop info
                    flattened_product = flatten_product_data(product, shop_id, shop_name, page, data)
                    all_products.append(flattened_product)
                
                # Removed individual page print to avoid tqdm interference
            
            # Check if there's a next page
            has_next = data.get('next') is not None
            if has_next:
                page += 1
            # Removed "reached last page" print to avoid tqdm interference
        else:
            # Only print errors, not normal completion
            if result.get('error'):
                print(f"Shop {shop_id}, Page {page}: {result['error']}")
            has_next = False
    
    # Removed final summary print to avoid tqdm interference
    return all_products

def flatten_product_data(product, shop_id, shop_name, page, page_data=None):
    """Flatten product JSON data into a flat dictionary"""
    flattened = {
        'shop_id': shop_id,
        'shop_name': shop_name,
        'page': page,
        'random_key': product.get('random_key'),
        'name1': product.get('name1'),
        'name2': product.get('name2'),
        'price': product.get('price'),
        'price_prefix': product.get('price_prefix'),
        'price_text': product.get('price_text'),
        'price_text_mode': product.get('price_text_mode'),
        'shop_text': product.get('shop_text'),
        'stock_status': product.get('stock_status'),
        'delivery_city_name': product.get('delivery_city_name'),
        'delivery_city_flag': product.get('delivery_city_flag'),
        'is_adv': product.get('is_adv'),
        'card_type': product.get('card_type'),
        'estimated_sell': product.get('estimated_sell'),
        'image_url': product.get('image_url'),
        'image_count': product.get('image_count'),
        'more_info_url': product.get('more_info_url'),
        'web_client_absolute_url': product.get('web_client_absolute_url'),
        'similar_api': product.get('similar_api'),
        'media_search': product.get('media_search')
    }
    
    # Extract categories from page data if available
    if page_data and page_data.get('categories'):
        categories_list = []
        for category in page_data['categories']:
            cat_info = f"{category.get('title', '')} (ID: {category.get('cat_id', '')}, Slug: {category.get('cat_slug', '')})"
            categories_list.append(cat_info)
        flattened['categories'] = ' | '.join(categories_list)
        flattened['primary_category'] = page_data['categories'][0].get('title', '') if page_data['categories'] else ''
        flattened['primary_category_id'] = page_data['categories'][0].get('cat_id', '') if page_data['categories'] else ''
        flattened['primary_category_slug'] = page_data['categories'][0].get('cat_slug', '') if page_data['categories'] else ''
    else:
        flattened['categories'] = ''
        flattened['primary_category'] = ''
        flattened['primary_category_id'] = ''
        flattened['primary_category_slug'] = ''
    
    # Extract parent categories if available
    if page_data and page_data.get('parent_categories'):
        parent_categories_list = []
        for parent_cat in page_data['parent_categories']:
            parent_categories_list.append(parent_cat.get('title', ''))
        flattened['parent_categories'] = ' | '.join(parent_categories_list)
    else:
        flattened['parent_categories'] = ''
    
    # Extract additional category metadata
    if page_data:
        flattened['category_is_leaf'] = page_data.get('category_is_leaf', False)
        flattened['filter_by_category_title'] = page_data.get('filter_by_category_title', '')
        flattened['total_products_count'] = page_data.get('count', 0)
        flattened['max_price'] = page_data.get('max_price', 0)
        flattened['min_price'] = page_data.get('min_price', 0)
        flattened['seo_title'] = page_data.get('seo_title', '')
        flattened['seo_description'] = page_data.get('seo_description', '')
    else:
        flattened['category_is_leaf'] = False
        flattened['filter_by_category_title'] = ''
        flattened['total_products_count'] = 0
        flattened['max_price'] = 0
        flattened['min_price'] = 0
        flattened['seo_title'] = ''
        flattened['seo_description'] = ''
    
    # Extract badges if present
    if product.get('badges'):
        flattened['badges'] = ', '.join([str(badge) for badge in product['badges']])
    else:
        flattened['badges'] = ''
    
    # Extract discount info if present
    if product.get('discount_info'):
        flattened['discount_info'] = ', '.join([str(discount) for discount in product['discount_info']])
    else:
        flattened['discount_info'] = ''
    
    # Extract media URLs
    if product.get('media_urls'):
        media_urls = []
        for media in product['media_urls']:
            if media.get('type') == 'image':
                media_urls.append(media.get('url', ''))
        flattened['media_urls'] = ', '.join(media_urls)
        flattened['media_count'] = len(media_urls)
    else:
        flattened['media_urls'] = ''
        flattened['media_count'] = 0
    
    # Extract direct CTA info
    if product.get('direct_cta'):
        cta = product['direct_cta']
        flattened['cta_url'] = cta.get('url', '')
        flattened['cta_label'] = cta.get('label', '')
        flattened['cta_list_type'] = cta.get('list_type', '')
        flattened['cta_icon'] = cta.get('icon', '')
    else:
        flattened['cta_url'] = ''
        flattened['cta_label'] = ''
        flattened['cta_list_type'] = ''
        flattened['cta_icon'] = ''
    
    return flattened

def save_products_to_csv(all_products, filename):
    """Save all products to CSV file"""
    if not all_products:
        print("No products to save")
        return
    
    # Get all possible fieldnames
    all_fieldnames = set()
    for product in all_products:
        all_fieldnames.update(product.keys())
    
    fieldnames = sorted(all_fieldnames)
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_products)
    
    print(f"Saved {len(all_products)} products to {filename}")

def append_products_to_csv(products_batch, filename):
    """Append products batch to existing CSV file"""
    if not products_batch:
        return
    
    # Check if file exists
    file_exists = os.path.exists(filename)
    
    if file_exists:
        # Read existing file to get fieldnames
        existing_df = pd.read_csv(filename)
        existing_fieldnames = set(existing_df.columns)
        
        # Get fieldnames from new batch
        new_fieldnames = set()
        for product in products_batch:
            new_fieldnames.update(product.keys())
        
        # Combine all fieldnames
        all_fieldnames = existing_fieldnames.union(new_fieldnames)
        fieldnames = sorted(all_fieldnames)
        
        # Create new batch dataframe with all columns
        batch_df = pd.DataFrame(products_batch)
        
        # Ensure both dataframes have same columns
        for col in fieldnames:
            if col not in existing_df.columns:
                existing_df[col] = ''
            if col not in batch_df.columns:
                batch_df[col] = ''
        
        # Reorder columns
        existing_df = existing_df[fieldnames]
        batch_df = batch_df[fieldnames]
        
        # Combine and save
        combined_df = pd.concat([existing_df, batch_df], ignore_index=True)
        combined_df.to_csv(filename, index=False, encoding='utf-8')
    else:
        # Create new file
        save_products_to_csv(products_batch, filename)
    
    print(f"Appended {len(products_batch)} products to {filename}")

def get_processed_shops(filename):
    """Get list of shops that have already been processed"""
    processed_shops = set()
    
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename)
            if 'shop_id' in df.columns:
                processed_shops = set(df['shop_id'].unique())
                print(f"Found {len(processed_shops)} already processed shops")
        except Exception as e:
            print(f"Error reading existing file: {e}")
    
    return processed_shops

async def main():
    """Main function to crawl products for all shops"""
    concurrent_requests = 100  # Limit concurrent requests
    final_filename = './shop_products.csv'
    
    print(f"Starting product crawling for {len(shops)} shops")
    print(f"Concurrent requests limit: {concurrent_requests}")
    
    # Check if we should reset the crawl
    if RESET_CRAWL and os.path.exists(final_filename):
        os.remove(final_filename)
        print(f"Reset mode: Removed existing {final_filename}")
    
    # Check for existing progress
    processed_shops = get_processed_shops(final_filename)
    
    # Filter out already processed shops
    remaining_shops = shops[~shops['id'].isin(processed_shops)]
    
    if len(remaining_shops) == 0:
        print("All shops have already been processed!")
        return
    
    print(f"Resuming crawl: {len(processed_shops)} shops already processed")
    print(f"Remaining shops to process: {len(remaining_shops)}")
    
    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(concurrent_requests)
    
    # Configure session with connection limits
    connector = aiohttp.TCPConnector(limit=30, limit_per_host=15)
    timeout = aiohttp.ClientTimeout(total=60)
    
    total_new_products = 0
    processed_count = 0
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # Test with first remaining shop
        test_shop = remaining_shops.iloc[0]
        print(f"Testing with shop: {test_shop['name']} (ID: {test_shop['id']})")
        
        test_result = await fetch_shop_products(session, test_shop['id'], 0, semaphore)
        if test_result['success']:
            print("Test successful! Starting crawl...")
        else:
            print("Test failed! Stopping execution.")
            return
        
        # Process shops in batches to save progress incrementally
        batch_size = 5000  # Process 5000 shops at a time

        for batch_start in range(0, len(remaining_shops), batch_size):
            batch_end = min(batch_start + batch_size, len(remaining_shops))
            batch_shops = remaining_shops.iloc[batch_start:batch_end]
            
            print(f"\nProcessing batch {batch_start//batch_size + 1}/{(len(remaining_shops) + batch_size - 1)//batch_size}")
            print(f"Shops {batch_start + 1} to {batch_end} of {len(remaining_shops)} remaining")
            
            # Create tasks for this batch
            tasks = []
            for _, shop in batch_shops.iterrows():
                task = crawl_all_pages_for_shop(session, shop['id'], shop['name'], semaphore)
                tasks.append(task)
            
            # Execute batch with progress bar
            batch_products = []
            for task in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"Batch {batch_start//batch_size + 1}"):
                shop_products = await task
                batch_products.extend(shop_products)
                processed_count += 1
            
            # Save this batch immediately
            if batch_products:
                append_products_to_csv(batch_products, final_filename)
                total_new_products += len(batch_products)
                # Only print summary after each batch, not individual progress
                print(f"\nBatch {batch_start//batch_size + 1} completed: {len(batch_products)} products saved")
            
            # Add delay between batches
            if batch_end < len(remaining_shops):
                await asyncio.sleep(3)
    
    print(f"\nCrawling completed!")
    print(f"Processed {processed_count} new shops")
    print(f"Total new products collected: {total_new_products}")
    
    # Display final statistics
    if os.path.exists(final_filename):
        final_df = pd.read_csv(final_filename)
        print(f"\nFinal Summary:")
        print(f"Total products in file: {len(final_df)}")
        print(f"Total unique shops: {final_df['shop_id'].nunique()}")
        print(f"DataFrame shape: {final_df.shape}")
        print(f"Top 10 shops by product count:")
        print(final_df['shop_name'].value_counts().head(10))

# Run the crawler
if __name__ == "__main__":
    asyncio.run(main())
