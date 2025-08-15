import requests


class CobaltAPI:
    def __init__(self, instance_url: str) -> None:
        self.instance_url = instance_url

    def stream(self, url: str) -> requests.Response:
        response = requests.post(self.instance_url, json={
            "url": url
        }, headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        }).json()
        if response["status"] == "error":
            raise CobaltAPIError(response["error"])
        stream = requests.get(response["url"], stream=True)
        stream.raise_for_status()
        return stream

    def stream_to_file(self, url: str, file_path: str, chunk_size: int = 8192) -> None:
        stream = self.stream(url)
        with open(file_path, "wb") as f:
            for chunk in stream.iter_content(chunk_size=chunk_size):
                f.write(chunk)


class CobaltAPIError(Exception):
    pass
