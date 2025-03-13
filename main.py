import os
import json
import requests
import zipfile
import tempfile
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed

# GraphQL API URL
GRAPHQL_URL = "https://api.impakt.com/graphql"

# Streamlit UI
st.title("Impakt Media Downloader")

# User input for `take` value
take_value = st.number_input("Number of posts to fetch (min: 1, max: 100)", min_value=1, max_value=100, value=10)

# Button to fetch data
if st.button("Fetch Posts"):
    # GraphQL query
    query = """
    query Posts($take: Int!) {
        posts(where: { uploadId: { gt: 0 } }, orderBy: [{ createdAt: Desc }], take: $take) {
            items {
                Media {
                    ext
                    url
                }
                Creator {
                    username
                }
            }
        }
    }
    """

    # Make request
    response = requests.post(GRAPHQL_URL, json={"query": query, "variables": {"take": take_value}})

    if response.status_code != 200:
        st.error("Failed to fetch data from the API")
        st.stop()

    data = response.json()
    items = data.get("data", {}).get("posts", {}).get("items", [])

    if not items:
        st.warning("No posts found.")
        st.stop()

    st.success(f"Fetched {len(items)} posts. Starting downloads...")

    # Temporary directory
    temp_dir = tempfile.mkdtemp()

    def get_unique_filename(base_name, extension, folder):
        """Ensure unique filenames."""
        counter = 1
        new_name = f"{base_name}.{extension}"
        while os.path.exists(os.path.join(folder, new_name)):
            new_name = f"{base_name}_{counter}.{extension}"
            counter += 1
        return new_name

    def download_file(item):
        """Download a media file."""
        media_url = item["Media"]["url"]
        username = item["Creator"]["username"]
        file_extension = item["Media"]["ext"]

        if not file_extension:
            file_extension = ".mp4"

        unique_filename = get_unique_filename(username, file_extension, temp_dir)
        file_path = os.path.join(temp_dir, unique_filename)

        try:
            response = requests.get(media_url, stream=True, timeout=10)
            response.raise_for_status()

            with open(file_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

            return file_path  # Return valid file path
        except requests.RequestException as e:
            return None  # Indicate failure

    # Download in parallel (batches of 10)
    batch_size = 10
    downloaded_files = []

    with ThreadPoolExecutor(max_workers=batch_size) as executor:
        futures = {executor.submit(download_file, item): item for item in items}
        for future in as_completed(futures):
            result = future.result()
            if result:  # If download was successful
                downloaded_files.append(result)
                st.write(f"✅ Downloaded: {os.path.basename(result)}")
            else:
                st.write("❌ Failed to download a file.")

    # Check if any files were downloaded before zipping
    if not downloaded_files:
        st.error("No files were successfully downloaded.")
        st.stop()

    # Create ZIP
    zip_path = os.path.join(temp_dir, "downloaded_media.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in downloaded_files:  # Only add successfully downloaded files
            zipf.write(file, arcname=os.path.basename(file))

    # Verify ZIP isn't empty
    if os.stat(zip_path).st_size == 0:
        st.error("The ZIP archive is empty. No valid files were downloaded.")
        st.stop()

    # Provide ZIP for download
    with open(zip_path, "rb") as zip_file:
        st.download_button(
            label="Download All Media as ZIP",
            data=zip_file,
            file_name="media_files.zip",
            mime="application/zip"
        )

    st.success("Download ready! 🎉")
