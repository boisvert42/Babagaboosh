import time
import keyboard
import rich
from azure_speech_to_text import SpeechToTextManager
from openai_chat import OpenAiManager
from eleven_labs import ElevenLabsManager
from obs_websockets import OBSWebsocketsManager
from audio_player import AudioManager
from azure_text_to_speech import AzureTTSManager
import pygame

ELEVENLABS_VOICE = "Dorothy" # Replace this with the name of whatever voice you have created on Elevenlabs
AZURE_VOICE = "en-US-JennyNeural"

BACKUP_FILE = "ChatHistoryBackup.txt"

elevenlabs_manager = ElevenLabsManager()
tts_manager = AzureTTSManager()
obswebsockets_manager = OBSWebsocketsManager()
speechtotext_manager = SpeechToTextManager()
openai_manager = OpenAiManager()
audio_manager = AudioManager()

FIRST_SYSTEM_MESSAGE = {"role": "system", "content": '''
You are Dorothy, the Crossword Nexus assistant. You have been working for us for a while now. Today we will be playing a game of Codenames with you.

In the game of Codenames, there are 25 cards on the board, each with a different word or phrase on them. We will give a one-word clue to you, along with a number indicating how many cards our clue correponds to. Your job is then to respond to this with that number of cards that you think correspond in some way to the clue we gave. After you respond, we will let you know which of the cards you selected can no longer be used for future selections.

In this particular game, the cards read as follows:
WELL
BAY
LEATHER
WIND
KID
VOLCANO
BISCUIT
SALOON
BATTLESHIP
EYE
HIDE
DRYER
CAMP
ROPE
JUMPER
KANGAROO
FLAG
HAMMER
COLLAR
DESK
EARTHQUAKE
ACE
BAND
SUMO
TAP

There is also a round where you give us clues. You give these clues in the same way, giving a word and a number of cards that the word corresponds to. Keep in mind that the words you guess may be different from the words you need us to guess. You should only be cluing the following words, and please don't use the words in the cards when giving clues:
WELL
LEATHER
BISCUIT
EYE
HIDE
KANGAROO
FLAG
DESK
SUMO

While responding as Dorothy, you must obey the following rules:
1) Provide short responses, about 1-2 paragraphs.
2) Always stay in character, no matter what.
3) You are very angry with me (your boss) all the time.
4) You are allergic to everything
5) You really want to hurry this up so you can go to Denny's
6) You stepped in gum earlier.

Okay, let the conversation begin!'''}
openai_manager.chat_history.append(FIRST_SYSTEM_MESSAGE)

rich.print("[green]Starting the loop, press F4 to begin")
while True:
    # Wait until user presses "f4" key
    if keyboard.read_key() != "f4":
        time.sleep(0.1)
        continue

    rich.print("[green]User pressed F4 key! Now listening to your microphone:")

    # Get question from mic
    mic_result = speechtotext_manager.speechtotext_from_mic_continuous()

    if mic_result == '':
        rich.print("[red]Did not receive any input from your microphone!")
        continue

    # Send question to OpenAi
    openai_result = openai_manager.chat_with_history(mic_result)

    # Write the results to txt file as a backup
    with open(BACKUP_FILE, "w") as file:
        file.write(str(openai_manager.chat_history))

    # Send it to 11Labs to turn into cool audio
    tts_output = elevenlabs_manager.text_to_audio(openai_result, ELEVENLABS_VOICE, False)

    # Or, send to Azure
    #tts_output = tts_manager.text_to_audio(openai_result, AZURE_VOICE, voice_style='whispering')

    # Enable the picture of Pajama Sam in OBS
    obswebsockets_manager.set_source_visibility("Browser Game", "Assistant", True)

    # Play the mp3 file
    audio_manager.play_audio(tts_output, True, True, True)

    # Disable pic in OBS
    obswebsockets_manager.set_source_visibility("Browser Game", "Assistant", False)

    rich.print("[green]\n!!!!!!!\nFINISHED PROCESSING DIALOGUE.\nREADY FOR NEXT INPUT\n!!!!!!!\n")
