
import asyncio
import base64
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus
from winrt.windows.storage.streams import Buffer

async def media_monitor_task():
    try:
        title = ""
        artist = ""
        source_app = ""
        is_playing = False
        thumbnail_b64 = None
        
        if MediaManager:
            sessions = await MediaManager.request_async()
            current_session = sessions.get_current_session()
            if current_session:
                info = await current_session.try_get_media_properties_async()
                title = info.title
                artist = info.artist
                source_app = current_session.source_app_user_model_id
                
                if PlaybackStatus:
                    playback_info = current_session.get_playback_info()
                    is_playing = (playback_info.playback_status == PlaybackStatus.PLAYING)
                
                # Update thumbnail
                if info.thumbnail and Buffer:
                    try:
                        stream = await info.thumbnail.open_read_async()
                        size = stream.size
                        buffer = Buffer(size)
                        await stream.read_async(buffer, size, 0)
                        
                        b = bytes(buffer)
                        enc = base64.b64encode(b).decode("utf-8")
                        thumbnail_b64 = "data:image/jpeg;base64," + enc
                    except Exception as e:
                        print(f"Erro ao ler thumbnail: {e}")
        
        print("Title:", title)
        print("Artist:", artist)
        print("Source App:", source_app)
        print("Is Playing:", is_playing)
        print("Thumbnail Length:", len(thumbnail_b64) if thumbnail_b64 else 0)

    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(media_monitor_task())

