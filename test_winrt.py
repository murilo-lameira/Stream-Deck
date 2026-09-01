import asyncio
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionPlaybackStatus

async def test():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    if current_session:
        info = await current_session.try_get_media_properties_async()
        playback_info = current_session.get_playback_info()
        status = playback_info.playback_status
        is_playing = (status == GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING)
        
        print("Title:", info.title)
        print("Artist:", info.artist)
        print("SourceApp:", current_session.source_app_user_model_id)
        print("IsPlaying:", is_playing)
    else:
        print("No media playing")

asyncio.run(test())

