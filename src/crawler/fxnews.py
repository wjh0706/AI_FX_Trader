import os
import requests
from bs4 import BeautifulSoup
import jsonlines
import sys

try:
    # Get page range from command line arguments
    if len(sys.argv) != 3:
        print("Usage: python fxnews.py <start_page> <end_page>")
        sys.exit(1)

    start_page = int(sys.argv[1])
    end_page = int(sys.argv[2])

    if start_page > end_page:
        print("Start page cannot be greater than end page.")
        sys.exit(1)

    # Get the current working directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to the directory containing the JSONL files
    jsonl_dir = os.path.join(current_dir, 'forexnews')

    # Ensure the directory exists, create it if it doesn't
    os.makedirs(jsonl_dir, exist_ok=True)

    for page_num in range(start_page, end_page + 1):
        print(f"working on page {page_num}")
        # Get the HTML content from the website
        url = f'https://www.forexlive.com/page/{page_num}/'
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        html_content = response.text

        # Parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract all instances of headline, brief, and date
        headlines = [headline.get_text(strip=True).replace('\n', '') for headline in soup.find_all('h3', class_='article-slot__title title bottom')]
        briefs = [li.get_text(strip=True) for li in soup.find_all('li', class_='text-body tldr__item bold')]
        dates = [date.get_text(strip=True).replace('\n', '') for date in soup.find_all('div', class_='publisher-details__date')]

        # Construct the absolute path to the JSONL file within the directory
        jsonl_file_path = os.path.join(jsonl_dir, f'{page_num}.jsonl')

        # Write extracted information to a JSONL file
        with jsonlines.open(jsonl_file_path, mode='w') as writer:
            for headline, brief, date in zip(headlines, briefs, dates):
                data = {
                    'headline': headline,
                    'brief': brief,
                    'date': date
                }
                writer.write(data)
        print(f"page {page_num} completed")

except requests.HTTPError as e:
    print("HTTP error occurred:", e)
except requests.RequestException as e:
    print("Error fetching content:", e)
except ValueError:
    print("Please provide valid integer values for start and end pages.")
except Exception as e:
    print("An error occurred:", e)
