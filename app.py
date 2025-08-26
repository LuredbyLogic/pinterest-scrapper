# app.py

import gradio as gr
import os
import asyncio
from dotenv import load_dotenv
from scraper import PinterestScraper
from datetime import datetime
import pandas as pd
import shutil

# Load environment variables from .env file
load_dotenv()
PINTEREST_EMAIL = os.getenv("PINTEREST_EMAIL")
PINTEREST_PASSWORD = os.getenv("PINTEREST_PASSWORD")

# Ensure credentials are set
if not PINTEREST_EMAIL or not PINTEREST_PASSWORD:
    raise ValueError("Pinterest email and password must be set in the .env file.")

# --- Main Scraper Logic Wrapper ---
async def run_scraper_process(search_type, query, num_pins, progress=gr.Progress()):
    """
    A wrapper function to be called by the Gradio interface.
    It handles the entire scraping process and yields status updates.
    """
    if not query:
        yield "Error: Query/URL cannot be empty.", None, None
        return

    progress(0, desc="Initializing...")
    yield "Initializing scraper...", None, None, None

    # Create a unique directory for this scrape job
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_query = "".join(c if c.isalnum() else "_" for c in query)[:50]
    output_dir = os.path.join("data", f"{sanitized_query}_{timestamp}")
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    try:
        async with PinterestScraper(PINTEREST_EMAIL, PINTEREST_PASSWORD) as scraper:
            progress(0.1, desc="Logging in...")
            yield "Logging into Pinterest...", None, None, None
            login_success = await scraper.login()
            if not login_success:
                yield "Login Failed. Check credentials or solve CAPTCHA in non-headless mode.", None, None, None
                return

            progress(0.3, desc=f"Scraping for '{query}'...")
            yield f"Starting to scrape for '{query}'...", None, None, None
            
            pins_data = await scraper.scrape(query, num_pins, search_type=search_type.lower())
            
            if not pins_data:
                yield "No pins found. The page might be empty or a different layout.", None, None, None
                return

            progress(0.7, desc="Downloading images...")
            yield f"Found {len(pins_data)} pins. Downloading images...", None, None, None
            
            csv_path = await scraper.download_pins(pins_data, images_dir)
            
            progress(1, desc="Complete!")
            
            # Prepare outputs for Gradio
            image_files = [os.path.join(images_dir, f) for f in os.listdir(images_dir)]
            df = pd.read_csv(csv_path)

            yield f"Scraping complete! Data saved in '{output_dir}' folder.", df, image_files, gr.File(value=csv_path, visible=True)

    except Exception as e:
        yield f"An error occurred: {e}", None, None, None
        # Clean up failed directory
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
    
# --- Gradio Interface Definition ---
with gr.Blocks(theme=gr.themes.Soft(), title="Pinterest Scraper") as demo:
    gr.Markdown("# Modern Pinterest Content Scraper")
    gr.Markdown("Uses Playwright to scrape content by keyword or URL. Make sure your `.env` file is set up with your Pinterest credentials.")

    with gr.Row():
        with gr.Column(scale=1):
            search_type = gr.Radio(
                ["Keyword", "URL"], 
                label="Search Type", 
                value="Keyword"
            )
            query_input = gr.Textbox(
                label="Enter Keyword or Pinterest URL",
                placeholder="e.g., 'modern kitchen design' or a board URL"
            )
            num_pins_slider = gr.Slider(
                minimum=10,
                maximum=1000,
                value=50,
                step=10,
                label="Number of Pins to Scrape"
            )
            start_button = gr.Button("Start Scraping", variant="primary")
            
            status_output = gr.Textbox(label="Status Log", interactive=False)
            download_csv_button = gr.File(label="Download Scraped Data (CSV)", visible=False, interactive=False)


        with gr.Column(scale=2):
            gr.Markdown("### Scraped Results")
            results_df = gr.DataFrame(label="Scraped Pin Data")
            gallery_output = gr.Gallery(label="Downloaded Images", show_label=True, elem_id="gallery", columns=5, height="auto")

    # Connect the button to the scraper function
    start_button.click(
        fn=run_scraper_process,
        inputs=[search_type, query_input, num_pins_slider],
        outputs=[status_output, results_df, gallery_output, download_csv_button]
    )

if __name__ == "__main__":
    # Create the base data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
        
    # The Gradio app's main loop is synchronous, but it can launch async functions.
    demo.launch()