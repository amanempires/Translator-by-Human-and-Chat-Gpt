import streamlit as st
from googletrans import Translator
import base64
from gtts import gTTS
from io import BytesIO
import openai
import os
import speech_recognition as sr

LANGUAGES = {
    None: "Choose your Language", 'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic', 'hy': 'Armenian',
    'az': 'Azerbaijani', 'eu': 'Basque', 'be': 'Belarusian', 'bn': 'Bengali', 'bs': 'Bosnian',
    'bg': 'Bulgarian', 'ca': 'Catalan', 'ceb': 'Cebuano', 'ny': 'Chichewa', 'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)', 'co': 'Corsican', 'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish',
    'nl': 'Dutch', 'en': 'English', 'eo': 'Esperanto', 'et': 'Estonian', 'tl': 'Filipino', 'fi': 'Finnish',
    'fr': 'French', 'fy': 'Frisian', 'gl': 'Galician', 'ka': 'Georgian', 'de': 'German', 'el': 'Greek',
    'gu': 'Gujarati', 'ht': 'Haitian Creole', 'ha': 'Hausa', 'haw': 'Hawaiian', 'iw': 'Hebrew', 'hi': 'Hindi',
    'hmn': 'Hmong', 'hu': 'Hungarian', 'is': 'Icelandic', 'ig': 'Igbo', 'id': 'Indonesian', 'ga': 'Irish',
    'it': 'Italian', 'ja': 'Japanese', 'jv': 'Javanese', 'kn': 'Kannada', 'kk': 'Kazakh', 'km': 'Khmer',
    'ko': 'Korean', 'ku': 'Kurdish (Kurmanji)', 'ky': 'Kyrgyz', 'lo': 'Lao', 'la': 'Latin', 'lv': 'Latvian',
    'lt': 'Lithuanian', 'lb': 'Luxembourgish', 'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay',
    'ml': 'Malayalam', 'mt': 'Maltese', 'mi': 'Maori', 'mr': 'Marathi', 'mn': 'Mongolian', 'my': 'Myanmar (Burmese)',
    'ne': 'Nepali', 'no': 'Norwegian', 'ps': 'Pashto', 'fa': 'Persian', 'pl': 'Polish', 'pt': 'Portuguese',
    'pa': 'Punjabi', 'ro': 'Romanian', 'ru': 'Russian', 'sm': 'Samoan', 'gd': 'Scots Gaelic', 'sr': 'Serbian',
    'st': 'Sesotho', 'sn': 'Shona', 'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak', 'sl': 'Slovenian',
    'so': 'Somali', 'es': 'Spanish', 'su': 'Sundanese', 'sw': 'Swahili', 'sv': 'Swedish', 'tg': 'Tajik',
    'ta': 'Tamil', 'te': 'Telugu', 'th': 'Thai', 'tr': 'Turkish', 'uk': 'Ukrainian', 'ur': 'Urdu',
    'uz': 'Uzbek', 'vi': 'Vietnamese', 'cy': 'Welsh', 'xh': 'Xhosa', 'yi': 'Yiddish', 'yo': 'Yoruba', 'zu': 'Zulu'
}

feedback = ['Best', "Good", "Average", "Worse"]
openai.api_key = ""

class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

session_state = SessionState(translated_text=None, detected_lang_name=None)


@st.cache_data(hash_funcs={BytesIO: id})
def translate(text, target_lang):
    try:
        translator = Translator()
        detected_lang = translator.detect(text).lang
        translated_text = translator.translate(text, src=detected_lang, dest=target_lang)
        detected_lang_name = LANGUAGES.get(detected_lang, "Unknown")
        
        # Get language code
        lang_code = target_lang[:2].lower()
        
        # Convert translated text to MP3 audio
        tts = gTTS(translated_text.text, lang=lang_code, slow=False)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        
        return translated_text.text, detected_lang_name, audio_bytes.getvalue(), lang_code
    except Exception as e:
        return None, None, None, None

@st.cache(hash_funcs={BytesIO: id})
def get_binary_file_downloader_html(bin_file, file_label='File', button_text='Download'):
    """
    Generate a link to download the given binary file.
    :param bin_file: The binary file data.
    :param file_label: The label to display for the file.
    :param button_text: The text to display on the download button.
    :return: A string representing the HTML code for the download link and button.
    """
    bin_str = base64.b64encode(bin_file).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}">{button_text}</a>'
    return href

