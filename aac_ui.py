import streamlit as st
from st_clickable_images import clickable_images
import ast
import random
import string 
import io
import os
from dotenv import load_dotenv
from google.cloud import texttospeech
import base64
from streamlit_extras.stylable_container import stylable_container
# Sample data representing the 42 items

import google.generativeai as genai
from image import text_to_image

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

client = texttospeech.TextToSpeechClient()

audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    speaking_rate=1
)

generation_config = {
"temperature": 0.9,
"top_p": 1,
"top_k": 0,
"max_output_tokens": 8192,
"response_mime_type": "text/plain",
}

voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Studio-O",
)


st.set_page_config(layout="wide")
model = genai.GenerativeModel(
model_name="gemini-1.5-flash",
generation_config=generation_config,

)


color = dict([((66, 11, 103, 255), "pink"), 
((2, 22, 115, 255), "lightblue"), 
((89, 0, 0, 255), "bisque"), 
((32, 109, 32, 255), "PaleTurquoise"), 
((19, 111, 129, 255), "powderblue"), 
((66, 11, 103, 255), "lavender"), 
])

def get_items(clicked_texts):
    # Replace this with your actual logic to compute the next set of items
    # For example, you might use `clicked_texts` to fetch new data or generate items
    sentence = ""
    
    response = model.generate_content([
        "input:  Give me most common words by with the sentence start for an individual, I am building AAC app, so give me 24 words which could be first word. Keep the words in a list and output the list only like ['word1', 'word2', ..]",
        "output: ",
        ])
    
    if clicked_texts is not None and len(clicked_texts) > 0:
        print("inside second word")
        sentence += " ".join(clicked_texts)
        response = model.generate_content([
        "input:  Context is AAC app, predict the next word for this incomplete sentence,{}. Give the most probable 24 words which could come next in english grammar of an individual. Keep the words in a list and output the list only like ['word1', 'word2', ..]".format(sentence),
        "output: ",
        ])

    start = response.text.find('[')
    end = response.text.find(']')

    # Extract the list
    word = response.text[start+1:end]
    word = word.strip()
    words = word.split(',')
    final_words = [x.strip() for x in words]
    
    final_words = [x[1:-1] if x.startswith("'") and x.endswith("'") else x for x in final_words]

    # Compute new items based on clicked_texts
    mycolor = random.choice(list(color.keys()))
    print("mycolor: ", mycolor)

    next_items = []

    for i in range(len(final_words)):
        mycolor = random.choice(list(color.keys()))
        next_items.append(
            {"id": i, "label": final_words[i], "image_url": "data:image/jpeg;base64,"+text_to_image(text=final_words[i], font_filepath="Supercarnival.ttf",color=mycolor), "color":mycolor}
        )
        
    return next_items


if "clicked_texts" not in st.session_state:
    st.session_state.clicked_texts = []


def on_click(label):
    print("my button label",label)
    st.session_state.clicked_texts.append(label)


def create_button_grid(items, columns=8):
    rows = len(items) // columns + (len(items) % columns > 0)

    with stylable_container(
        
        key="grey_button",
        css_styles="""
            button {
                background-color:gold;
                margin-top: 5px;
                border-radius: 20px;
            }
            
        """
    ):
        with stylable_container(
            key="container_with_border",
            css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 1rem;
                    background-color:   lightyellow;
                    padding: calc(1em - 1px)
                }
                """,
        ):
            for row in range(rows):
                cols = st.columns(columns)
                for col in range(columns):
                    idx = row * columns + col
                    if idx < len(items):
                        item = items[idx]
                        with cols[col]:
                            # Add a bordered container for each grid item
                            with st.container(border=True):
                            
                                bg_color = color[item['color']]
                                st.markdown(
                                    f"""
                                    <div style="border: 2px solid #ccc; border-radius: 10px; padding: 10px; text-align: center; background-color: {bg_color};">
                                        <img src="{item['image_url']}" style="width: 100%; height: auto;">
                                    </div>
                                    """,
                                
                                    unsafe_allow_html=True,
                                )
                            
                                st.button(
                                    item['label'], 
                                    key='button_'''.join(random.choices(string.ascii_lowercase +
                                        string.digits, k=10)),
                                    on_click=lambda label=item['label']: on_click(label),
                                    use_container_width=True
                                )


def text_to_speech(text):
    tts = gTTS(text)
    audio = io.BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)
    return audio

# Main function to display the grid
def main():
    print("inside main")
    items = get_items(st.session_state.clicked_texts)
    st.title("AAC tool for Nonverbal Autism using Gemini")
    
    st.markdown(
    """
    <style>
    textinput {
        font-size: 3rem !important;
    }
    input {
        font-size: 2rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

    st.text_input("", value=" ".join(st.session_state.clicked_texts), key="text_bar")

    if st.button("Genreate Audio of Text", type="primary",use_container_width=True ):
        text = st.session_state.clicked_texts
        if text:
            input_text = texttospeech.SynthesisInput(text=" ".join(text))
            response = client.synthesize_speech(
                request={"input": input_text, "voice": voice, "audio_config": audio_config}
            )
            st.audio(
                f"data:audio/mp3;base64,{base64.b64encode(response.audio_content).decode()}", format="audio/mp3"
            )
    
    #st.write("Click on any item:")
    create_button_grid(items)
    print("final output ", st.session_state.clicked_texts)


if __name__ == "__main__":
    main()