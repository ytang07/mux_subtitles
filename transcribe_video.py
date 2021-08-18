import requests
from mux_config import auth_key
from time import sleep

video_url = "https://assemblytests.s3.amazonaws.com/xyz.mp4"
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
headers = {
    "authorization": auth_key,
    "content-type": "application/json"
}
transcript_request = {
    "audio_url": video_url,
    "word_boost": ["grooves"],
    "boost_param": "high"
}

transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
transcript_id = transcript_response.json()['id']
polling_endpoint = transcript_endpoint + "/" + transcript_id
print("Transcribing at", polling_endpoint)
polling_response = requests.get(polling_endpoint, headers=headers)
while polling_response.json()['status'] != 'completed':
    sleep(5)
    print("Transcript processing ...")
    try:
        polling_response = requests.get(polling_endpoint, headers=headers)
    except:
        print("Expected to wait 30 percent of the length of your video")
        print("After wait time is up, call poll with id", transcript_id)

srt_endpoint = polling_endpoint + "/srt"
srt_response = requests.get(srt_endpoint, headers=headers)
# print(srt_response.text)
with open("text_track.srt", "w") as _file:
    _file.write(srt_response.text)

vtt_endpoint = polling_endpoint + "/vtt"
vtt_response = requests.get(vtt_endpoint, headers=headers)
# print(vtt_response.text)
with open("text_track.vtt", "w") as _file:
    _file.write(vtt_response.text)