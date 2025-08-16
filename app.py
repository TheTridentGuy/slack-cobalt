import re
import os
import shutil
import dotenv
from pathlib import Path
from slack_bolt import App
from cobalt_api import CobaltAPIClient, CobaltAPIError, CobaltAPIClientException
from slack_bolt.adapter.socket_mode import SocketModeHandler


dotenv.load_dotenv()
app = App(token=os.environ["SLACK_BOT_TOKEN"])
client = app.client
cobalt_client = CobaltAPIClient(os.environ["COBALT_API_INSTANCE"], os.environ.get("COBALT_API_KEY"))
OUTPUT_DIR = os.environ.get("OUTPUT_DIR")
OUTPUT_DIR = "output" if not OUTPUT_DIR else OUTPUT_DIR


def recursive_url_search(elements):
    if elements is None:
        return []
    urls = []
    for element in elements:
        if element.get("type") == "link":
            urls.append(element["url"])
        else:
            urls.extend(recursive_url_search(element.get("elements")))
    return urls


@app.event("message")
def raw_file_reply(message):
    blocks = message.get("blocks")
    if not blocks:
        return
    urls = recursive_url_search(blocks)
    ts = message["ts"]
    for url in urls:
        if re.search(r"(youtube\.com|youtu\.be)", url):
            try:
                cobalt_response = cobalt_client.post(url)
                save_path = str(Path(OUTPUT_DIR)/Path(cobalt_response.filename))
                cobalt_response.stream_to_file(save_path)
                client.files_upload_v2(channel=message["channel"], file=save_path, thread_ts=ts)
                os.remove(save_path)
            except (CobaltAPIError, CobaltAPIClientException) as e:
                print(e)


def clean_output_dir():
    try:
        shutil.rmtree(OUTPUT_DIR)
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    try:
        clean_output_dir()
        os.mkdir(OUTPUT_DIR)
        SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    except KeyboardInterrupt:
        clean_output_dir()
