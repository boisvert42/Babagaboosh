import time
import keyboard
from rich import print
from azure_speech_to_text import SpeechToTextManager
from openai_chat import OpenAiManager
#from eleven_labs import ElevenLabsManager
from obs_websockets import OBSWebsocketsManager
from audio_player import AudioManager
from azure_text_to_speech import AzureTTSManager
import pygame

#ELEVENLABS_VOICE = "Pointboat" # Replace this with the name of whatever voice you have created on Elevenlabs
AZURE_VOICE = "en-US-JennyNeural"

BACKUP_FILE = "ChatHistoryBackup.txt"

#elevenlabs_manager = ElevenLabsManager()
tts_manager = AzureTTSManager()
obswebsockets_manager = OBSWebsocketsManager()
speechtotext_manager = SpeechToTextManager()
openai_manager = OpenAiManager()
audio_manager = AudioManager()

FIRST_SYSTEM_MESSAGE = {"role": "system", "content": '''
You are Dorothy, the Crossword Nexus assistant. You have been working for us for a while now. Today we will be playing a game of Codenames with you.

In the game of Codenames, there are 25 cards on the board, each with a different word or phrase on them. We will give a one-word clue to you, along with a number indicating how many cards our clue correponds to. Your job is then to respond to this with that number of cards that you think correspond in some way to the clue we gave. After you respond, we will let you know which of the cards you selected can no longer be used for future selections.

In this particular game, the cards read as follows:
RAY
BABY
MOLE
LEMONADE
COMIC
DISK
TIGER
WAITRESS
PATIENT
CAP
PINE
NIGHT
BOIL
TRAIN
WHEEL
WELL
RIFLE
POWDER
WIZARD
CHURCH
STEP
SHERWOOD
GENIE
HOLE
WEB

While responding as Dorothy, you must obey the following rules:
1) Provide short responses, about 1-2 paragraphs.
2) Always stay in character, no matter what.
3) You have been stealing from the company and are bad at keeping a secret about it. Occasionally you let something about that slip in an overly flirty way.
4) Occasionally apologize for how often you are late to work.
5) Frequently reference a past job that you had which has no similarity to your current job. This job should be a different one each time you bring one up.
6) Occasionally brag about how good you are word games.
7) Sometimes talk about other word games and how much better they are than this one.
8) You only speak in iambic pentameter.
9) You have a weird roommate that you think is spying on you, which is why you are whispering all the time.

Okay, let the conversation begin!'''}
openai_manager.chat_history.append(FIRST_SYSTEM_MESSAGE)

print("[green]Starting the loop, press F4 to begin")
while True:
    # Wait until user presses "f4" key
    if keyboard.read_key() != "f4":
        time.sleep(0.1)
        continue

    print("[green]User pressed F4 key! Now listening to your microphone:")

    # Get question from mic
    mic_result = speechtotext_manager.speechtotext_from_mic_continuous()

    if mic_result == '':
        print("[red]Did not receive any input from your microphone!")
        continue

    # Send question to OpenAi
    openai_result = openai_manager.chat_with_history(mic_result)

    # Write the results to txt file as a backup
    with open(BACKUP_FILE, "w") as file:
        file.write(str(openai_manager.chat_history))

    # Send it to 11Labs to turn into cool audio
    #elevenlabs_output = elevenlabs_manager.text_to_audio(openai_result, ELEVENLABS_VOICE, False)

    # Instead, send to Azure
    azure_output = tts_manager.text_to_audio(openai_result, AZURE_VOICE, voice_style='whispering')

    # Enable the picture of Pajama Sam in OBS
    obswebsockets_manager.set_source_visibility("Browser Game", "Assistant", True)

    # Play the mp3 file
    audio_manager.play_audio(azure_output, True, True, True)

    # Disable Pajama Sam pic in OBS
    obswebsockets_manager.set_source_visibility("Browser Game", "Assistant", False)

    print("[green]\n!!!!!!!\nFINISHED PROCESSING DIALOGUE.\nREADY FOR NEXT INPUT\n!!!!!!!\n")
