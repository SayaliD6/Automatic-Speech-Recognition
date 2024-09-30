import asyncio
import azure.cognitiveservices.speech as speechsdk
import uvicorn
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
app = FastAPI()
@app.websocket("/ws")
async def speech_recognize_continuous_async_from_microphone(websocket, path):
    done=False
    a=""
    connected = set()    
    connected.add(websocket)
    speech_config = speechsdk.SpeechConfig(subscription="8c393570a0ce4dde9c5429fd6ab4357c", region="uksouth")
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    done = False
    def recognizing_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        global a
        a= format(evt.result.text)    
        return a            
    def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):                 
        print(format(evt.result.text))  
    def stop_cb(evt: speechsdk.SessionEventArgs):            
        print('CLOSING on {}'.format(evt))
        nonlocal done
        done = True
        return a
    speech_recognizer.recognizing.connect(recognizing_cb)
    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)        
    result_future = speech_recognizer.start_continuous_recognition_async()
    result_future.get() 
    while not done:
        if ("stop" in a):   
            print('Stop',end="")
            speech_recognizer.stop_continuous_recognition_async()
            break 
        for conn in connected:
            await conn.send(f'{a}')
    print("recognition stopped.")
    return a

if __name__ == '__main__':
    uvicorn.run(app=app)
    start_server = websockets.serve(speech_recognize_continuous_async_from_microphone, "0.0.0.0", port=8000)
    # start_server = WebSocket.app(speech_recognize_continuous_async_from_microphone, "0.0.0.0", port=8000)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

   
    

    








