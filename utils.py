import requests
from bs4 import BeautifulSoup
import os
import openai

# Load environment variables if not already loaded
from dotenv import load_dotenv
load_dotenv()

# Function to fetch HTML content from a URL
def fetch_web_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Will raise an HTTPError for bad responses
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None

# Function to extract useful information from HTML content
def extract_information(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    return text.strip()  # Stripping whitespace for cleaner text output

# Function to analyze text using OpenAI's GPT-4
def analyze_text_with_gpt4(text, question):
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Please analyze the call log provided in the URL above to identify and extract 3 key facts in the form of concise points from the discussion. The log contains dialogue from multiple participants on various topics. Summarize the main points and decisions made based on the question provided. If a later document contradicts earlier information, edit the facts to reflect the most current and accurate information. Return the facts in a clear and concise format, using complete sentences. Here's the question regarding the call: {question}"},
                {"role": "user", "content": f"Here is the extracted content from the call log: {text}"}
                ],
                temperature=0.7,
                max_tokens=1024,
                top_p=1
                )
    # Print the summarized analysis from GPT-4
        return (completion.choices[0].message.content)
    except Exception as e:
        print(f"Error while processing with GPT-4: {e}")
        return "Failed to process the text with GPT-4."

# Main function to handle the extraction and analysis of URLs
def process_urls(urls):
    combined_text = ""
    for url in urls.split(" "):
        html_content = fetch_web_page(url)
        if html_content:
            extracted_text = extract_information(html_content)
            combined_text += extracted_text + "\n\n"  # Add space between contents of different URLs

    # Analyze the combined text using GPT-4
    if combined_text:
        analysis_result = analyze_text_with_gpt4(combined_text, question)
        print("GPT-4 Analysis:", analysis_result)
    else:
        print("No data was extracted from the URLs provided.")

# Example URLs
'''urls = 
https://storage.googleapis.com/cleric-assignment-call-logs/call_log_20240314_104111.txt
https://storage.googleapis.com/cleric-assignment-call-logs/call_log_20240315_104111.txt

# Run the process
process_urls(urls)'''

question = "What is our pricing model?"
