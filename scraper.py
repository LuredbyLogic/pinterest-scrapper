# scraper.py

import os
import time
import asyncio
import pandas as pd
import aiofiles
from playwright.async_api import async_playwright, TimeoutError
from urllib.parse import quote_plus
from datetime import datetime

class PinterestScraper:
    def __init__(self, email, password, headless=False):
        self.email = email
        self.password = password
        self.headless = headless
        self.browser = None
        self.page = None

    async def __aenter__(self):
        self.p = await async_playwright().start()
        self.browser = await self.p.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.p:
            await self.p.stop()

    async def login(self):
        """Logs into Pinterest."""
        print("Navigating to login page...")
        await self.page.goto("https://www.pinterest.com/login/")
        
        # Wait for the email field to be ready
        await self.page.wait_for_selector('input[name="id"]', timeout=30000)
        
        print("Entering credentials...")
        await self.page.fill('input[name="id"]', self.email)
        await self.page.fill('input[name="password"]', self.password)
        await self.page.click('button[type="submit"]')
        
        # Wait for successful login by checking for the search bar on the home page
        print("Waiting for login confirmation...")
        try:
            await self.page.wait_for_selector('input[aria-label="Search"]', timeout=30000)
            print("Login successful.")
            return True
        except TimeoutError:
            print("Login failed. Could be a CAPTCHA or wrong credentials.")
            # Save a screenshot for debugging
            await self.page.screenshot(path="login_error.png")
            return False

    async def scrape(self, query, max_pins, search_type='keyword'):
        """
        Main scraping function. Navigates based on search type and scrapes pins.
        - query: The keyword or URL to search for.
        - max_pins: The target number of pins to scrape.
        - search_type: 'keyword' or 'url'.
        """
        if search_type == 'keyword':
            url = f"https://www.pinterest.com/search/pins/?q={quote_plus(query)}"
        elif search_type == 'url':
            url = query
        else:
            raise ValueError("Invalid search_type. Must be 'keyword' or 'url'.")

        print(f"Navigating to: {url}")
        await self.page.goto(url, wait_until="load", timeout=60000)
        await asyncio.sleep(5) # Give page time to settle

        scraped_pins = set()
        last_pin_count = 0
        stale_scrolls = 0

        while len(scraped_pins) < max_pins:
            current_pin_count = len(scraped_pins)
            print(f"Scraped {current_pin_count}/{max_pins} pins...")

            # --- Scroll to load more content ---
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            await asyncio.sleep(2) # Wait for content to load

            # --- Extract pin data from the page ---
            # This selector targets the container for each pin
            pin_elements = await self.page.query_selector_all('div[data-grid-item="true"]')
            
            for element in pin_elements:
                # Get the link to the pin detail page
                link_element = await element.query_selector('a')
                if not link_element: continue
                pin_url = await link_element.get_attribute('href')
                if pin_url and pin_url.startswith('/pin/'):
                    full_pin_url = f"https://www.pinterest.com{pin_url}"

                    # Get the image source
                    img_element = await element.query_selector('img')
                    if not img_element: continue
                    img_src = await img_element.get_attribute('src')
                    
                    if full_pin_url and img_src:
                        # Use a higher resolution version of the image if available
                        high_res_img_src = img_src.replace('/236x/', '/736x/')
                        scraped_pins.add((full_pin_url, high_res_img_src))
                
                if len(scraped_pins) >= max_pins:
                    break
            
            # --- Check if we are stuck ---
            if len(scraped_pins) == last_pin_count:
                stale_scrolls += 1
                if stale_scrolls > 5: # If no new pins are found after 5 scrolls, break
                    print("No more new pins found. Ending scrape.")
                    break
            else:
                last_pin_count = len(scraped_pins)
                stale_scrolls = 0
        
        return list(scraped_pins)[:max_pins]

    async def download_pins(self, pins_data, output_dir):
        """Downloads images and saves metadata."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Use aiohttp for concurrent downloads for better performance
        import aiohttp
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i, (pin_url, img_url) in enumerate(pins_data):
                file_extension = os.path.splitext(img_url.split('?')[0])[-1] or '.jpg'
                filename = os.path.join(output_dir, f"pin_{i+1}{file_extension}")
                tasks.append(self._download_image(session, img_url, filename))
            
            await asyncio.gather(*tasks)

        # Save metadata to CSV
        df = pd.DataFrame(pins_data, columns=['pin_url', 'image_url'])
        csv_path = os.path.join(output_dir, "data.csv")
        df.to_csv(csv_path, index=False)
        print(f"Saved metadata to {csv_path}")
        return csv_path

    async def _download_image(self, session, url, path):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    async with aiofiles.open(path, mode='wb') as f:
                        await f.write(await response.read())
                    print(f"Downloaded {path}")
                else:
                    print(f"Failed to download {url} - Status: {response.status}")
        except Exception as e:
            print(f"Error downloading {url}: {e}")