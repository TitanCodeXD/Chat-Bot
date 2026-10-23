# Importações necessárias para o streamlit, api do google, leitura em json, lottie e etc.
import streamlit as st
import requests
from PIL import Image
import google.generativeai as genai
import PIL.Image
import pathlib
import tqdm
import os
import time
import json
import fitz
import tempfile
import PyPDF2
from io import BytesIO
from streamlit_lottie import st_lottie #Import de arquivos lottie animados
from dotenv import load_dotenv

# Padrão da página como centralizado
st.set_page_config(layout="centered")

# Carregando arquivo .env (variáveis de ambiente) e pegando nossa KEY da API
load_dotenv()

API_KEY = os.getenv("API_KEY");
genai.configure(api_key = API_KEY);
model = genai.GenerativeModel('gemini-3.8-flash')
chat = model.start_chat(history=[])

messages = []
image_messages = []
pdf_messages = []

### Variáveis Globais de state
if "selected_language" not in st.session_state:
    st.session_state["selected_language"] = "English"

if "selected_font_size" not in st.session_state:
    st.session_state["selected_font_size"] = "Medium"

if "selected_background" not in st.session_state:
    st.session_state["selected_background"] = "Padrão"

if "selected_background_messages" not in st.session_state:
    st.session_state["selected_background_messages"] = "Padrão"

# Importando pasta de CSS para estilizações globais
def local_css(file_name):
    with open(file_name) as f:
        
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("./styles.css");

############# FUNÇÕES 
def set_language(language):
    st.session_state["selected_language"] = language
    #st.rerun() apenas para testes

# Função para atualizar o container
def update_chat_container():
    chat_message_html = f"""<div id="chat-area">{''.join([f'<div class="message {message_class}"><b>{user}:</b> {message}</div>' for user, message in messages])}</div>"""
    # Exibe as mensagens no Streamlit
    st.markdown(chat_message_html, unsafe_allow_html=True)

        
# Função para processar o envio de mensagem do chat
def process_chat_message(user_input):
    if user_input:
        response = chat.send_message(user_input)

        # Lingua selecionada
        selected_language = st.session_state["selected_language"]

        if selected_language == "Português": 
            pronome = "Você"
        else:
            pronome = "You"
        st.session_state.messages.append((pronome, user_input))
        st.session_state.messages.append(("Gemini", response.text))
        update_chat_container()
        st.rerun()
    else:
        st.markdown('<span id="erro">Por favor, digite alguma coisa.</span>', unsafe_allow_html=True)

# Função para alterar tamanho da fonte do site, útil para acessibilidade
def set_font_size(font_size):
    if font_size == "Small":
        st.markdown('<style>body { font-size: small; } p { font-size: small; } h1,h3 {font-size: 22px;}</style>', unsafe_allow_html=True)
    elif font_size == "Medium":
        st.markdown('<style>body { font-size: medium; } p,li,h3,ul,h1 { font-size: medium; }</style>', unsafe_allow_html=True)
    elif font_size == "Large":
        st.markdown('<style>body { font-size: large; } h3,h1 { font-size: 45px; } p {font-size: 30px;} p.aviso {font-size: 27px}</style>', unsafe_allow_html=True)

# Função para alterar a cor do background do site, útil para acessibilidade
def set_background(color):
    if color == "Branco":
        st.markdown('''<style> [data-testid="stSidebarContent"] { background-color: #D7D5CD; } [data-testid="stAppViewContainer"] { background-color: white;} 
                    [data-testid="stHeader"] { background-color: white;}  [data-testid="stSidebarCollapseButton"] { background-color: #D7D5CD;} [data-testid="stMainMenu"] { background-color: #D7D5CD;} 
                    [data-testid="main-menu-list"] { background-color: #D7D5CD;} [data-testid="stImageCaption"] {color: black} p,li,ul,h3,h1,h2,button { color: black; }</style>''', unsafe_allow_html=True)
        
    elif color == "Padrão": 
        st.markdown('<style></style>', unsafe_allow_html=True)

