# rnow-dl

## For educational purposes only
This is not supported. Don't contact me to fix this if it's broken.

# You Assume all liability for using this.

### Config
- Add your bearer token to the config.ini
```ini
[DEFAULT]
# The Bearer token
TOKEN: Bearer xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

- Get the token by inspecting the web traffic and looking for a GET request to https://REDACTED/content/v1/content/739115/streaming-urls?encodingType=hls
- Right Click and copy headers
- Paste in notepad and copy the section 'Bearer xxxxxx' it's a really long string.
- If you don't copy the headers, paste them in notepad, and then copy them again the encoding in the config file will be incorrect.

### Run
- clone the repo
- install requirements `pip install -r requirements.txt`
- You will also need ffmpeg installed and in your path
- run `python main.py`
- This will ask you for a url, and will save the video file as mp4.

### Considerations
- You need a right now account for this
- Don't be stupid.