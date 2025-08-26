# Modern Pinterest Content Scraper

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-Automated-brightgreen.svg)
![Gradio](https://img.shields.io/badge/Gradio-Web%20UI-orange.svg)

A powerful and user-friendly Pinterest scraper built with a modern tech stack. It uses Playwright for robust browser automation and features a clean Gradio web interface for easy control.

Scrape content by keyword or by pasting any Pinterest URL, with full control over the quantity of pins you want to download.

 
*(You can replace this with your own screenshot after running the app)*

---

### Key Features

-   **Modern Core:** Utilizes `async` Playwright for efficient and non-blocking web scraping.
-   **Intuitive Web UI:** Powered by Gradio, allowing you to run and manage scrapes from your browser.
-   **Flexible Scraping Modes:**
    -   **Keyword Search:** Enter any term and scrape the visual results.
    -   **URL Ripping:** Paste a URL for a user's board, profile, or a search result page to scrape its content.
-   **Quantity Control:** A simple slider lets you specify exactly how many pins to retrieve.
-   **Organized Output:** Each scraping job creates a unique folder containing:
    -   All downloaded images.
    -   A `data.csv` file with metadata (pin URL, image URL).
-   **Stable & Reliable:** Includes automated login to a Pinterest account, which greatly improves scraping stability and avoids public-facing limitations.
-   **Secure:** Keeps your sensitive credentials safe and out of the source code using a `.env` file.

### Project Structure

```
/pinterest-scraper/
|-- app.py # The main file with the Gradio UI
|-- scraper.py # The core Playwright scraping logic
|-- requirements.txt # List of Python packages
|-- .env # Your secret credentials (you will create this)
|-- .gitignore # To exclude unnecessary files from git
|-- README.md # This file
|-- /data/ # (Auto-generated) Output directory for scrapes
```

### Setup and Installation

Follow these steps to get the scraper running on your local machine.

**1. Clone the Repository**
```bash
git clone https://github.com/LuredbyLogic/pinterest-scraper.git
cd pinterest-scraper
```

2. Create the .env File
Create a file named .env in the root of the project directory. Add your Pinterest credentials to it like this:
```
PINTEREST_EMAIL=your_pinterest_email@example.com
PINTEREST_PASSWORD=your_secret_password
```

3. Install Python Dependencies
It is recommended to use a virtual environment.

```
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install required packages
pip install -r requirements.txt
```

4. Install Playwright Browsers
This is a crucial one-time setup step that downloads the necessary browser binaries for Playwright.
```Bash
playwright install
```

### How to Run

With all the dependencies installed and your `.env` file configured, start the application:

```bash
python app.py
```

Now, open your web browser and navigate to the local URL provided in the terminal (usually `http://127.0.0.1:7860`).

### How to Use

1.  **Select Search Type:** Choose between "Keyword" or "URL".
2.  **Enter Query:** Type your search term or paste the full Pinterest URL.
3.  **Set Quantity:** Use the slider to define how many pins you want to scrape.
4.  **Start Scraping:** Click the "Start Scraping" button.
5.  **Monitor Progress:** The "Status Log" will show real-time updates.
6.  **View Results:** Once complete, the scraped data and downloaded images will appear in the UI, and a CSV download button will become available. All files will be saved locally in the `data/` directory.

---

### Future Enhancements

This project is built to be extensible. Potential future features include:
-   **API Integration:** Add support for the official Pinterest API as a scraping method.
-   **Date Range Filtering:** Implement logic to scrape pins within a specific date range.
-   **Concurrent Workers:** Allow running multiple scraping tasks simultaneously to speed up large jobs.
