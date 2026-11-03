import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
from streamlit_drawable_canvas import st_canvas
 
Expert=" "
profile_imgenh=" "
 
# Inicializar session_state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""
if 'base64_image' not in st.session_state:
    st.session_state.base64_image = ""
    
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."
 
 
# Streamlit 
st.set_page_config(page_title='Tablero Musical')

# ---------- ESTILO: ESTUDIO DE GRABACIÓN (CSS + SVG en línea, sin archivos extra) ----------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&family=Outfit:wght@400;500;600&display=swap');

:root {
    --night: #140B1F;
    --plum: #2A1640;
    --plum-2: #3A1F57;
    --gold: #F5B83D;
    --coral: #FF6B6B;
    --teal: #2EC4B6;
    --cream: #F6EBDD;
    --cream-dim: #CDBFD9;
    --ink: #2A1640;
}

html, body, [class*="css"], .stApp { font-family: 'Outfit', system-ui, sans-serif; }

/* Fondo: noche violeta con pentagramas dorados y focos de escenario */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: var(--night) !important;
    background-image:
        radial-gradient(ellipse at 50% -5%, rgba(245,184,61,0.22), transparent 50%),
        radial-gradient(ellipse at 100% 60%, rgba(255,107,107,0.12), transparent 45%),
        radial-gradient(ellipse at 0% 80%, rgba(46,196,182,0.10), transparent 45%),
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='110'%3E%3Cg stroke='%23F5B83D' stroke-opacity='.11' stroke-width='1'%3E%3Cline x1='0' y1='25' x2='40' y2='25'/%3E%3Cline x1='0' y1='35' x2='40' y2='35'/%3E%3Cline x1='0' y1='45' x2='40' y2='45'/%3E%3Cline x1='0' y1='55' x2='40' y2='55'/%3E%3Cline x1='0' y1='65' x2='40' y2='65'/%3E%3C/g%3E%3C/svg%3E");
    color: var(--cream) !important;
}
.block-container { padding-top: 1.6rem; max-width: 760px; }

header[data-testid="stHeader"] { background: transparent !important; }
header[data-testid="stHeader"] * { color: var(--gold) !important; fill: var(--gold) !important; }

.stApp p, .stApp label, .stApp li, .stApp h2,
[data-testid="stWidgetLabel"] p { color: var(--cream) !important; }

/* Encabezado */
.hero-art { display: flex; justify-content: center; }
.hero-art svg { width: 100%; max-width: 380px; height: auto; }
.spin { transform-origin: 180px 60px; animation: spin 9s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.stApp h1 {
    font-family: 'Fraunces', serif;
    text-align: center;
    color: var(--gold) !important;
    font-weight: 800;
    font-size: 2.6rem;
    letter-spacing: 0.01em;
    padding: 0.2rem 0 0.4rem 0;
    text-shadow: 0 0 24px rgba(245,184,61,0.45);
}
.stApp h3 {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    color: var(--cream) !important;
}
.stApp [data-testid="stMain"] h3 { text-align: center; font-size: 1.2rem; color: var(--cream-dim) !important; }

/* Barra lateral */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--plum), var(--night)) !important;
    border-right: 2px solid rgba(245,184,61,0.35);
}
[data-testid="stSidebar"] h3 { color: var(--gold) !important; text-align: left; font-size: 1.05rem; }
[data-testid="stSidebar"] * { color: var(--cream); }
[data-testid="stSidebarCollapseButton"] * { color: var(--gold) !important; }

/* Lienzo: se ve como una hoja de papel bajo un foco */
[data-testid="stCustomComponentV1"] iframe, iframe[title*="canvas"] {
    display: block;
    margin: 0.6rem auto;
    border-radius: 14px;
    box-shadow: 0 0 0 4px var(--gold), 0 14px 40px rgba(0,0,0,0.55), 0 0 50px rgba(245,184,61,0.25);
}

/* Slider */
[data-testid="stSlider"] [role="slider"] { background: var(--gold) !important; box-shadow: 0 0 12px var(--gold) !important; border: 2px solid var(--night) !important; }
[data-testid="stSliderThumbValue"], [data-testid="stSliderThumbValue"] *,
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"] { color: var(--gold) !important; }

