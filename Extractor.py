import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import re
from lxml import html
from zipfile import ZipFile  # Import ZipFile from zipfile module

# Function to extract HTML content from a URL
def extract_html_content(url):
    try:
        # Send an HTTP GET request to fetch the HTML content
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception as e:
        return None

# Function to extract image URLs from HTML content
def extract_and_filter_image_urls(html_content):
    try:
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

            # Filter for image URLs containing '600'
            image_urls = [url for url in image_urls if '600' in url]

            return image_urls
        else:
            return []
    except Exception as e:
        return []

# Streamlit app
st.title("Image Downloader")

# User input for URL
url = st.text_input("Enter the URL:")

if st.button("Download"):
    if not url:
        st.warning("Please enter a valid URL.")
    else:
        try:
            # Extract HTML content from the provided URL
            html_content = extract_html_content(url)

            if html_content:
                # Extract and filter image URLs from the HTML content
                image_urls = extract_and_filter_image_urls(html_content)

                if image_urls:
                    st.success("Image URLs extracted and filtered successfully!")

                    # Download button to download all images
                    all_images_data = []

                    for i, img_url in enumerate(image_urls, start=1):
                        img_response = requests.get(img_url)
                        if img_response.status_code == 200:
                            img = Image.open(BytesIO(img_response.content))

                            # Display small previews of the images
                            st.image(img, caption=f"Image {i}", width=200)

                            # Append image data for downloading all images
                            all_images_data.append((f"image_{i}.jpg", img_response.content))
                        else:
                            st.warning(f"Failed to download image {i} from {img_url}.")

                    # Provide a single download button to download all images
                    if st.button("Download All Images"):
                        with st.spinner("Downloading..."):
                            zip_data = BytesIO()
                            with ZipFile(zip_data, 'w') as zipf:
                                for file_name, img_data in all_images_data:
                                    zipf.writestr(file_name, img_data)
                            st.write(zip_data)
                            st.download_button(
                                label="Download All Images",
                                data=zip_data.getvalue(),
                                file_name="images.zip",
                                key="download_all_button",
                            )

                else:
                    st.warning("No image URLs containing '600' found in the HTML.")
            else:
                st.error("Failed to fetch HTML content. Please check the URL.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
