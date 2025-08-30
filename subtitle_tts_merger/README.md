# Subtitle TTS Merger

This is a web-based application that allows you to merge Text-To-Speech (TTS) audio files with a video's subtitles. You can upload a video and a subtitle file (in SRT format), and then for each subtitle line, you can upload a corresponding TTS audio file. The application will then generate a single audio file where each TTS clip is placed at the correct start time and its speed is adjusted to fit the duration of the subtitle line.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You will need to have either Conda or Python with pip installed on your system.

*   **Conda:** You can install Conda by downloading and installing Anaconda or Miniconda from the official website.
*   **Python:** You can download and install Python from [python.org](https://python.org).

## Installation

You can set up the project environment using either `conda` or `pip`.

### Using `conda` (Recommended)

1.  **Clone the repository or download the project files.**

2.  **Create the Conda environment:** Open your terminal or Anaconda Prompt and navigate to the project directory. Then, run the following command to create a new Conda environment from the `environment.yml` file. This will install all the necessary dependencies.
    ```bash
    conda env create -f environment.yml
    ```

3.  **Activate the environment:**
    ```bash
    conda activate subtitle-merger-env
    ```

### Using `pip`

1.  **Clone the repository or download the project files.**

2.  **Create a virtual environment:** It is recommended to use a virtual environment to keep the project's dependencies isolated.
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    *   On Windows:
        ```bash
        venv\\Scripts\\activate
        ```
    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

Once you have installed the dependencies and activated the environment, you can run the application with the following command:

```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000` in your web browser.

## Building the Executable (for Windows)

You can also package the application into a standalone Windows executable (`.exe`) file.

1.  **Make sure you have installed the dependencies** as described in the Installation section.

2.  **Run the PyInstaller command:** In your terminal or command prompt, from the root of the project directory, run the following command:
    ```bash
    pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" app.py
    ```
    *Note: On Windows, the path separator for `--add-data` is a semicolon (`;`). If you are on macOS or Linux, you should use a colon (`:`).*

3.  **Find the executable:** After the command finishes, you will find a `dist` folder. Inside this folder, you will find the `app.exe` file. You can run this file to start the application.