def main():
    st.title("Voice Message Portal")
    folder_path = "E:\\voice" 
    st.subheader("Choose your Input option")
    text_input_option = st.radio("",("Type your Query", "Type your Query by voice"))
    if text_input_option == "Type your Query":
        original_query = st.text_area("",placeholder="Write Your Queryyy......")
    else:
        st.write("Please select Target language and press the Translate button and speak")
    st.subheader("Translate your Data")
    target_lang_name = st.selectbox("Select your Sending Language", list(LANGUAGES.values()))
    if st.button("Translate"):
        if text_input_option == "Type your Query by voice":
            r = sr.Recognizer()
            try:
                with sr.Microphone() as source:
                    st.write("Speak now...")
                    audio_data = r.listen(source)
                original_query = r.recognize_google(audio_data)
                st.write("Message recorded:", original_query)
            except sr.UnknownValueError:
                st.warning("Could not understand audio.")
                original_query = ""
            except sr.RequestError as e:
                st.error("Could not request results; {0}".format(e))
                original_query = ""
            except Exception as e:
                st.error(f"An error occurred: {e}")
                original_query = ""
        name=original_query[:7]
        st.subheader("Original Query ")
        st.write(original_query)
        if original_query and target_lang_name:
            translated_text, detected_lang_name, audio_bytes, lang_code = translate(original_query, target_lang_name)
            session_state.translated_text = translated_text 
            session_state.detected_lang_name = detected_lang_name
            if translated_text is not None:
                st.subheader(f"Translated Text (Original Language: {detected_lang_name})")
                st.write(translated_text)
                pdf_data = translated_text.encode('utf-8')
                b64_pdf = base64.b64encode(pdf_data).decode('utf-8')
                href_pdf = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="E:\\voice{name}.pdf">Download Translated Text as PDF</a>'
                st.markdown(href_pdf, unsafe_allow_html=True)
                if audio_bytes:
                    b64_audio = base64.b64encode(audio_bytes).decode('utf-8')
                    href_audio = f'<a href="data:audio/mpeg;base64,{b64_audio}" download="E:\\voice{name}.mp3" download>Download Translated Text as Audio</a>'
                    st.markdown(href_audio, unsafe_allow_html=True)
                    
                if translated_text:
                    translated_text += "Give me the correct syntax and Elaborate\n"
                    improved_query_result = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content":translated_text}],
                        max_tokens=2000,
                        temperature=0.5
                    )
                    if improved_query_result and improved_query_result.choices:
                        improved_query = improved_query_result.choices[0].message["content"]
                        st.subheader("Query Improvement by the Gpt")
                        st.write(improved_query)
                        pdf_data1 = improved_query.encode('utf-8')
                        b64_pdf1 = base64.b64encode(pdf_data1).decode('utf-8')
                        href_pdf1 = f'<a href="data:application/octet-stream;base64,{b64_pdf1}" download="{name}.pdf">Download Improved Translated Text as PDF</a>'
                        st.markdown(href_pdf1, unsafe_allow_html=True)

                        tts1 = gTTS(improved_query, lang=lang_code, slow=False)
                        audio_bytes1 = BytesIO()
                        tts1.write_to_fp(audio_bytes1)
                        b64_audio1 = base64.b64encode(audio_bytes1.getvalue()).decode('utf-8')
                        href_audio1 = f'<a href="data:audio/mpeg;base64,{b64_audio1}" download="{name}.mp3" download>Download Improved Translated Text as Audio</a>'
                        st.markdown(href_audio1, unsafe_allow_html=True)
                    else:
                        st.warning("Query improvement failed. Please try again.")
            else:
                st.error("Translation failed. Please try again with different text.")
        else:
            st.warning("Please enter text and select a target language.")

    st.subheader("All Files in your Folder")
    num = 1
    if folder_path and os.path.isdir(folder_path):
        file_list = os.listdir(folder_path)
        for file_name in file_list:
            st.write(num, file_name)
            file_path = os.path.join(folder_path, file_name)
            if file_name.lower().endswith('.mp3'):
                with open(file_path, "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format='audio/mp3')
            elif file_name.lower().endswith('.pdf'):
                pass
            num += 1

if __name__ == "__main__":
    main()
