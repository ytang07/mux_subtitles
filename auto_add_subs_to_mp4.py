import boto3
import mux_python
import requests
from time import sleep
from mux_config import auth_key, token_id, secret_id
from botocore.exceptions import ClientError
from aws_config import access_key, secret_key

def s3_upload(filename, bucket):
    s3_client = boto3.client('s3', 
        aws_access_key_id = access_key, 
        aws_secret_access_key = secret_key)
    try:
        response = s3_client.upload_file(filename, bucket, filename)
        s3_client.put_object_acl(ACL='public-read', Bucket=bucket, Key=filename)
    except ClientError as e:
        print("Error")
    # "https://assemblytests.s3.amazonaws.com/xyz.mp4"
    _url = f"https://{bucket}.s3.amazonaws.com/{filename}"
    print(f"Uploaded to {_url}")
    return _url

def transcribe_video(video_url):
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
    with open("text_track.srt", "w") as _file:
        _file.write(srt_response.text)

    vtt_endpoint = polling_endpoint + "/vtt"
    vtt_response = requests.get(vtt_endpoint, headers=headers)
    with open("text_track.vtt", "w") as _file:
        _file.write(vtt_response.text)

def upload_to_mux(track_url, video_url):
    configuration = mux_python.Configuration()

    configuration.username = token_id
    configuration.password = secret_id

    assets_api = mux_python.AssetsApi(mux_python.ApiClient(configuration))

    if ".srt" in track_url:
        add_captions = mux_python.CreateTrackRequest(url=track_url, type="text", text_type="subtitles", language_code="en-US", closed_captions=True, name="English")
    elif ".vtt" in track_url:
        add_captions = mux_python.CreateTrackRequest(url="https://assemblytests.s3.amazonaws.com/text_track.vtt", type="text", text_type="subtitles", language_code="en-US", closed_captions=False, name="English")
    else:
        print("Only .srt and .vtt file types are supported")
    input_settings = [mux_python.InputSettings(url=video_url), add_captions]
    create_asset_request = mux_python.CreateAssetRequest(input=input_settings, playback_policy=[mux_python.PlaybackPolicy.PUBLIC],mp4_support='standard')
    create_asset_response = assets_api.create_asset(create_asset_request)
    print("Created Asset: " + str(create_asset_response))
    assert create_asset_response != None
    assert create_asset_response.data.id != None

video = input("Where is your video located?")
bucket = input("What is the name of your public S3 bucket?")

if "https://" not in video:
    video = s3_upload(video, bucket)

transcribe_video(video)
_format = input("Would you like srt or vtt format?")
if "srt" in _format:
    _track_url = s3_upload("text_track.srt", bucket)
elif "vtt" in _format:
    _track_url = s3_upload("text_track.vtt", bucket)

upload_to_mux(_track_url, video)