import json
from time import time

import requests
import re


class Non200ResponseException(Exception):
    def __init__(self, response):
        self.response = response
        self.status_code = response.status_code
        self.message = f"Received a non-200 HTTP response: {self.status_code}"
        super().__init__(self.message)


class APIKeyNotFoundException(Exception):
    def __init__(self, message="INNERTUBE_API_KEY not found."):
        self.message = message
        super().__init__(self.message)


class YouTubeScript:
    def __init__(self):
        self.api_key = None
        self.video_ids = []

    @property
    def request_data(self):
        return {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": "2.20230525.00.00",
                }
            }
        }

    @staticmethod
    def get_innertube_api_key(response_text):
        pattern = r"ytcfg.set\(({.*})\)"
        match = re.findall(pattern, response_text)
        if match:
            json_value = match[0]
            json_data = json.loads(json_value)
            return json_data['INNERTUBE_API_KEY']

        raise APIKeyNotFoundException()

    def get_continuation_token(self, items):
        continuation_token = None
        for item in items:
            if item.get('richItemRenderer'):
                video_id = item['richItemRenderer']['content']['videoRenderer']['navigationEndpoint']['watchEndpoint'][
                    'videoId']
                self.video_ids.append(video_id)
            elif item.get('continuationItemRenderer'):
                continuation_token = item['continuationItemRenderer']['continuationEndpoint']['continuationCommand'][
                    'token']

        return continuation_token

    def fetch_initial_links(self, response_text):
        pattern = 'ytInitialData = (.*);<\/script>'
        match = re.search(pattern, response_text)
        json_value = match.group(1)
        json_data = json.loads(json_value)

        items = json_data['contents']['twoColumnBrowseResultsRenderer'][
            'tabs'][1]['tabRenderer']['content']['richGridRenderer']['contents']

        return self.get_continuation_token(items)

    def start_continuation(self, continuation_token):
        url = f'https://www.youtube.com/youtubei/v1/browse?key={self.api_key}&prettyPrint=false'

        request_data = self.request_data

        counter = 0
        while continuation_token is not None:
            counter += 1
            print(f'({counter}) Fetching videos...')
            request_data['continuation'] = continuation_token
            response = requests.post(url=url, json=request_data)

            if response.status_code != 200:
                raise Non200ResponseException(response)

            response_data = response.json()

            continuation_items = response_data['onResponseReceivedActions'][0]['appendContinuationItemsAction'][
                'continuationItems']

            continuation_token = self.get_continuation_token(continuation_items)

    def request_init(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            raise Non200ResponseException(response)

        self.api_key = self.get_innertube_api_key(response.text)

        return self.fetch_initial_links(response.text)

    @staticmethod
    def extract_channel_name(link_or_name):
        # If the input is a link, extract the channel name from it
        if link_or_name.startswith("https://www.youtube.com/"):
            match = re.match(r"https://www.youtube.com/@(\w+)/.*", link_or_name)
            if match:
                return match.group(1)
        # If the input is already a channel name, return it as is
        return link_or_name

    def save_video_ids(self, file_name):
        data = {
            'count': len(self.video_ids),
            'video_ids': [f"https://www.youtube.com/watch?v={v_id}" for v_id in self.video_ids]
        }
        with open(f'{file_name}.json', 'w') as f:
            json.dump(data, f, indent=4)

    def scrap(self, channel, file_name):
        name = self.extract_channel_name(channel)
        start_url = f'https://www.youtube.com/@{name}/videos'

        continuation_token = self.request_init(url=start_url)

        self.start_continuation(continuation_token)
        self.save_video_ids(file_name)


if __name__ == '__main__':
    channel_link_or_name = 'AnubhavSinghBassi'  # Or link like "https://www.youtube.com/@AnubhavSinghBassi/videos"
    json_file_name = 'AnubhavSinghBassi'

    start_time = time()
    script = YouTubeScript()
    script.scrap(channel_link_or_name, json_file_name)
    print(f"\nTotal time taken to scrap {len(script.video_ids)} links: {time() - start_time} seconds")
    print(f"{'#' * 20} Completed {'#' * 20}")
