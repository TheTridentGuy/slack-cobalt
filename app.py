import re
import os
import shutil
import dotenv
from slack_bolt import App
from cobalt_api import CobaltAPI, CobaltAPIError
from slack_bolt.adapter.socket_mode import SocketModeHandler


dotenv.load_dotenv()
app = App(token=os.environ["SLACK_BOT_TOKEN"])
client = app.client
cobalt_client = CobaltAPI(os.environ["COBALT_API_INSTANCE"])


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


@app.message(re.compile(r"(youtube.com|youtu.be)"))
def raw_file_reply(message, say):
    urls = recursive_url_search(message["blocks"])
    ts = message["ts"]
    for index, url in enumerate(urls):
        try:
            save_path = f"output/{str(ts).replace('.', '_')}_{index}.mp4"
            cobalt_client.stream_to_file(url, save_path)
            client.files_upload_v2(channel=message["channel"], file=save_path, thread_ts=ts)
            os.remove(save_path)
        except CobaltAPIError as e:
            print(e)

@app.event("message")
def ignore_message():
    pass

try:
    shutil.rmtree("output")
except FileNotFoundError:
    pass
os.mkdir("output")
SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
