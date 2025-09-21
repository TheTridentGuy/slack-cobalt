from typing import BinaryIO, Any

import requests


class CobaltAPIStreamableResponse:
    def __init__(self, stream: requests.Response, original_response_json: Any):
        self.stream = stream
        self._original_response_json = original_response_json

    @property
    def filename(self):
        return self._original_response_json["filename"]

    def stream_to_file(self, file: BinaryIO | str, chunk_size=8192):
        if isinstance(file, str):
            file = open(file, "wb")
        with file as f:
            for chunk in self.stream.iter_content(chunk_size=chunk_size):
                f.write(chunk)
            if f.tell() == 0:
                raise CobaltAPIError("Response stream was empty.")


class CobaltAPITunnelResponse(CobaltAPIStreamableResponse):
    pass


class CobaltAPIRedirectResponse(CobaltAPIStreamableResponse):
    pass


class CobaltAPIClient:
    def __init__(self, instance_url: str, api_key: str = None) -> None:
        self.instance_url = instance_url
        self.api_key = api_key

    def post(self, url: str) -> CobaltAPITunnelResponse | CobaltAPIRedirectResponse | None:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"}
        if self.api_key:
            headers.update({
                               "Authorization": f"Api-Key {self.api_key}"})
        response = requests.post(self.instance_url, json={
            "url": url}, headers=headers).json()
        status = response["status"]
        if status == "error":
            raise CobaltAPIError(response["error"]["code"])
        elif status == "tunnel":
            stream = requests.get(response["url"], stream=True)
            try:
                stream.raise_for_status()
            except requests.exceptions.RequestException as e:
                raise CobaltAPIError(f"Tunnel URL errored out: {e}")
            return CobaltAPITunnelResponse(stream, response)
        elif status == "redirect":
            stream = requests.get(response["url"], stream=True)
            try:
                stream.raise_for_status()
            except requests.exceptions.RequestException as e:
                raise CobaltAPIError(f"Redirect URL errored out: {e}")
            return CobaltAPIRedirectResponse(stream, response)
        else:
            raise CobaltAPIClientException(f"Unsupported non-error status: {status}")


class CobaltAPIError(Exception):
    pass


class CobaltAPIClientException(Exception):
    pass
