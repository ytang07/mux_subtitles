import mux_python
from mux_config import token_id, secret_id

configuration = mux_python.Configuration()

configuration.username = token_id
configuration.password = secret_id

assets_api = mux_python.AssetsApi(mux_python.ApiClient(configuration))

add_captions = mux_python.CreateTrackRequest(url="https://assemblytests.s3.amazonaws.com/text_track.srt", type="text", text_type="subtitles", language_code="en-US", closed_captions=True, name="English")
# add_captions = mux_python.CreateTrackRequest(url="https://assemblytests.s3.amazonaws.com/text_track.vtt", type="text", text_type="subtitles", language_code="en-US", closed_captions=False, name="English")
input_settings = [mux_python.InputSettings(url='https://assemblytests.s3.amazonaws.com/xyz.mp4'), add_captions]
create_asset_request = mux_python.CreateAssetRequest(input=input_settings, playback_policy=[mux_python.PlaybackPolicy.PUBLIC],mp4_support='standard')
create_asset_response = assets_api.create_asset(create_asset_request)
print("Created Asset: " + str(create_asset_response))
assert create_asset_response != None
assert create_asset_response.data.id != None