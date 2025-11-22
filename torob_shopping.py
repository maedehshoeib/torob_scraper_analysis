import asyncio
import aiohttp
import pandas as pd
from tqdm.asyncio import tqdm
import random

url = 'https://api.torob.com/v4/internet-shop/list/?page={page}&shop_type=all&size={count}&source=next_desktop'

async def fetch_shops(session, page, count, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Add random jitter delay between 1-5 seconds
            await asyncio.sleep(random.uniform(1, 5))
            
            headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8,fa;q=0.7',
                'origin': 'https://torob.com',
                'priority': 'u=1, i',
                'referer': 'https://torob.com/',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
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
            
            async with session.get(url.format(page=page, count=count), headers=headers, cookies=cookies) as response:
                content_type = response.headers.get('content-type', '')
                
                if response.status == 200:
                    # Check if response is JSON
                    if 'application/json' in content_type:
                        try:
                            data = await response.json()
                            return data
                        except Exception as json_err:
                            # If JSON parsing fails, treat as error
                            print(f"Page {page}: JSON parsing failed. Content type: {content_type}, Error: {json_err}")
                            if attempt < max_retries - 1:
                                continue
                            return {"error": f"JSON parsing failed for page {page}"}
                    else:
                        text_response = await response.text()
                        # Check if it's a Cloudflare challenge
                        if 'آیا شما یک ربات هستید' in text_response or 'challenge' in text_response.lower():
                            print(f"Page {page}: Cloudflare challenge detected")
                            return {"error": f"Cloudflare challenge for page {page}"}
                        else:
                            print(f"Page {page}: Unexpected content type: {content_type}")
                            print(f"First 500 chars: {text_response[:500]}")
                            if attempt < max_retries - 1:
                                continue
                            return {"error": f"Unexpected response for page {page}"}
                else:
                    print(f"Page {page}: HTTP {response.status}")
                    if attempt < max_retries - 1:
                        continue
                    return {"error": f"HTTP {response.status} for page {page}"}
                    
        except Exception as e:
            print(f"Page {page} (attempt {attempt + 1}): Exception - {type(e).__name__}: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(random.uniform(2, 5))  # Wait before retry
                continue
            return {"error": f"Exception for page {page}: {type(e).__name__}: {str(e)}"}

async def scrape_all_shops():
    all_shops = []
    
    # Add connection limits and timeout - more conservative settings
    connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
    timeout = aiohttp.ClientTimeout(total=120)  # Increased timeout
    
    # Use a cookie jar to maintain session
    cookie_jar = aiohttp.CookieJar()
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout, cookie_jar=cookie_jar) as session:
        # Try to visit the main site first to get cookies
        try:
            async with session.get('https://torob.com/', headers={
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'accept': '*/*',
                'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8,fa;q=0.7'
            }) as response:
                print(f"Main site visit: {response.status}")
                await asyncio.sleep(2)
        except Exception as e:
            print(f"Main site visit failed: {e}")
        
        # Create tasks for all pages at once
        total_pages = 55
        tasks = [fetch_shops(session, page, 3000) for page in range(total_pages)]
        
        # Execute all tasks with progress bar
        results = await tqdm.gather(*tasks, desc="Fetching all shops")
        
        # Process results
        errors = []
        for idx, result in enumerate(results):
            if "error" in result:
                errors.append(result["error"])
            elif "results" in result and result["results"]:
                all_shops.extend(result["results"])
                print(f"Page {idx}: Added {len(result['results'])} shops")
            else:
                errors.append(f"Page {idx}: No results field or empty results")
        
        if errors:
            print(f"Errors encountered:")
            for error in errors:
                print(f"  - {error}")
    
    return all_shops

async def main():
    shops_data = await scrape_all_shops()
    
    # Convert to DataFrame
    df = pd.DataFrame(shops_data)
    
    # Export to CSV
    df.to_csv('torob_shops.csv', index=False, encoding='utf-8')
    print(f"Exported {len(df)} shops to torob_shops.csv")
    
    # Display basic info
    print(f"DataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

if __name__ == "__main__":
    asyncio.run(main())