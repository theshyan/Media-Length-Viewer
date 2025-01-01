import os
import re
from pymediainfo import MediaInfo
from termcolor import colored
from tabulate import tabulate

# to find mp3 files
def find_audio_files(directory):
    audio_extensions = (".mp3",)
    audio_path_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(audio_extensions):
                audio_path_files.append(os.path.join(root, file))

    return audio_path_files


# for extract file data
def get_audio_info(file_path):
    media_info = MediaInfo.parse(file_path)
    track = next((t for t in media_info.tracks if t.track_type == "Audio"), None)

    if track and track.duration:
        return float(track.duration) / 1000
    return None


# take path from user
input_path = input("Enter the directory path:\n(like: f:\\Music)\n> ").strip()

music_data = []
total_duration_in_sec = 0

if os.path.exists(input_path):
    music_files = find_audio_files(input_path)

    if music_files:
        for music_path in music_files:
            file_name = os.path.basename(music_path)

            length_in_sec = get_audio_info(music_path)

            if length_in_sec:
                # convert to HH:MM:SS
                hour = int(length_in_sec // 3600)
                minutes = int((length_in_sec % 3600) // 60)
                seconds = int(length_in_sec % 60)
                length = f"{hour:02}:{minutes:02}:{seconds:02}"

                music_data.append([file_name, length])

                total_duration_in_sec += length_in_sec
            else:
                print(f"Couldn't retrieve length for {file_name}.")
    else:
        print("No audio files found in the specified directory.")
else:
    print("The provided directory does not exist.")

if music_data:
    # sorting by length
    music_data.sort(key=lambda x: x[1])

    colored_music_data = []
    for i, music in enumerate(music_data, start=1):
        colored_music_data.append([
            colored(str(i), 'yellow'),
            colored(music[0], 'cyan'),
            colored(music[1], 'green')
        ])

    total_hour = int(total_duration_in_sec // 3600)
    total_minutes = int((total_duration_in_sec % 3600) // 60)
    total_seconds = int(total_duration_in_sec % 60)
    total_length = f"{total_hour:02}:{total_minutes:02}:{total_seconds:02}"

    colored_music_data.append([
        colored("Total", 'yellow'),
        colored("Total Length", 'cyan'),
        colored(total_length, 'green')
    ])

    print(tabulate(colored_music_data, headers=["#", "Music Name", "Length"], tablefmt="grid"))
