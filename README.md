# Impakt Media Downloader

This is a Streamlit app that:

    Fetches media files from the Impakt GraphQL API.
    Downloads them in parallel batches for speed.
    Saves each file with the creator's username.
    Ensures unique filenames.
    Provides a scrollable log of the download status.
    Generates a ZIP file for bulk downloads.

## Installation

First, install the required dependencies:

```
pip install streamlit requests
```

## Usage

    Run the app:

    streamlit run app.py

    Set the number of posts to fetch (1-100).
    Click "Fetch Posts" to start downloading.
    Monitor progress in the scrollable log.
    Download all media as a ZIP file.

## Features

✅ Fetches latest media posts from Impakt<br/>
✅ Downloads in parallel (10 at a time)<br/>
✅ Uses Media.ext for correct file types<br/>
✅ Ensures unique filenames<br/>
✅ Provides ZIP file for bulk download<br/>

## Requirements

    Python 3.7+
    Streamlit
    Requests