/* Campo de clave */
[data-baseweb="input"], [data-baseweb="base-input"] {
    background: var(--plum) !important;
    border: 2px solid var(--plum-2) !important;
    border-radius: 14px !important;
}
[data-baseweb="input"]:focus-within { border-color: var(--gold) !important; box-shadow: 0 0 0 3px rgba(245,184,61,0.25) !important; }
[data-baseweb="input"] input { color: var(--cream) !important; background: transparent !important; }

/* Botones: oro, como un botón de REC */
.stButton > button {
    background: var(--gold) !important;
    border: none !important;
    border-radius: 999px !important;
    padding: 0.6rem 1.8rem;
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    font-size: 1.02rem;
    letter-spacing: 0.04em;
    box-shadow: 0 5px 0 #B9821A, 0 10px 22px rgba(245,184,61,0.3);
    transition: transform 0.12s ease, background 0.12s ease;
}
.stButton > button, .stButton > button p, .stButton > button span { color: var(--ink) !important; }
.stButton > button:hover { background: var(--coral) !important; transform: translateY(-2px); }
.stButton > button:active { transform: translateY(3px); box-shadow: 0 1px 0 #B9821A; }
.stButton > button:focus-visible { outline: 3px solid var(--cream) !important; outline-offset: 3px; }

/* Divisor */
[data-testid="stMain"] hr { border: none !important; height: 2px; background: repeating-linear-gradient(90deg, var(--gold) 0 10px, transparent 10px 20px) !important; opacity: 0.55; margin: 1.6rem 0; }

/* Letra de la canción: hoja de partitura */
.st-key-lyrics {
    background: var(--cream);
    border-left: 8px solid var(--gold);
    border-radius: 8px 22px 22px 8px;
    padding: 1.2rem 1.6rem;
    margin-top: 1rem;
    box-shadow: 0 12px 32px rgba(0,0,0,0.45);
}
.stApp .st-key-lyrics p, .stApp .st-key-lyrics * { color: var(--ink) !important; }
.stApp .st-key-lyrics p { font-family: 'Fraunces', serif; font-size: 1.05rem; line-height: 1.7; }

/* Avisos y spinner */
div[data-testid="stAlert"] { background: rgba(245,184,61,0.14) !important; border: 1px solid var(--gold); border-radius: 14px; }
div[data-testid="stAlert"] p, div[data-testid="stAlert"] * { color: var(--cream) !important; }
[data-testid="stSpinner"] * { color: var(--cream) !important; }

/* Ecualizador decorativo */
.eq { display: flex; justify-content: center; align-items: flex-end; gap: 6px; height: 46px; margin-top: 2rem; }
.eq span {
    width: 8px; height: 100%; border-radius: 4px 4px 0 0;
    background: linear-gradient(180deg, var(--gold), var(--coral));
    transform-origin: bottom;
    animation: bounce 1.1s ease-in-out infinite;
}
@keyframes bounce { 0%,100% { transform: scaleY(0.25); } 50% { transform: scaleY(1); } }

#MainMenu, footer { visibility: hidden; }

@media (prefers-reduced-motion: reduce) {
    .spin, .eq span { animation: none; }
    .eq span { transform: scaleY(0.6); }
    .stButton > button { transition: none; }
}
@media (max-width: 640px) { .stApp h1 { font-size: 2rem; } }
</style>

<div class="hero-art">
<svg viewBox="0 0 360 120" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Disco de vinilo con notas musicales">
  <g class="spin">
    <circle cx="180" cy="60" r="56" fill="#0D0816" stroke="#3A1F57" stroke-width="2"/>
    <g fill="none" stroke="#F5B83D" stroke-opacity=".18">
      <circle cx="180" cy="60" r="49"/><circle cx="180" cy="60" r="43"/><circle cx="180" cy="60" r="37"/><circle cx="180" cy="60" r="31"/><circle cx="180" cy="60" r="25"/>
    </g>
    <path d="M180 60 L226 34 A52 52 0 0 1 232 60Z" fill="#FFFFFF" opacity=".06"/>
    <circle cx="180" cy="60" r="19" fill="#F5B83D"/>
    <circle cx="180" cy="60" r="13" fill="none" stroke="#B9821A" stroke-width="1.5"/>
    <circle cx="180" cy="60" r="3.5" fill="#140B1F"/>
  </g>
  <g fill="#F5B83D">
    <g transform="translate(40 86)"><ellipse rx="8" ry="6" transform="rotate(-22)"/><rect x="6" y="-40" width="2.6" height="40"/><path d="M8.6 -40C20 -32 22 -22 16 -12C17 -22 13 -28 8.6 -30Z"/></g>
    <g transform="translate(86 62)" fill="#FF6B6B"><ellipse rx="7" ry="5" transform="rotate(-22)"/><rect x="5" y="-32" width="2.4" height="32"/></g>
    <g transform="translate(290 92)" fill="#2EC4B6"><ellipse rx="8" ry="6" transform="rotate(-22)"/><rect x="6" y="-40" width="2.6" height="40"/>
      <g transform="translate(34 -8)"><ellipse rx="8" ry="6" transform="rotate(-22)"/><rect x="6" y="-40" width="2.6" height="40"/></g>
      <polygon points="6,-40 48,-48 48,-40 6,-32"/></g>
    <g transform="translate(320 48)"><ellipse rx="6" ry="4.5" transform="rotate(-22)"/><rect x="4.5" y="-26" width="2.2" height="26"/><path d="M6.7 -26C14 -21 15 -15 11 -9C12 -15 9 -19 6.7 -20Z"/></g>
  </g>
</svg>
</div>
""",
    unsafe_allow_html=True,
)

st.title('🕯️ Tablero Musical')
with st.sidebar:
    st.subheader("Acerca de:")
    st.subheader("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto y convertirlo en una canción")
st.subheader("Dibuja el boceto en el panel y presiona el botón para analizarla")
 
# Add canvas component
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('Selecciona el ancho de línea', 1, 30, 5)
stroke_color = "#000000" 
bg_color = '#FFFFFF'
 
# Create a canvas component
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)
 
ke = st.text_input('Ingresa tu Clave', type="password")
os.environ['OPENAI_API_KEY'] = ke
 
# Retrieve the OpenAI API Key
api_key = os.environ['OPENAI_API_KEY']
 
# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)
 
analyze_button = st.button("Analiza la imagen", type="secondary")
 
# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if canvas_result.image_data is not None and api_key and analyze_button:
 
    with st.spinner("Analizando ..."):
        # Encode the image
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
        input_image.save('img.png')
        
        # Codificar la imagen en base64
        base64_image = encode_image_to_base64("img.png")
        st.session_state.base64_image = base64_image
            
        prompt_text = (f"Describe in spanish briefly the image")
    
        # Make the request to the OpenAI API
        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
              model= "gpt-4o-mini",
              messages=[
                {
                   "role": "user",
                   "content": [
                     {"type": "text", "text": prompt_text},
                     {
                       "type": "image_url",
                       "image_url": {
                         "url": f"data:image/png;base64,{base64_image}",
                       },
                     },
                   ],
                  }
                ],
              max_tokens=500,
              )
            
            if response.choices[0].message.content is not None:
                    full_response += response.choices[0].message.content
                    message_placeholder.markdown(full_response + "▌")
            
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)
            
            # Guardar en session_state
            st.session_state.full_response = full_response
            st.session_state.analysis_done = True
            
            if Expert== profile_imgenh:
               st.session_state.mi_respuesta= response.choices[0].message.content
    
        except Exception as e:
            st.error(f"An error occurred: {e}")
 
# Mostrar la funcionalidad de crear historia si ya se hizo el análisis
if st.session_state.analysis_done:
    st.divider()
    st.subheader(" ¿Te atreves a crear el nuevo hit mundial?")
    
    if st.button("Crear canción"):
        with st.spinner("Creando el nuevo hit mundial..."):
            story_prompt = (
                f"Basándote en esta descripción: '{st.session_state.full_response}', "
                "escribe en español la letra de una canción breve. "
                "Debe ser coherente y rimar."
            )
            
            story_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": story_prompt}],
                max_tokens=700,
            )
            
            with st.container(key="lyrics"):
                st.markdown("**Tu Top hit:**")
                st.write(story_response.choices[0].message.content)
 
# Warnings for user action required
if not api_key:
    st.warning("Por favor ingresa tu API key.")

# Decoración final: ecualizador en CSS
st.markdown(
    '<div class="eq" aria-hidden="true">'
    + "".join(
        f'<span style="animation-delay:{d}s;animation-duration:{t}s"></span>'
        for d, t in [(0,1.1),(0.2,0.9),(0.4,1.3),(0.1,1.0),(0.5,0.8),(0.3,1.2),(0.6,0.95),(0.15,1.15),(0.45,0.85),(0.25,1.05)]
    )
    + "</div>",
    unsafe_allow_html=True,
)
