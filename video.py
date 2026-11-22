import os
import requests
import time
import ffmpeg
from pathlib import Path

MAX_ATTEMPTS = 4

def download_video(
    out_path: str, video_url: str, iteration: int
) -> str | None:
    if video_url is None or video_url == "":
        return None

    time.sleep(4.0)

    local_filename = "iteration_" + str(iteration) + "_raw." + video_url.split('?')[0].split('.')[-1]
    download_video_path = out_path + "/" + local_filename
    os.makedirs(Path(download_video_path).parent, exist_ok=True)

    video_name = "iteration_" + str(iteration) + '.mp4'
    video_path = Path(download_video_path).parent / video_name

    sleep_time = 1.0
    download_success = False
    download_attempts = 0
    while download_attempts < MAX_ATTEMPTS:
        try:
            with requests.get(video_url, stream=True) as r:
                r.raise_for_status()
                with open(download_video_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

                stream = ffmpeg.input(download_video_path)
                stream = ffmpeg.output(stream, str(video_path))
                ffmpeg.run(stream, quiet=True, overwrite_output=True)

                os.remove(download_video_path)
                download_success = True
                break
        except ffmpeg.Error as e:
            print("Video conversion failed:", e.stderr.decode(errors="replace") if e.stderr else str(e))
            time.sleep(sleep_time)
            sleep_time *= 2.0
        except Exception as e:
            print("Video download failed:", str(e))
            time.sleep(sleep_time)
            sleep_time *= 2.0
        finally:
            download_attempts += 1

    if not download_success:
        return None

    return video_name

