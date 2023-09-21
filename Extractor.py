import streamlit as st
import os
import json
import requests
import zipfile
from io import BytesIO

# Function to download screenshots and create a ZIP file
def download_screenshots(url):
    try:
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

            # Parse the HTML code
            soup = BeautifulSoup(html_code, 'html.parser')

            # Find all 'srcset' attributes
            srcset_attributes = soup.find_all(attrs={"srcset": True})

            # Extract URLs from the 'srcset' attributes using regular expressions
            image_urls = []

            for srcset in srcset_attributes:
                urls = re.findall(r'https://\S+\.png', srcset['srcset'])
                image_urls.extend(urls)

            # Create a folder to save the downloaded screenshots
            if not os.path.exists('Screenshots'):
                os.makedirs('Screenshots')

            # Initialize a counter for incrementing filenames
            counter = 1

            # Loop through each URL and download the images
            for img_url in image_urls:
                # Generate a unique filename for each image based on the counter
                filename = os.path.join('Screenshots', f"{counter:04d}_{os.path.basename(img_url)}")

                # Send an HTTP GET request to download the image
                img_response = requests.get(img_url)

                # Check if the request was successful (status code 200)
                if img_response.status_code == 200:
                    # Save the image to the local folder
                    with open(filename, 'wb') as image_file:
                        image_file.write(img_response.content)
                    counter += 1

            # Create a ZIP file containing the screenshots and Output.json
            with zipfile.ZipFile('Screenshots.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write('Output.json')
                for root, _, files in os.walk('Screenshots'):
                    for file in files:
                        zipf.write(os.path.join(root, file))

            return True
        else:
            return False
    except Exception as e:
        return str(e)

# Streamlit app
st.title("Screenshot Extractor")

# User input for URL
url = st.text_input("Enter the URL:")

if st.button("Extract"):
    if not url:
        st.warning("Please enter a valid URL.")
    else:
        result = download_screenshots(url)
        if result:
            st.success("Screenshots downloaded and zipped successfully!")

            # Provide download link for the ZIP file
            with open('Screenshots.zip', 'rb') as f:
                zip_data = f.read()
            st.download_button(
                label="Download Screenshots ZIP",
                data=zip_data,
                file_name="Screenshots.zip",
                key="download_button",
            )
        else:
            st.error("Failed to extract screenshots. Please check the URL.")
