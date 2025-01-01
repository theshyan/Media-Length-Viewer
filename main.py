from pymediainfo import MediaInfo
from tabulate import tabulate
from termcolor import colored
from colorama import init
import os
import re

# Activates ANSI color support for Windows and automatically resets colors after each print.
init(autoreset=True)


def find_video_files(directory):
    """
        Searches the given directory and its subdirectories for video files
        with specified extensions (.mkv, .mp4).

        Args:
            directory (str): The root directory to search.
        Returns:
            list: List of full paths to video files.
    """
    video_extensions = (".mkv", ".mp4")
    video_path_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(video_extensions):
                video_path_files.append(os.path.join(root, file))

    return video_path_files


def get_video_info(file_path):
    """
        Extracts the duration of a video file.

        This function parses the given video file and extracts the duration
        in seconds.

        Args:
            file_path (str): The full path to the video file.
        Returns:
            float: Duration of the video in seconds, or None if the duration
    """
    media_info = MediaInfo.parse(file_path)
    track = next((t for t in media_info.tracks if t.track_type == "Video"), None)

    if track and track.duration:
        return float(track.duration) / 1000
    return None

# تابع برای تمیز کردن نام فایل و استخراج سال
def clean_movie_name(file):
    """
        Cleans the movie name and extracts the year.

        This function takes a movie file name, removes unwanted characters,
        and attempts to extract the year (if present). It returns the cleaned
        movie name and the extracted year.

        Args:
            file (str): The movie file name (with extension).
        Returns:
            tuple: A tuple containing the cleaned movie name and the year (if found).
            If no year is found, the second element of the tuple will be None.
    """
    base_name = os.path.splitext(file)[0]
    match = re.search(r"(.+?)(?:\W|_)?(\d{4})(?:\W|_)?", base_name)

    if match:
        clean_name = match.group(1).replace(".", " ").strip()
        year = match.group(2)
        return clean_name, year

    # if can't found Year
    return base_name.replace(".", " ").strip(), None

# take path from user
input_path = input("Enter the directory path:\n(like: f:\\Movies)\n> ").strip()


movies_data = []
total_duration_in_sec = 0

if os.path.exists(input_path):
    movies = find_video_files(input_path)

    if movies:
        for movie_path in movies:
            file_name = os.path.basename(movie_path)
            clean_name, year = clean_movie_name(file_name)

            length_in_sec = get_video_info(movie_path)

            if length_in_sec:
                # Convert the duration to the format HH:MM:SS
                hour = int(length_in_sec // 3600)
                minutes = int((length_in_sec % 3600) // 60)
                seconds = int(length_in_sec % 60)
                length = f"{hour:02}:{minutes:02}:{seconds:02}"

                movies_data.append([clean_name, year or "Unknown", length])

                # Total Length
                total_duration_in_sec += length_in_sec
            else:
                print(f"Couldn't retrieve length for {file_name}.")
    else:
        print("No video files found in the specified directory.")
else:
    print("The provided directory does not exist.")


if movies_data:
    ask = input('Show By "Length" or "Year: [L / Y]": ').upper()

    try:
        if ask[0] == "L":
            # sorting by Length
            movies_data.sort(key=lambda x: x[2])
            print("\nMovies sorted by Length:")

        elif ask[0] == "Y":
            # sorting by Year
            movies_data.sort(key=lambda x: int(x[1]) if x[1] != "Unknown" else -1)
            print("\nMovies sorted by Year:")

    except IndexError:
        # Handle the case where the input is empty
        movies_data.sort(key=lambda x: int(x[1]) if x[1] != "Unknown" else -1)
        print("\nMovies sorted by Year:")

    # Add an index (count) to the data
    movies_data_with_index = [[i+1] + movie for i, movie in enumerate(movies_data)]

    # add colors
    colored_movies_data = []
    for movie in movies_data_with_index:
        movie_row = [
            colored(str(movie[0]), 'yellow'),
            colored(movie[1], 'cyan'),
            colored(movie[2], 'magenta'),
            colored(movie[3], 'green')
        ]
        colored_movies_data.append(movie_row)

    total_hour = int(total_duration_in_sec // 3600)
    total_minutes = int((total_duration_in_sec % 3600) // 60)
    total_seconds = int(total_duration_in_sec % 60)
    total_length = f"{total_hour:02}:{total_minutes:02}:{total_seconds:02}"

    colored_movies_data.append([
        colored("Total", 'yellow'),
        colored("Total Length", 'cyan'),
        "",
        colored(total_length, 'green')
    ])

    print(tabulate(colored_movies_data, headers=["#", "Movie Name", "Year", "Length"], tablefmt="grid"))
