# Importações necessárias para o streamlit, api do google, leitura em json, lottie e etc.
import streamlit as st
#Services
from services.chat import create_chat, send_message
from services.image import analyze_image
from services.pdf import extract_pdf_text, analyze_pdf
from services.audio import process_audio
from PIL import Image
import json
from io import BytesIO
from streamlit_lottie import st_lottie #Import de arquivos lottie animados
import html


# Padrão da página como centralizado
st.set_page_config(layout="centered")

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


# Função para processar o envio de mensagem do chat
def process_chat_message(user_input):
    if user_input:
        try:
            response = send_message(
                st.session_state.gemini_chat,
                user_input
            )

            # Língua selecionada
            st.session_state.messages.append(("user", user_input))
            st.session_state.messages.append(("assistant", response))

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
                    [data-testid="main-menu-list"] { background-color: #D7D5CD;} [data-testid="stImageCaption"] {color: black} p,li,ul,h3,h1,h2,button { color: black; } [data-testid="stAppViewContainer"] h1 {
    color: #222222 !important;
}</style>''', unsafe_allow_html=True)
        
    elif color == "Padrão": 
        st.markdown("""
                    <style>
                        [data-testid="stAppViewContainer"] {
                            background-color: #0E1117 !important;
                        }
        
                        [data-testid="stHeader"] {
                            background-color: #0E1117 !important;
                        }
        
                        [data-testid="stSidebar"],
                        [data-testid="stSidebarContent"] {
                            background-color: #161B22 !important;
                        }
        
                        [data-testid="stAppViewContainer"] h1,
                        [data-testid="stAppViewContainer"] h2,
                        [data-testid="stAppViewContainer"] h3,
                        [data-testid="stAppViewContainer"] p,
                        [data-testid="stAppViewContainer"] label {
                            color: #E6EDF3 !important;
                        }
                    </style>
                """, unsafe_allow_html=True)

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
        st.write("📍 **Pergunte o que quiser!** Diga um oi, pergunte qual a origem da roupa branca no réveillon, por que o céu é azul? Deixe a criatividade rolar solta (não use o bot para consultas de pesquisas, vá atrás para conferir as informações; sempre é bom ter uma fonte confiável).")

        st.markdown(
            '<p class="aviso">Aviso: Dependendo da pergunta, o bot pode acrescentar muito texto e não enviar a resposta. Seja pontual. Se o bot der algum erro, peça para ele resumir a resposta, deve funcionar.</p>',
            unsafe_allow_html=True
        )

        chat_container = st.container()

        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)

            for user, message in st.session_state.messages:
                message_class = "user" if user == "user" else "bot"
                display_name = "Você" if user == "user" else "Gemini"
                safe_message = html.escape(str(message))

                st.markdown(
                    f'<div class="message {message_class}"><b>{display_name}:</b> {safe_message}</div>',
                    unsafe_allow_html=True
                )

            st.markdown('</div>', unsafe_allow_html=True)

        user_input = st.chat_input("Diga alguma coisa...", key="user_input")

        if user_input:
            with st.spinner("Processando..."):
                process_chat_message(user_input)

        st.markdown(
            "<div id='chat-area' style='overflow-y: auto; max-height: 500px;'></div>",
            unsafe_allow_html=True
        )

    elif selected_language == "English":
        st.write("### Chat Bot:")
        st.write("📍 **Ask anything you want!** Say hello, ask where white clothes on New Year's Eve come from, why the sky is blue, and let your creativity run wild.")

        st.markdown(
            '<p class="aviso">Note: Depending on the question, the bot may add a lot of text and fail to send the response. Be concise. If the bot gives an error, ask it to summarize the response.</p>',
            unsafe_allow_html=True
        )

        chat_container = st.container()

        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)

            for user, message in st.session_state.messages:
                message_class = "user" if user == "user" else "bot"
                display_name = "You" if user == "user" else "Gemini"
                safe_message = html.escape(str(message))

                st.markdown(
                    f'<div class="message {message_class}"><b>{display_name}:</b> {safe_message}</div>',
                    unsafe_allow_html=True
                )

            st.markdown('</div>', unsafe_allow_html=True)

        user_input = st.chat_input("Write something...", key="user_input")

        if user_input:
            with st.spinner("Processing..."):
                process_chat_message(user_input)

        st.markdown(
            "<div id='chat-area' style='overflow-y: auto; max-height: 500px;'></div>",
            unsafe_allow_html=True
        )


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
    if "audio_result" not in st.session_state:
        st.session_state.audio_result = None

    if "audio_error" not in st.session_state:
        st.session_state.audio_error = None

    if selected_language == "Português":
        st.write("### Análise de Áudio")
        st.write(
            "📍 **Envie um áudio!**: Envie um áudio e faça perguntas "
            "sobre seu conteúdo. Quer um resumo de um áudio de 10 minutos? Experimente!"
        )
        st.markdown(
            '<p class="aviso">O áudio deve conter falas para obter os melhores resultados. '
            'Arquivos com apenas ruídos ou música podem não produzir uma análise adequada.</p>',
            unsafe_allow_html=True
        )

        prompt_label = "Digite sua questão sobre o áudio:"
        prompt_placeholder = "Ex.: Me resuma esse áudio."
        upload_label = "Envie seu arquivo de áudio"
        button_label = "Processar áudio"
        loading_message = "Processando áudio..."
        result_label = "Resposta:"
        error_message = "Não foi possível processar o áudio:"

    else:
        st.write("### Audio Review")
        st.write(
            "📍 **Upload an audio file!**: Upload audio and ask questions "
            "about its content. Want a summary of a 10-minute recording? Give it a try!"
        )
        st.markdown(
            '<p class="aviso">Audio containing speech generally produces the best results. '
            'Files containing only noise or music may not produce a useful analysis.</p>',
            unsafe_allow_html=True
        )

        prompt_label = "Enter your question about the audio:"
        prompt_placeholder = "E.g., Summarize this audio."
        upload_label = "Upload your audio file"
        button_label = "Process audio"
        loading_message = "Processing audio..."
        result_label = "Response:"
        error_message = "Unable to process audio:"

    st.caption(
        "💡 O processamento pode levar alguns segundos, dependendo do tamanho do áudio e da disponibilidade do serviço."
        if selected_language == "Português"
        else "💡 Processing may take a few seconds depending on audio size and service availability."
    )

    user_prompt = st.text_input(
        prompt_label,
        placeholder=prompt_placeholder,
        key="audio_prompt"
    )

    audio_file = st.file_uploader(
        upload_label,
        type=["wav", "mp3"],
        key="audio_upload"
    )

    if audio_file is not None:
        audio_bytes = audio_file.getvalue()
        audio_key = (audio_file.name, audio_bytes)

        # Detecta quando um novo áudio é enviado
        if st.session_state.get("current_audio_key") != audio_key:
            st.session_state.current_audio_key = audio_key
            st.session_state.audio_result = None
            st.session_state.audio_error = None

        mime_type = (
            "audio/mpeg"
            if audio_file.name.lower().endswith(".mp3")
            else "audio/wav"
        )

        st.audio(audio_bytes, format=mime_type)

        if st.button(button_label, key="process_audio_button"):
            prompt = user_prompt.strip()

            if not prompt:
                prompt = (
                    "Analise este áudio, apresente sua transcrição e faça um resumo."
                    if selected_language == "Português"
                    else "Analyze this audio, provide its transcription and summarize it."
                )

            with st.spinner(loading_message):
                try:
                    response = process_audio(
                        audio_bytes,
                        mime_type,
                        prompt
                    )

                    st.session_state.audio_result = response
                    st.session_state.audio_error = None

                except Exception as error:
                    st.session_state.audio_error = str(error)
                    st.session_state.audio_result = None

        if st.session_state.audio_error:
            st.error(
                f"{error_message} {st.session_state.audio_error}"
            )

        if st.session_state.audio_result:
            st.text_area(
                result_label,
                value=st.session_state.audio_result,
                height=300,
                key="audio_result_display"
            )


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