# Função para alterar a cor do background das mensagens, útil para acessibilidade
def set_background_messages(color_message):
    if color_message == "Branco e Preto":
        st.markdown('<style> div.message.user { background-color: white; color: black} div.message.bot{ background-color: black;}</style>', unsafe_allow_html=True)
        
    elif color_message == "Padrão": 
        st.markdown('<style></style>', unsafe_allow_html=True)

    elif color_message == "Azul Claro e Roxo":
        st.markdown('<style> div.message.user { background-color: #85D4FD; color: black} div.message.bot{ background-color: purple;} </style>', unsafe_allow_html=True)
    
    elif color_message == "Azul Claro e Cinza":
        st.markdown('<style> div.message.user { background-color: #3797f0; color: white} div.message.bot{ background-color: gray;} </style>', unsafe_allow_html=True)
  
### Nessa próximas duas funções foi referenciado de um projeto similiar que também foi usado áudios com 
#inteligência artificial, então bastou analisar e moldar conforme a necessidade
# Função para processar o áudio enviado
def process_audio(audio_file_path, user_prompt):
        model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
        audio_file = genai.upload_file(path=audio_file_path)
        response = model.generate_content(
            [
                user_prompt,
                audio_file
            ]
        )
        return response.text

# Função para salvar o arquivo de áudio temporariamente
def save_uploaded_file(uploaded_file):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.' + uploaded_file.name.split('.')[-1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                return tmp_file.name
        except Exception as e:
            st.error(f"Error: {e}")
            return None
######## Sidebars - Filtros

#Linguagem
with st.sidebar:
    language_options = ["English", "Português"]
    st.markdown('''<style> [data-testid="stMarkdownContainer"] h1 { font-size: 45px; text-shadow: 2px -2px #466EFF; }</style>''', unsafe_allow_html=True)
    st.sidebar.title('SETTINGS ⚙️')

    with open('./img/Animation.json') as f:
        lottie_animation = json.load(f)
    
    st_lottie(lottie_animation)

    selected_language = st.selectbox("LINGUAGEM 🌎", language_options)

    if selected_language != st.session_state["selected_language"]:
        set_language(selected_language)

#Fontes
with st.sidebar:
    font_size_options = ["Medium", "Small", "Large"]
    selected_font_size = st.selectbox("Font Size 🔍", font_size_options)
    st.sidebar.markdown("---")
    
    if selected_font_size != st.session_state["selected_font_size"]:
        set_font_size(selected_font_size)

#Background Color
with st.sidebar:
    background_options = ["Padrão", "Branco"]
    selected_background = st.radio(" Background 🎨", background_options)

    if selected_background != st.session_state["selected_background"]:
        set_background(selected_background)

#Message-Colors
with st.sidebar:
    background_options_messages = ["Padrão", "Branco e Preto", "Azul Claro e Roxo", "Azul Claro e Cinza"]
    selected_background_messages = st.radio(" Background Messages 🎨", background_options_messages)
    st.sidebar.markdown("---")
    st.image('./img/gemini.png', caption='Powered by Gemini AI')

    if selected_background_messages != st.session_state["selected_background_messages"]:
        set_background_messages(selected_background_messages)





#### Começo das páginas e utilização do Bot

# stSidebarContent
st.title("Chat Bot 🤖💭 ")

#Mudando linguagem da aba conforme o filtro
if selected_language == "Português":
        aba1, aba2, aba3, aba4, aba5 = st.tabs(['Chat Bot Geral','Análise de Imagens','Análise de PDFs', 'Análise de Áudio', 'Sobre']);
elif selected_language == "English":
        aba1, aba2, aba3, aba4, aba5 = st.tabs(['Chat Bot Geral','Image Review','PDFs Review', 'Audio Review', 'About']);

