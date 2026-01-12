## Installation:

Create a virtual environment and create the required packages:

```
conda create --name seagull_scarer python=3.13
conda activate seagull_scarer
pip install -r requirements.txt
```

Make sure to create a service account for Google's cloud vision API. You will need to provide the JSON file to the script for authentication. 

## Example Usage:

```
python play_sound.py audio_files/meow.mp3 test_images/seagull1.jpg "gulls,western gull,seabird" YOUR_SERVICE_ACCOUNT.json
```
