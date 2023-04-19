# README

This code is a Python script that fetches a website's content, filters it, and sends it to the OpenAI ChatGPT API to receive SEO advice. The script then saves the optimized output to files and merges them into a single file.

## Requirements

- Python 3.7+
- `requests` library
- `beautifulsoup4` library
- `dotenv` library
- OpenAI API key

## Installation

1. Clone this repository
2. Install the required libraries by running `pip install -r requirements.txt`
3. Create a `.env` file in the root directory and add your OpenAI API key as `API_KEY=YOUR_API_KEY_HERE`
4. Run the script by providing a website URL as a command-line argument. Optionally, you can include the `gpt4` flag to use the GPT-4 model instead of the default GPT-3.5 model.

Example usage:

- `python main.py example.com`
- `python main.py example.com gpt4`


## Output

The script will create a directory with the name of the website (without the `www.` prefix) followed by `_output`, and save the filtered content to multiple files with a maximum size of 8000 characters (or 2049 if using the GPT-4 model). The script will also create another directory with the name of the website followed by `_to_optimize`, and save the optimized outputs to files with the prefix `optimized_output`. Finally, the script will merge all outputs into a single file with the name of the website followed by `.txt`.
