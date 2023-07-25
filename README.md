# Python Script to Extract YouTube Videos
The Python script extracts YouTube video links from a specific channel using pure Python code, without relying on any third-party libraries. It accepts either the channel link or name as input and fetches all the video links from the channel. The script offers a simple and self-contained solution for users to extract video data programmatically without external dependencies.


## To Run Script

    python main.py

#### Note: To add channel name, open `main.py` file, scroll to the bottom of file and change value of variable

    channel_link_or_name = 'thenewboston' # Name of @channel

    OR 

    channel_link_or_name = 'https://www.youtube.com/@thenewboston/videos' # Link of @channel videos tab

After script run successfully, their will be file generated named `channel_name.json` which contains all the videos link.
