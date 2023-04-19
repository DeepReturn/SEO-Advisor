import os
import re
import sys
from urllib.parse import urlparse

import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
openai.api_key = API_KEY


def extract_text_from_html(html_content):
    """Extract text from HTML content using BeautifulSoup."""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=" ")

def fetch_and_save_website(url, gpt4):
    def save_chunks_to_files(text, chunk_size, directory, prefix):
        count = 0
        position = 0
        length = len(text)

        if not os.path.exists(directory):
            os.makedirs(directory)

        while position < length:
            chunk = text[position:position + chunk_size]
            count += 1
            with open(os.path.join(directory, f'{prefix}_{count}.txt'), 'w', encoding='utf-8') as output_file:
                output_file.write(chunk)
            position += chunk_size

        return count

    parsed_url = urlparse(url)
    website_name = parsed_url.netloc.replace("www.", "")
    output_directory = f"{website_name}_output"
    file_prefix = "output"
    chunk_size = 8000 if gpt4 else 2049

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract important SEO elements using BeautifulSoup
        title = soup.find("title")
        meta_description = soup.find("meta", {"name": "description"})
        meta_keywords = soup.find("meta", {"name": "keywords"})
        headings = soup.find_all(re.compile("^h[1-6]$"))
        images = soup.find_all("img", alt=True)
        internal_links = soup.find_all("a", href=re.compile("^/[^/]"))
        external_links = soup.find_all("a", href=re.compile("^(http|https)://"))

        filtered_elements = []

        if title:
            filtered_elements.append(str(title))
        if meta_description:
            filtered_elements.append(str(meta_description))
        if meta_keywords:
            filtered_elements.append(str(meta_keywords))
        for heading in headings:
            filtered_elements.append(str(heading))
        for img in images:
            filtered_elements.append(str(img))
        for link in internal_links + external_links:
            filtered_elements.append(str(link))

        filtered_content = ' '.join(filtered_elements)

        # Save the filtered content to chunks
        total_files = save_chunks_to_files(filtered_content, chunk_size, output_directory, file_prefix)
        print(f'Filtered website content saved to {total_files} output files in "{output_directory}" directory.')
    else:
        print('Failed to fetch the website content. Status code:', response.status_code)

    return website_name

def analyze_and_save_website(website_name):
    def send_to_chatgpt_api(prompt):
        messages = [
            {"role": "system", "content": "You are an AI trained to provide SEO advice."},
            {"role": "user", "content": f"Please provide SEO advice for the following website raw content:\n\n{prompt}"}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=600,
            temperature=0.5,
        )

        if response:
            return response["choices"][0]["message"]["content"]
        else:
            print("Error calling ChatGPT API")
            return None

    def save_output_to_directory(output, domain, file_number):
        output_directory = f"{domain}_to_optimize"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        output_file = os.path.join(output_directory, f"optimized_output_{file_number}.txt")
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(output)

        print(f"Optimized output saved to {output_file}")

    input_directory = f"{website_name}_output"

    if not os.path.exists(input_directory):
        print(f"Input directory '{input_directory}' not found.")
        sys.exit(1)

    input_files = [f for f in os.listdir(input_directory) if f.endswith(".txt")]

    if not input_files:
        print("No input files found in the input directory.")
        sys.exit(1)

    all_outputs = []

    for file_number, input_file in enumerate(input_files, start=1):
        with open(os.path.join(input_directory, input_file), "r", encoding="utf-8") as file:
            website_content = file.read()

        # Extract text from the HTML content before sending it to the ChatGPT API
        text_content = extract_text_from_html(website_content)

        output = send_to_chatgpt_api(text_content)
        if output:
            all_outputs.append(output)
            save_output_to_directory(output, website_name, file_number)

    # Save all outputs to a single merged file
    merged_output_file = f"{website_name}.txt"
    with open(merged_output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(all_outputs))

    print(f"All outputs merged and saved to {merged_output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Please provide a URL as a command-line argument.')
        sys.exit(1)

    website_url = sys.argv[1]
    if not website_url.startswith('http://') and not website_url.startswith('https://'):
        website_url = 'https://' + website_url

    use_gpt4 = "gpt4" in sys.argv

    website_name = fetch_and_save_website(website_url, use_gpt4)
    analyze_and_save_website(website_name)

