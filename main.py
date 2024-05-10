import time
import requests
from PIL import Image
import argparse
import cv2
from os import get_terminal_size
from moviepy.editor import VideoFileClip
import playsound
import threading
import datetime

img = None

def get_total_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return total_frames


def get_total_duration(video_path):
    video = VideoFileClip(video_path)
    total_duration = video.duration
    video.close()
    return total_duration


def get_average_fps(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
    total_duration = cap.get(cv2.CAP_PROP_POS_MSEC)
    average_fps = total_frames / total_duration
    cap.release()
    return average_fps


def get_single_frame(video_path, frame_number):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if ret:
        global img
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        return img
    else:
        print("Failed to read frame")


parser = argparse.ArgumentParser('ytcli',description='Watch YouTube videos in the terminal!')
parser.add_argument('video_id',help='The YouTube video ID')
args = parser.parse_args()

r = requests.get(f'https://inv.us.projectsegfau.lt/latest_version?id={args.video_id}&itag=18')
if r.status_code != 200:
    exit()
with open('video.mp4', 'wb') as f:
    f.write(r.content)


def g_audio(filename, output):
    video = VideoFileClip(filename)
    audio = video.audio
    audio.write_audiofile(output)
    audio.close()
    video.close()


fps = get_average_fps("video.mp4")
g_audio("video.mp4", "audio.mp3")
x = threading.Thread(target=lambda: playsound.playsound("audio.mp3"))
x.start()
start = datetime.datetime.now()
tf = get_total_frames("video.mp4")
total_duration = get_total_duration("video.mp4")
for frame in range(tf):
    img = get_single_frame("video.mp4", frame)
    sz = get_terminal_size()
    img = img.resize((sz[0]-3, sz[1]*2-3))
    sz = img.size
    image_data = img.load()
    half_height = round(sz[1] * 0.5)

    print("\x1b[H", end='')
    for ii in range(half_height):
        for i in range(sz[0]):
            # Access pixel values directly from the image data
            c1 = image_data[i, ii * 2] if 0 <= i < sz[0] and 0 <= ii * 2 < sz[1] else None
            c2 = image_data[i, ii * 2 + 1] if 0 <= i < sz[0] and 0 <= ii * 2 + 1 < sz[1] else None
            color1 = c1 if c1 else (0, 0, 0)
            color2 = c2 if c2 else (0, 0, 0)

            print(f'\x1b[38;2;{color1[0]};{color1[1]};{color1[2]}m'
                  f'\x1b[48;2;{color2[0]};{color2[1]};{color2[2]}m▀\x1b[0m', end='')
        print('')

    # calculate elapsed time
    elapsed_time = (datetime.datetime.now() - start).total_seconds()

    # calculate target time for this frame
    target_time = total_duration * (frame + 1) / tf

    # calculate sleep time
    sleep_time = target_time - elapsed_time

    # sleep for calculated time
    if sleep_time > 0:
        time.sleep(sleep_time)


    print(frame, (datetime.datetime.now() - start), total_duration*230)

x.join()