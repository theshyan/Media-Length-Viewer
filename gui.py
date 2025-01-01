import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QComboBox, QTextEdit, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from pymediainfo import MediaInfo
import os
import re
from tabulate import tabulate
from colorama import init

# Activates ANSI color support for Windows and automatically resets colors after each print.
init(autoreset=True)

class MovieInfoApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video File Info")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # dark mode
        self.setStyleSheet("background-color: #2e2e2e; color: white;")

        self.label_path = QLabel("Enter directory path:")
        layout.addWidget(self.label_path)

        self.entry_path = QLineEdit(self)
        self.entry_path.setFixedWidth(350)
        layout.addWidget(self.entry_path)

        self.label_sort = QLabel("Sort by:")
        layout.addWidget(self.label_sort)

        self.combo_box = QComboBox(self)
        self.combo_box.addItem("Length")
        self.combo_box.addItem("Year")
        self.combo_box.setCurrentIndex(0)
        self.combo_box.setFixedWidth(150)
        layout.addWidget(self.combo_box)

        self.button_show = QPushButton("Show Movies", self)
        self.button_show.clicked.connect(self.show_movies)
        layout.addWidget(self.button_show)

        self.text_box = QTextEdit(self)
        self.text_box.setStyleSheet("font-family: 'Courier'; font-size: 12pt; background-color: #444444; color: white;")
        layout.addWidget(self.text_box)

        self.entry_path.returnPressed.connect(self.show_movies)
        self.setLayout(layout)

    # Function to find all video files (.mkv, .mp4)
    def find_video_files(self, directory):
        video_extensions = (".mkv", ".mp4")
        video_path_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(video_extensions):
                    video_path_files.append(os.path.join(root, file))
        return video_path_files


    def get_video_info(self, file_path):
        media_info = MediaInfo.parse(file_path)
        track = next((t for t in media_info.tracks if t.track_type == "Video"), None)
        if track and track.duration:
            return float(track.duration) / 1000  # Convert duration from ms to sec
        return None


    def clean_movie_name(self, file):
        base_name = os.path.splitext(file)[0]
        # Regular expression to extract name and year
        match = re.search(r"(.+?)(?:\W|_)?(\d{4})(?:\W|_)?", base_name)
        if match:
            clean_name = match.group(1).replace(".", " ").strip()
            year = match.group(2)
            return clean_name, year
        return base_name.replace(".", " ").strip(), None

    def show_movies(self):
        input_path = self.entry_path.text().strip()

        if not input_path:
            self.text_box.setText("Please enter a valid directory path.")
            return

        input_path = input_path.strip()

        if not os.path.exists(input_path):
            self.text_box.setText("The provided directory does not exist.")
            return

        movies_data = []
        total_duration_in_sec = 0
        movies = self.find_video_files(input_path)

        if movies:
            for movie_path in movies:
                file_name = os.path.basename(movie_path)
                clean_name, year = self.clean_movie_name(file_name)
                length_in_sec = self.get_video_info(movie_path)

                if length_in_sec:
                    # Convert duration from seconds to HH:MM:SS
                    hour = int(length_in_sec // 3600)
                    minutes = int((length_in_sec % 3600) // 60)
                    seconds = int(length_in_sec % 60)
                    length = f"{hour:02}:{minutes:02}:{seconds:02}"

                    movies_data.append([clean_name, year or "Unknown", length])
                    total_duration_in_sec += length_in_sec
                else:
                    print(f"Couldn't retrieve length for {file_name}.")
        else:
            self.text_box.setText("No video files found in the specified directory.")
            return

        # Get the sorting criteria selected by the user (Length or Year)
        ask = self.combo_box.currentText()

        try:
            if ask == "Length":
                # Sort by movie length
                movies_data.sort(key=lambda x: x[2])

            elif ask == "Year":
                # Sort by year
                movies_data.sort(key=lambda x: int(x[1]) if x[1] != "Unknown" else -1)

        except IndexError:
            movies_data.sort(key=lambda x: int(x[1]) if x[1] != "Unknown" else -1)

        movies_data_with_index = [[i + 1] + movie for i, movie in enumerate(movies_data)]

        colored_movies_data = "<table border='1' cellpadding='5' cellspacing='0' style='width: 100%; font-family: Courier;'>"
        colored_movies_data += "<tr><th>#</th><th>Movie Name</th><th>Year</th><th>Length</th></tr>"

        for movie in movies_data_with_index:
            colored_movies_data += f"<tr><td style='color: yellow;'>{movie[0]}</td>"
            colored_movies_data += f"<td style='color: cyan;'>{movie[1]}</td>"
            colored_movies_data += f"<td style='color: darkorange;'>{movie[2]}</td>"
            colored_movies_data += f"<td style='color: lightgreen;'>{movie[3]}</td></tr>"

        # calculate the total duration of all movies
        total_hour = int(total_duration_in_sec // 3600)
        total_minutes = int((total_duration_in_sec % 3600) // 60)
        total_seconds = int(total_duration_in_sec % 60)
        total_length = f"{total_hour:02}:{total_minutes:02}:{total_seconds:02}"

        colored_movies_data += f"<tr><td colspan='3' style='color: yellow;'>Total</td>"
        colored_movies_data += f"<td style='color: lightpink;'>{total_length}</td></tr>"

        colored_movies_data += "</table>"

        self.text_box.setHtml(colored_movies_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MovieInfoApp()
    window.show()
    sys.exit(app.exec_())


