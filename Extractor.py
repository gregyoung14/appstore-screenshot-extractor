#App Store ScreenShot Extractor

from bs4 import BeautifulSoup
import json
import re
import requests
from lxml import html
import os

# URL to fetch
url = 'https://apps.apple.com/us/app/planet-fitness-workouts/id399857015'  # Replace with your URL

# Fetch the web page content
response = requests.get(url)
html_content = response.content

# Parse the HTML content using lxml
parsed_html = html.fromstring(html_content)

# Extract content using class name
class_name = "we-screenshot-viewer__screenshots"
soup = BeautifulSoup(html_content, 'html.parser')
element_class = soup.find(class_=class_name)
if element_class:
    # Convert the element to a string
    html_code = str(element_class)
    # You can use html_code as needed

# Now you have the extracted HTML content in html_code

# Parse the HTML code
soup = BeautifulSoup(html_code, 'html.parser')

# Find all 'srcset' attributes
srcset_attributes = soup.find_all(attrs={"srcset": True})

# Extract URLs from the 'srcset' attributes using regular expressions
image_urls = []

for srcset in srcset_attributes:
    urls = re.findall(r'https://\S+\.png', srcset['srcset'])
    image_urls.extend(urls)

# Convert the list of URLs to a JSON array
json_data = json.dumps(image_urls)

# Load the JSON data
image_urls = json.loads(json_data)

# Filter the URLs to keep only those ending with "600x0w.png"
filtered_urls = [url for url in image_urls if url.endswith("600x0w.png")]

# Convert the filtered list of URLs to a JSON array
filtered_json_data = json.dumps(filtered_urls)

# Save the filtered JSON data to a local file named "Output.json"
with open("Output.json", "w") as outfile:
    json.dump(filtered_urls, outfile)

print("Filtered JSON data saved to 'Output.json'")

# Load the filtered JSON data from 'Output.json'
with open('Output.json', 'r') as json_file:
    filtered_urls = json.load(json_file)

# Create a folder to save the downloaded screenshots if it doesn't exist
if not os.path.exists('Screenshots'):
    os.makedirs('Screenshots')

# Initialize a counter for incrementing filenames
counter = 1

# Loop through each URL and download the images
for url in filtered_urls:
    # Generate a unique filename for each image based on the counter
    filename = os.path.join('Screenshots', f"{counter:04d}_{os.path.basename(url)}")
    
    # Send an HTTP GET request to download the image
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Save the image to the local folder
        with open(filename, 'wb') as image_file:
            image_file.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download: {url}")
    
    # Increment the counter for the next filename
    counter += 1