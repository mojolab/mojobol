
import asyncio
import time
import speech_recognition as sr
from os import path
from pydub import AudioSegment
import gtts
from googletrans import Translator
from playsound import playsound
import openai
import os
import threading


#create a async function that transcibes audio
async def transcribe(path):


# convert mp3 file to wav
    sound = AudioSegment.from_mp3(path)
    sound.export("transcript.wav", format="wav")


    # transcribe audio file
    AUDIO_FILE = "transcript.wav"

    # use the audio file as the audio source
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
            audio = r.record(source)  # read the entire audio file

    #return text from audio file asnycronously
    print("Transcription done : "+r.recognize_google(audio))
    return r.recognize_google(audio)


async def translate(text,lang="en"):
    #translate text to english
    
    translator = Translator()
    print("Translation done "+translator.translate(text, dest=lang).text)
    return  translator.translate(text, dest=lang).text


#ask chat gpt using openai module

async def askchat_gpt(text):
    openai.api_key=''
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=[{"role": "user", "content": text}])
    print("Chat done "+response.choices[0].message.content)
    return response.choices[0].message.content

def play_audio(path):
    playsound(path)  
     
def play_audio_loop(path):
        global stop_flag
        stop_flag=False
    
        while True:

            playsound(path) 
            if stop_flag:
                 break


async def read_text(text):
    #read text given in form of a string
    tts = gtts.gTTS(text, lang='hi')
    print("Text to speech started with text "+text )
    try:
        tts.save("text.mp3")
    except:
         #delete the file if it exists
        if path.exists("text.mp3"):
            os.remove("text.mp3")
            tts.save("text.mp3")    


    
    print("Text to speech done")
    playsound("text.mp3")


async def workflow(path):
     # Play audio in a separate thread
     
    audio_thread = threading.Thread(target=play_audio_loop, args=("wait.wav",))
    audio_thread.start()


    text=await transcribe(path)
    en_text=await translate(text)
    response=await askchat_gpt(en_text)
    hi_text=await translate(response,"hi")
    global stop_flag
    stop_flag=True
    audio_thread.join()

    
    await read_text(hi_text)
    print("done")

asyncio.run(workflow("poshan.wav"))
     