with aba1:
    if selected_language == "Português":
        st.write("### Chat Bot:")
        st.write(" 📍 **Pergunte o que quiser!** Diga um oi, pergunte qual a origem da roupa branca no reveillon, por que o céu é azul?, deixe a criatividade rolar solta (não use o bot para consultas de pesquisas, vá atrás para confiar as informações, sempre bom ter uma fonte confiável);")
        st.markdown('<p class = aviso>Aviso: Dependendo da pergunta, o bot pode acrescentar muito texto e não enviar a resposta. Seja pontual. Se o bot der algum erro, peça para ele resumir a resposta, deve funcionar.</p>', unsafe_allow_html=True);

        chat_container = st.container()

        if 'messages' not in st.session_state:
            st.session_state.messages = []

        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for user, message in st.session_state.messages:
                message_class = "user" if user == "Você" else "bot"
                st.markdown(f'<div class="message {message_class}"><b>{user}:</b> {message}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        user_input = st.chat_input("Diga alguma coisa... ", key = "user_input")
        if user_input:
            with st.spinner('Processando...'):
                process_chat_message(user_input);

        st.markdown("<div id='chat-area' style='overflow-y: auto; max-height: 500px;'></div>", unsafe_allow_html=True)
    elif selected_language == "English":
        st.write("### Chat Bot:")
        st.write(" 📍 **Ask anything you want!** Say hello, ask where the white clothes come from on New Year's Eve, why the sky is blue, let your creativity run wild (don't use the bot for research queries, go back and trust the information, it's always good to have a reliable source).")
        st.markdown('<p class = aviso>Note: Depending on the question, the bot may add a lot of text and not send the answer. Be punctual. If the bot gives an error, ask it to summarise the answer, it should works.</p>', unsafe_allow_html=True);

        chat_container = st.container()

        if 'messages' not in st.session_state:
            st.session_state.messages = []

        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for user, message in st.session_state.messages:
                message_class = "user" if user == "You" else "bot"
                st.markdown(f'<div class="message {message_class}"><b>{user}:</b> {message}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        user_input = st.chat_input("Write something... ", key = "user_input")

        if user_input:
            with st.spinner('Processing...'):
                process_chat_message(user_input);
        
        st.markdown("<div id='chat-area' style='overflow-y: auto; max-height: 500px;'></div>", unsafe_allow_html=True)


#Agora para a aba2, foi fundamental acessar a documentação do gemini, aqui precisamos alterar o modelo da IA, 
#para que possamos conversar enviando imagens. De resto, repitimos o processo da aba1
with aba2:  
 if selected_language == "Português":
    st.write("### Análise de Imagens com IA")
    st.write("📍 **Envie uma imagem!**: Envie uma imagem e pergunte o que quiser sobre ela para a IA!")
    st.markdown("<p class = aviso >Aviso: A IA lê imagens de até 20MB.</p>", unsafe_allow_html=True);

    model = genai.GenerativeModel('gemini-1.5-flash') ## para analisar as imagens, precisamos de outra versão do gemini
    uploaded_file = st.file_uploader("Escolha uma imagem...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Imagem Enviada', use_column_width=True)
        st.write("Analisando a imagem...")

        if 'image_messages' not in st.session_state:
            st.session_state.image_messages = []

        if len(st.session_state.image_messages) == 0:
            st.session_state.image_messages.append(("Você", f"Analise esta imagem: {uploaded_file.name}"))
            response = model.generate_content(["Analize esta imagem", image]) #Primeira pergunta padrão que será enviada, mas depois podemos fazer mais
            response.resolve()
            st.session_state.image_messages.append(("Gemini", response.text))

        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for user, message in st.session_state.image_messages:
                message_class = "user" if user == "Você" else "bot"
                st.markdown(f'<div class="message {message_class}"><b>{user}:</b> {message}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        user_input = st.chat_input("Pergunte algo sobre a imagem...", key="image_user_input")
        if user_input:
            st.session_state.image_messages.append(("Você", user_input))
            response = model.generate_content([user_input, image])
            response.resolve()
            st.session_state.image_messages.append(("Gemini", response.text))
            st.rerun()

 elif selected_language == "English":
    st.write("### Image Review with AI")
    st.write("📍 **Upload an image!**: Upload an image and ask the AI anything about it!")
    st.markdown("<p class = aviso>Note: IA supports up to 20MB upload</p>", unsafe_allow_html=True)

    model = genai.GenerativeModel('gemini-1.5-flash') ## para analisar as imagens, precisamos de outra versão do gemini
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], key = "image")
    if uploaded_file is not None:
        image = PIL.Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        st.write("Analyzing the image...")

        if 'image_messages' not in st.session_state:
            st.session_state.image_messages = []

        if len(st.session_state.image_messages) == 0:
            st.session_state.image_messages.append(("You", f"Analyze this image: {uploaded_file.name}"))
            response = model.generate_content(["Analyze this image", image])
            response.resolve()
            st.session_state.image_messages.append(("Gemini", response.text))

        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for user, message in st.session_state.image_messages:
                message_class = "user" if user == "You" else "bot"
                st.markdown(f'<div class="message {message_class}"><b>{user}:</b> {message}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        user_input = st.chat_input("Ask something about the image...", key="image_user_input")

        if user_input:
            st.session_state.image_messages.append(("You", user_input))
            response = model.generate_content([user_input, image])
            response.resolve()
            #response = chat.send_message(response1)
            st.session_state.image_messages.append(("Gemini", response.text))
            st.rerun()



#Agora na aba3, teremos alguns pontos similares ao da aba2, porém agora iremos analisar os textos contidos em um PDF,
#não trabalharemos com imagens. Além disso, precisamos converter o pdf para bytes.
with aba3:
  if selected_language == "Português":
    st.write("### Análise de PDFs com IA");
    st.write("📍 **Envie um arquivo PDF!**: Envie seu currículo, um livro, revista, e pergunte sobre ele para a IA, quer um resumo? um conselho? Teste agora!")
    st.markdown("<p class = aviso> Caso dê algum erro na leitura, tenha certeza que seu arquivo PDF esteja corretamente formatado. A IA irá ler o conteúdo do seu PDF, ignorando imagens.</p>", unsafe_allow_html=True);
    uploaded_file_pdf = st.file_uploader("Escolha um PDF...", type=["pdf"])
    
    if uploaded_file_pdf is not None:
        # O gmeini precisa fazer leitura em bytes, segundo a própria documentação, então vamos transformar o arquivo PDF em bytes
        pdf_bytes = BytesIO(uploaded_file_pdf.read())
        
        leitor_pdf = PyPDF2.PdfReader(pdf_bytes)

        num_paginas = len(leitor_pdf.pages)
        texto_completo = ""

        # Aqui vamos extrair o texto de cada página, ja que é assim que o gemini irá ler. Vamos só analisar texto, nada de imagens
        for num_pagina in range(num_paginas):
            pagina = leitor_pdf.pages[num_pagina]

            texto_pagina = pagina.extract_text()
            texto_completo += texto_pagina + "\n"

        # O melhor modelo do gemini para a leitura de textos em pdf
        model = genai.GenerativeModel('gemini-1.5-pro-latest')

        if 'pdf_messages' not in st.session_state:
            st.session_state.pdf_messages = []

        if len(st.session_state.pdf_messages) == 0:
            st.session_state.pdf_messages.append(("Você", f"Analise este PDF: {uploaded_file_pdf.name}"))
            response = model.generate_content([f"Analise este PDF", texto_completo])
            response.resolve()
            st.session_state.pdf_messages.append(("Gemini", response.text))

        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for user, message in st.session_state.pdf_messages:
                message_class = "user" if user == "Você" else "bot"
                st.markdown(f'<div class="message {message_class}"><b>{user}:</b> {message}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        user_input = st.chat_input("Pergunte algo sobre o PDF...", key="pdf_user_input")
        if user_input:
            st.session_state.pdf_messages.append(("Você", user_input))
            response = model.generate_content([user_input, texto_completo])
            response.resolve()
            st.session_state.pdf_messages.append(("Gemini", response.text))
            st.rerun()

    #Agora replicamos, mas trocando o idioma
  elif selected_language == "English":
    st.write("### PDF's Review with an IA");
    st.write("📍 **Send a PDF file!**: Send your resume/curriculum, a magazine, a book, ask about it to the IA, wants a summary? an advice? Try it now!")
    st.markdown("<p class = aviso> If there is an error when reading PDF file, make sure your file is correctly formatted. The AI will read the content of your PDF, ignoring images. </p>", unsafe_allow_html=True);
    uploaded_file_pdf = st.file_uploader("Choose a PDF File...", type=["pdf"])
    
    if uploaded_file_pdf is not None:
        pdf_bytes = BytesIO(uploaded_file_pdf.read())
        
        leitor_pdf = PyPDF2.PdfReader(pdf_bytes)

        num_paginas = len(leitor_pdf.pages)
        texto_completo = ""

        for num_pagina in range(num_paginas):
            pagina = leitor_pdf.pages[num_pagina]

            texto_pagina = pagina.extract_text()
            texto_completo += texto_pagina + "\n"

        model = genai.GenerativeModel('gemini-1.5-pro-latest')

        if 'pdf_messages' not in st.session_state:
            st.session_state.pdf_messages = []

        if len(st.session_state.pdf_messages) == 0:
            st.session_state.pdf_messages.append(("Você", f"Analise este PDF: {uploaded_file_pdf.name}"))
            response = model.generate_content([f"Analise este PDF", texto_completo])
            response.resolve()
            st.session_state.pdf_messages.append(("Gemini", response.text))

        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for user, message in st.session_state.pdf_messages:
                message_class = "user" if user == "Você" else "bot"
                st.markdown(f'<div class="message {message_class}"><b>{user}:</b> {message}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        user_input = st.chat_input("Pergunte algo sobre o PDF...", key="pdf_user_input")
        if user_input:
            st.session_state.pdf_messages.append(("Você", user_input))
            response = model.generate_content([user_input, texto_completo])
            response.resolve()
            st.session_state.pdf_messages.append(("Gemini", response.text))
            st.rerun()


# Nessa etapa de análise de áudios, foi necessário além de checar a documentação, consultar alguns projetos similares no github,
#pois estava ocasionando alguns problemas. Por fim deu tudo certo. Algumas partes parecidas com as abas anteriores.
with aba4:
  if selected_language == "Português":
    st.write("### Análise de Áudio");
    st.write("📍 **Envie um áudio!**:  Envie um áudio e faça alguma pergunte sobre ele, quer um resumo de um aúdio de 10 minutos? Teste !")
    st.markdown("<p class = aviso> O áudio deve conter falas, o bot irá principalmente analisar falas (que não contenham linguajar explícito/obscenidades!). Áudios que contenham barulhos/música, são prováveis a dar erro. </p>", unsafe_allow_html=True);

    user_prompt = st.text_input("Digite sua questão sobre o áudio:", placeholder="Que tal... 'Me resuma esse áudio'")

    audio_file = st.file_uploader("Envie seu arquivo", type=['wav', 'mp3'])
    if audio_file is not None:
        audio_path = save_uploaded_file(audio_file)
        st.audio(audio_path)

        if st.button('Processar!'):
            with st.spinner('Processando...'):
                processed_text = process_audio(audio_path, user_prompt)
                st.text_area("Resposta: ", processed_text, height=300)

  elif selected_language == "English":
    st.write("### Audio Review")
    st.write("📍 **Send an audio!**: Send an audio and ask a question about it, want a summary of a 10-minute audio? Try it out!")
    st.markdown("<p class = aviso> The audio must contain speech, the bot will mainly analyse speech (that doesn't contain explicit language/obscenities!). Audio that contains noise/music is likely to give an error. </p>", unsafe_allow_html=True);

    user_prompt = st.text_input("Enter your custom AI prompt:", placeholder="E.g., 'Please summarize the audio:'")

    audio_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3'])
    if audio_file is not None:
        audio_path = save_uploaded_file(audio_file)
        st.audio(audio_path)

        if st.button('Process Audio'):
            with st.spinner('Processing...'):
                processed_text = process_audio(audio_path, user_prompt)
                st.text_area("Processed Output", processed_text, height=300)


with aba5:
  # Conteúdo Dinâmico com Base no Idioma
  if selected_language == "Português":
    st.write("### Sobre");
    st.write("Este site foi contruido usando a biblioteca Streamlit do python através da API do Google Gemini, a inteligencia artificial do Google.")

    # Gemini
    st.image('./img/gemini.png', caption='Gemini AI')
    #Streamlit
    st.image('./img/Streamlit.png', caption='Streamlit Logo')

  elif selected_language == "English":
    st.write("### About");
    st.write("This site was built using the Streamlit python library via the Google Gemini API, Google's artificial intelligence.")
    
    #Gemini
    st.image('./img/gemini.png', caption='Gemini AI')

    #Streamlit
    st.image('./img/Streamlit.png', caption='Streamlit Logo')