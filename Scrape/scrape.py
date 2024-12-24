import requests
from bs4 import BeautifulSoup

def fetch_and_print_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        # Sending a GET request, ignoring SSL certificate verification for troubleshooting
        response = requests.get(url, headers=headers, verify=False)

        # Check if the request was successful
        if response.status_code == 200:
            # Use BeautifulSoup to parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            # Print out the prettified version of the HTML
            print(soup.prettify())
        else:
            print(f"Failed to retrieve the web page. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# Example usage
url = "https://www.youtube.com"
fetch_and_print_html(url)
