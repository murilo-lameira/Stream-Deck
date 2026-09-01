import asyncio
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winrt.windows.storage.streams import Buffer

async def test():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    if current_session:
        info = await current_session.try_get_media_properties_async()
        
        if info.thumbnail:
            stream = await info.thumbnail.open_read_async()
            size = stream.size
            buffer = Buffer(size)
            await stream.read_async(buffer, size, 0) # 0 is InputStreamOptions.None
            
            # Extract bytes
            try:
                b = bytes(buffer)
                print(f"Success! Read {len(b)} bytes.")
                with open("test_thumb.jpg", "wb") as f:
                    f.write(b)
            except Exception as e:
                print("Failed to convert buffer to bytes:", e)
                
                # alternative: 
                try:
                    from winrt.windows.storage.streams import DataReader
                    reader = DataReader.from_buffer(buffer)
                    b2 = reader.read_buffer(size)
                    print(b2)
                except Exception as e2:
                    print(e2)
        else:
            print("No thumbnail found.")
    else:
        print("No media playing")

asyncio.run(test())

