@echo off

rem Print the argument for debugging
echo Starting experiment for participant: %1

rem Check if user ID is provided
if "%1"=="" (
    echo You must provide a user ID as an argument.
    exit /b
)

rem Start VLC to play a video in fullscreen
start "" /min "C:\Program Files\VideoLAN\VLC\vlc.exe" --fullscreen "C:\Users\rpa\OneDrive - Aalborg Universitet\Projects\FFR\Films\The Red Balloon 30Min.mp4"

rem Pass the user ID argument to the Python script
start "" "c:/FFR Experiment/FFR-Test/.conda/pythonw.exe" "c:/FFR Experiment/FFR-Test/main.py" %1

rem Exit the batch script
exit
