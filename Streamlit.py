# Importações necessárias para o streamlit, api do google, leitura em json, lottie e etc.
import streamlit as st
#Services
from services.chat import create_chat, send_message
from services.image import analyze_image
from services.pdf import extract_pdf_text, analyze_pdf
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


################ Configuração antiga do Gemini removida. ####################
################ A integração com o novo SDK será feita gradualmente. #######
#API_KEY = os.getenv("API_KEY");
#genai.configure(api_key = API_KEY);
#model = genai.GenerativeModel('gemini-3.8-flash')
#chat = client.chats.create(model=MODEL_NAME)

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

# Função para processar o envio de mensagem do chat
def process_chat_message(user_input):
    if user_input:
        try:
            response = send_message(
                st.session_state.gemini_chat,
                user_input
            )

            # Língua selecionada
            selected_language = st.session_state["selected_language"]

            pronome = "Você" if selected_language == "Português" else "You"

            st.session_state.messages.append((pronome, user_input))
            st.session_state.messages.append(("Gemini", response))

            update_chat_container()
            st.rerun()

        except Exception as error:
            st.error(f"Erro ao enviar mensagem: {error}")

    else:
        st.markdown(
            '<span id="erro">Por favor, digite alguma coisa.</span>',
            unsafe_allow_html=True
        )

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

if "messages" not in st.session_state:
    st.session_state.messages = []

if "gemini_chat" not in st.session_state:
    st.session_state.gemini_chat = create_chat()

with aba1:
    if selected_language == "Português":
        st.write("### Chat Bot:")
        st.write(" 📍 **Pergunte o que quiser!** Diga um oi, pergunte qual a origem da roupa branca no reveillon, por que o céu é azul?, deixe a criatividade rolar solta (não use o bot para consultas de pesquisas, vá atrás para confiar as informações, sempre bom ter uma fonte confiável);")
        st.markdown('<p class = aviso>Aviso: Dependendo da pergunta, o bot pode acrescentar muito texto e não enviar a resposta. Seja pontual. Se o bot der algum erro, peça para ele resumir a resposta, deve funcionar.</p>', unsafe_allow_html=True);

        chat_container = st.container()

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
    if "image_messages" not in st.session_state:
        st.session_state.image_messages = []

    if selected_language == "Português":
        st.write("### Análise de Imagens com IA")
        st.write("📍 **Envie uma imagem!**: Envie uma imagem e pergunte o que quiser sobre ela para a IA!")
        st.markdown(
            '<p class="aviso">Aviso: A IA lê imagens de até 20MB.</p>',
            unsafe_allow_html=True
        )

        upload_label = "Escolha uma imagem..."
        image_caption = "Imagem Enviada"
        initial_prompt = "Analise esta imagem"
        initial_message = "Analise esta imagem:"
        chat_placeholder = "Pergunte algo sobre a imagem..."
        user_label = "Você"

        st.caption(
            "💡 A análise pode levar alguns segundos, dependendo "
            "da complexidade da imagem e da disponibilidade do serviço."
        )
    else:
        st.write("### Image Review with AI")
        st.write("📍 **Upload an image!**: Upload an image and ask the AI anything about it!")
        st.markdown(
            '<p class="aviso">Note: AI supports uploads up to 20MB.</p>',
            unsafe_allow_html=True
        )

        upload_label = "Choose an image..."
        image_caption = "Uploaded Image"
        initial_prompt = "Analyze this image"
        initial_message = "Analyze this image:"
        chat_placeholder = "Ask something about the image..."
        user_label = "You"

        st.caption(
                    "💡 Analysis may take a few seconds depending on "
                    "image complexity and service availability."
                )

    uploaded_file = st.file_uploader(
        upload_label,
        type=["jpg", "jpeg", "png"],
        key="image_upload"
    )

    
    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()
        image_key = (uploaded_file.name, image_bytes)

        # Detecta quando uma nova imagem é enviada
        if st.session_state.get("current_image_key") != image_key:
            st.session_state.current_image_key = image_key
            st.session_state.image_messages = []
            st.session_state.image_analysis_attempted = False
            st.session_state.image_analysis_error = None

        image = Image.open(BytesIO(image_bytes))

        st.image(
            image,
            caption=image_caption,
            use_container_width=True
        )

        # Primeira tentativa de análise
        if not st.session_state.image_analysis_attempted:
            st.session_state.image_analysis_attempted = True

            loading_message = (
                    "Aguarde um instante, estou analisando sua imagem..."
                    if selected_language == "Português"
                    else "Please wait, I'm analyzing your image..."
                )

            with st.spinner(loading_message):
                try:
                    response = analyze_image(initial_prompt, image)

                    st.session_state.image_messages.append(
                        (user_label, f"{initial_message} {uploaded_file.name}")
                    )
                    st.session_state.image_messages.append(
                        ("Gemini", response)
                    )

                except Exception as error:
                    st.session_state.image_analysis_error = str(error)

        # Exibe erro e oferece nova tentativa
        if st.session_state.image_analysis_error:
            st.error(
                f"Não foi possível analisar a imagem: "
                f"{st.session_state.image_analysis_error}"
            )

            retry_label = (
                "🔄 Tentar novamente"
                if selected_language == "Português"
                else "🔄 Try again"
            )

            if st.button(retry_label, key="retry_image_analysis"):
                retry_loading_message = (
                    "Tentando novamente, aguarde..."
                    if selected_language == "Português"
                     else "Trying again, please wait..."
                    )

                with st.spinner(retry_loading_message):
                    try:
                        response = analyze_image(initial_prompt, image)

                        st.session_state.image_messages.append(
                            (user_label, f"{initial_message} {uploaded_file.name}")
                        )
                        st.session_state.image_messages.append(
                            ("Gemini", response)
                        )

                        st.session_state.image_analysis_error = None

                    except Exception as error:
                        st.session_state.image_analysis_error = str(error)

                st.rerun()

        # Só exibe o chat depois que a análise inicial funcionar
        if st.session_state.image_messages:

            chat_container = st.container()

            with chat_container:
                st.markdown(
                    '<div class="chat-container">',
                    unsafe_allow_html=True
                )

                for user, message in st.session_state.image_messages:
                    message_class = "user" if user == user_label else "bot"

                    st.markdown(
                        f'<div class="message {message_class}">'
                        f'<b>{user}:</b> {message}</div>',
                        unsafe_allow_html=True
                    )

                st.markdown('</div>', unsafe_allow_html=True)

            user_input = st.chat_input(
                chat_placeholder,
                key="image_user_input"
            )

            if user_input:
                chat_loading_message = (
                "Analisando sua pergunta..."
                  if selected_language == "Português"
                    else "Analyzing your question..."
                        )

                with st.spinner(chat_loading_message):
                    try:
                        response = analyze_image(user_input, image)

                        st.session_state.image_messages.append(
                            (user_label, user_input)
                        )
                        st.session_state.image_messages.append(
                            ("Gemini", response)
                        )

                        st.rerun()

                    except Exception as error:
                        st.error(f"Erro ao enviar mensagem: {error}")


