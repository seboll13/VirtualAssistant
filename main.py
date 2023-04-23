import os
import openai
import speech_recognition as sr

openai.api_key_path = 'api_key.txt'
STD_ERROR_MESSAGE   = "Could not understand audio"


def audio_to_text(file) -> str:
    """Converts audio file to text using Google Speech Recognition"""
    recogniser = sr.Recognizer()
    with sr.AudioFile(file) as source:
        audio = recogniser.record(source)
    try:
        return recogniser.recognize_google(audio)
    except sr.UnknownValueError:
        return STD_ERROR_MESSAGE


def generate_response(prompt) -> str:
    """Sends text to OpenAI API and returns response"""
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=512,
        temperature=0.5,
        top_p=1,
        stop=None,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text


def speak_text(text) -> None:
    """Converts text to speech using Google Text-to-Speech"""
    os.system(f'gtts-cli "{text}" | mpg123 -')


def engage_conversation(recogniser) -> None:
    """Engages a new conversation with the VA"""
    speak_text('What can I do for you ?')
    with sr.Microphone() as source:
        audio = recogniser.listen(source)
        try:
            text = recogniser.recognize_google(audio)
            prompt = f'You are now a virtual assistant. The question is: "{text}". Your answer is: '
            print('Generating response...')
            response = generate_response(prompt)
            speak_text(response)
        except sr.UnknownValueError:
            print(STD_ERROR_MESSAGE)


def main():
    """Main function"""
    print("Say 'VA' to activate the virtual assistant")
    while True:
        with sr.Microphone() as source:
            recogniser = sr.Recognizer()
            audio = recogniser.listen(source)
            try:
                text = recogniser.recognize_google(audio)
                if text == "VA":
                    engage_conversation(recogniser)
                elif text == "exit":
                    print("Exiting...")
                    break
            except sr.UnknownValueError:
                print(STD_ERROR_MESSAGE)


if __name__ == "__main__":
    main()