#Agora na aba3, teremos alguns pontos similares ao da aba2, porém agora iremos analisar os textos contidos em um PDF,
#não trabalharemos com imagens. Além disso, precisamos converter o pdf para bytes.

with aba3:
    if "pdf_messages" not in st.session_state:
        st.session_state.pdf_messages = []

    if selected_language == "Português":
        st.write("### Análise de PDFs com IA")
        st.write(
            "📍 **Envie um arquivo PDF!**: Envie seu currículo, "
            "um livro ou uma revista e pergunte o que quiser sobre ele!"
        )
        st.markdown(
            '<p class="aviso">A IA analisará o texto do PDF, ignorando imagens. '
            'Certifique-se de que o documento esteja corretamente formatado.</p>',
            unsafe_allow_html=True
        )

        upload_label = "Escolha um PDF..."
        initial_prompt = "Analise este PDF"
        initial_message = "Analise este PDF:"
        chat_placeholder = "Pergunte algo sobre o PDF..."
        user_label = "Você"

        loading_message = "Aguarde um instante, estou analisando seu PDF..."
        chat_loading_message = "Analisando sua pergunta..."

    else:
        st.write("### PDF Analysis with AI")
        st.write(
            "📍 **Upload a PDF file!**: Send your resume, "
            "a book or a magazine and ask anything about it!"
        )
        st.markdown(
            '<p class="aviso">The AI will analyze the PDF text, ignoring images. '
            'Make sure your document is correctly formatted.</p>',
            unsafe_allow_html=True
        )

        upload_label = "Choose a PDF file..."
        initial_prompt = "Analyze this PDF"
        initial_message = "Analyze this PDF:"
        chat_placeholder = "Ask something about the PDF..."
        user_label = "You"

        loading_message = "Please wait, I'm analyzing your PDF..."
        chat_loading_message = "Analyzing your question..."

    st.caption(
        "💡 A análise pode levar alguns segundos, dependendo do tamanho do documento e da disponibilidade do serviço."
        if selected_language == "Português"
        else "💡 Analysis may take a few seconds depending on document size and service availability."
    )

    uploaded_file_pdf = st.file_uploader(
        upload_label,
        type=["pdf"],
        key="pdf_upload"
    )

    if uploaded_file_pdf is not None:
        pdf_bytes = uploaded_file_pdf.getvalue()
        pdf_key = (uploaded_file_pdf.name, pdf_bytes)

        # Detecta quando um novo PDF é enviado
        if st.session_state.get("current_pdf_key") != pdf_key:
            st.session_state.current_pdf_key = pdf_key
            st.session_state.pdf_messages = []
            st.session_state.pdf_analysis_attempted = False
            st.session_state.pdf_analysis_error = None
            st.session_state.pdf_text = None

        # Extrai o texto apenas uma vez por documento
        if st.session_state.pdf_text is None:
            try:
                st.session_state.pdf_text = extract_pdf_text(pdf_bytes)
            except Exception as error:
                st.session_state.pdf_analysis_error = str(error)

        if st.session_state.pdf_analysis_error:
            st.error(
                f"Não foi possível processar o PDF: "
                f"{st.session_state.pdf_analysis_error}"
            )

            if st.button(
                "Tentar novamente" if selected_language == "Português"
                else "Try again",
                key="retry_pdf_extraction"
            ):
                st.session_state.pdf_analysis_error = None
                st.session_state.pdf_text = None
                st.rerun()

        # Análise inicial do documento
        if (
            st.session_state.pdf_text
            and not st.session_state.pdf_analysis_attempted
        ):
            st.session_state.pdf_analysis_attempted = True

            with st.spinner(loading_message):
                try:
                    response = analyze_pdf(
                        initial_prompt,
                        st.session_state.pdf_text
                    )

                    st.session_state.pdf_messages.append(
                        (user_label, f"{initial_message} {uploaded_file_pdf.name}")
                    )
                    st.session_state.pdf_messages.append(
                        ("Gemini", response)
                    )

                except Exception as error:
                    st.session_state.pdf_analysis_error = str(error)

        # Exibe erro e oferece nova tentativa
        if st.session_state.pdf_analysis_error:
            st.error(
                f"Não foi possível analisar o PDF: "
                f"{st.session_state.pdf_analysis_error}"
            )

            retry_label = (
                "🔄 Tentar novamente"
                if selected_language == "Português"
                else "🔄 Try again"
            )

            if st.button(retry_label, key="retry_pdf_analysis"):
                st.session_state.pdf_analysis_error = None

                with st.spinner(loading_message):
                    try:
                        response = analyze_pdf(
                            initial_prompt,
                            st.session_state.pdf_text
                        )

                        st.session_state.pdf_messages.append(
                            (user_label, f"{initial_message} {uploaded_file_pdf.name}")
                        )
                        st.session_state.pdf_messages.append(
                            ("Gemini", response)
                        )

                    except Exception as error:
                        st.session_state.pdf_analysis_error = str(error)

                    else:
                        st.session_state.pdf_analysis_error = None

                st.rerun()

        # Chat disponível após a análise inicial
        if st.session_state.pdf_messages:
            chat_container = st.container()

            with chat_container:
                st.markdown(
                    '<div class="chat-container">',
                    unsafe_allow_html=True
                )

                for user, message in st.session_state.pdf_messages:
                    message_class = "user" if user == user_label else "bot"

                    st.markdown(
                        f'<div class="message {message_class}">'
                        f'<b>{user}:</b> {message}</div>',
                        unsafe_allow_html=True
                    )

                st.markdown('</div>', unsafe_allow_html=True)

            user_input = st.chat_input(
                chat_placeholder,
                key="pdf_user_input"
            )

            if user_input:
                with st.spinner(chat_loading_message):
                    try:
                        response = analyze_pdf(
                            user_input,
                            st.session_state.pdf_text
                        )

                        st.session_state.pdf_messages.append(
                            (user_label, user_input)
                        )
                        st.session_state.pdf_messages.append(
                            ("Gemini", response)
                        )

                        st.rerun()

                    except Exception as error:
                        st.error(f"Erro ao enviar mensagem: {error}")


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