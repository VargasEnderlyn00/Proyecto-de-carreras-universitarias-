import streamlit as st
import google.generativeai as genai
from config import GEMINI_API_KEY
from translations import translations
import logging
from functools import lru_cache

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Configuración del modelo
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Iniciar sesión de chat
chat_session = model.start_chat(history=[])

# Diccionario de materias por país
subjects_by_country = {
    "México": ["Matemáticas", "Español", "Ciencias", "Historia", "Inglés"],
    "Venezuela": ["Matemáticas", "Castellano", "Ciencias Naturales", "Historia", "Inglés"],
    "España": ["Matemáticas", "Lengua Castellana y Literatura", "Ciencias Naturales", "Geografía e Historia", "Inglés"],
    "Colombia": ["Matemáticas", "Lenguaje", "Ciencias Naturales", "Ciencias Sociales", "Inglés"],
    "Estados Unidos": ["Math", "English", "Science", "Social Studies", "Foreign Language"],
    "Brasil": ["Matemática", "Português", "Ciências", "História", "Inglês"],
    "Italia": ["Matematica", "Italiano", "Scienze", "Storia", "Inglese"]
}

# Función para obtener sugerencias de IA (actualizada)
@lru_cache(maxsize=100)
def get_ai_suggestions(interests, skills, subject_grades_tuple, country, language, is_student):
    # Convertir la tupla de vuelta a un diccionario
    subject_grades = dict(subject_grades_tuple)
    
    # Convertir el rendimiento académico a una escala de 10 si es estudiante
    subjects_info = ""
    if is_student:
        if country == "México":
            subject_grades_10 = {subject: grade / 10 for subject, grade in subject_grades.items()}
        elif country == "Venezuela":
            subject_grades_10 = {subject: grade / 2 for subject, grade in subject_grades.items()}
        elif country in ["Colombia", "Estados Unidos"]:
            subject_grades_10 = {subject: grade * 2 for subject, grade in subject_grades.items()}
        elif country == "Brasil":
            subject_grades_10 = {subject: grade * 2.5 for subject, grade in subject_grades.items()}
        else:
            subject_grades_10 = subject_grades

        subjects_info = "\n".join([f"{subject}: {grade:.1f}/10" for subject, grade in subject_grades_10.items()])
    
    prompt = f"""
    Basándote en la siguiente información de {'un estudiante' if is_student else 'una persona'}, sugiere posibles trayectorias educativas y profesionales:
    
    Intereses: {interests}
    Habilidades: {skills}
    País: {country}
    {'Rendimiento académico (sistema de ' + country + '):' if is_student else ''}
    {subjects_info if is_student else ''}
    
    Por favor, proporciona 5-8 sugerencias de trayectorias educativas y profesionales que se ajusten al perfil {'del estudiante' if is_student else 'de la persona'} y sean relevantes para el mercado laboral en {country}.
    Para cada sugerencia, incluye:
    1. El nombre de la carrera o trayectoria profesional.
    2. Una breve explicación de por qué sería adecuada, considerando el contexto de {country}.
    3. El rango de ingresos aproximados que se pueden esperar en esta carrera en {country} (expresado en la moneda local y en dólares estadounidenses anuales).
    4. Los 2-3 trabajos más comunes o populares dentro de esta trayectoria profesional en {country}.

    Proporciona la respuesta en {language}.
    """
    
    try:
        response = chat_session.send_message(prompt)
        suggestions = response.text
        
        # Formatear las sugerencias para resaltar las carreras y los rangos de ingresos
        formatted_suggestions = ""
        suggestion_count = 0
        for line in suggestions.split('\n'):
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')):
                suggestion_count += 1
                career_name = line.split('.', 1)[1].strip()
                formatted_suggestions += f"<div class='career-suggestion'><h3>{suggestion_count}. <span style='font-size: 1.2em; font-weight: bold;'>{career_name}</span></h3>"
            elif "dólares" in line.lower():
                formatted_suggestions += f"<p class='income-range' style='color: #4CAF50 !important;'>{line.strip()}</p>"
            else:
                formatted_suggestions += f"<p>{line.strip()}</p>"
        
        formatted_suggestions += "</div>"
        return formatted_suggestions
    except Exception as e:
        logging.error(f"Error al obtener sugerencias de IA: {str(e)}")
        return translate("ai_error", language)

# Estilo CSS personalizado (actualizado)
st.markdown("""
<style>
body {
    height: 100vh;
    width: 100vw;
    background-color: black !important;
    background-attachment: fixed;
    background-size: cover;
}
.stApp {
    background-color: black !important;
}
.sidebar .sidebar-content {
    background-color: #333333 !important;
}
.sidebar .sidebar-content * {
    color: white !important;
}
.sidebar .sidebar-content a:hover {
    background-color: rgba(255, 255, 255, 0.2);
}
/* Nuevos estilos */
h1, h2, h3, p, label, .stTextArea label, .stSlider label, .stSelectbox label, .stRadio label {
    color: white !important;
}
.stSlider > div {
    color: #808080 !important;
}
.stButton > button {
    background-color: #4CAF50 !important;
    color: white !important;
    border: none !important;
    padding: 10px 24px !important;
    text-align: center !important;
    text-decoration: none !important;
    display: inline-block !important;
    font-size: 16px !important;
    margin: 4px 2px !important;
    cursor: pointer !important;
    border-radius: 4px !important;
}
.stButton > button:hover {
    background-color: #45a049 !important;
}
/* Estilos para los cuadros de entrada */
.stTextArea textarea, .stTextInput input, .stSelectbox select {
    background-color: #333333 !important;
    color: white !important;
    border: 1px solid #555555 !important;
}
.stSlider [data-baseweb="thumb"] {
    background-color: #4CAF50 !important;
}
.stSlider [data-baseweb="track"] {
    background-color: #555555 !important;
}
.stSlider [data-baseweb="track-fill"] {
    background-color: #4CAF50 !important;
}
.stSlider [data-baseweb="slider"] {
    background-color: transparent !important;
}
.stSlider [role="slider"] {
    color: white !important;
}
.stSlider [data-testid="stTickBarMin"], .stSlider [data-testid="stTickBarMax"] {
    color: white !important;
}
.stSlider [data-testid="stTickBar"] {
    color: white !important;
}

/* Asegurar que el texto del slider sea blanco */
.stSlider label, .stSlider text {
    color: white !important;
}

/* Quitar el fondo del slider */
.stSlider [data-baseweb="slider"] {
    background-color: transparent !important;
}

/* Estilo para el contenedor del título y el logo */
.title-logo-container {
    display: flex;
    align-items: center;
    gap: 20px;
}
.title-logo-container img {
    width: 100px;
}

/* Estilos para las sugerencias de carrera */
.career-suggestion {
    font-size: 1.2em;
    margin-bottom: 20px;
}
.career-suggestion h3 {
    color: #4CAF50 !important;
    font-size: 1.4em;
}
.income-range {
    color: #4CAF50 !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Función para traducir el texto
def translate(key, lang):
    return translations.get(lang, {}).get(key, key)

# Selección de idioma
languages = {
    'es': 'Español',
    'en': 'English',
    'pt': 'Português',
    'it': 'Italiano'
}
selected_lang = st.sidebar.selectbox(translate("language_selector", "es"), list(languages.keys()), format_func=lambda x: languages[x])

# Contenido de la barra lateral
st.sidebar.title(translate("sidebar_title", selected_lang))
st.sidebar.markdown(f"[{translate('home', selected_lang)}](#)")
st.sidebar.markdown(f"[{translate('about', selected_lang)}](#)")
st.sidebar.markdown(f"[{translate('contact', selected_lang)}](#)")

st.sidebar.header(translate("about_tool", selected_lang))
st.sidebar.write(translate("tool_description", selected_lang))

# Título de la aplicación con logo
col1, col2 = st.columns([4, 1])
with col1:
    st.title(translate("app_title", selected_lang))
with col2:
    try:
        logo = "Logo-solo.png"
        st.image(logo, width=50)
    except FileNotFoundError:
        st.error("No se pudo cargar el logo. Asegúrate de que el archivo exista en la ubicación correcta.")

st.write(translate("input_instruction", selected_lang))

# El campo de edad ha sido eliminado

# Nuevo campo para indicar si es estudiante
is_student = st.radio(
    translate("are_you_student", selected_lang),
    [translate("yes", selected_lang), translate("no", selected_lang)]
)

interests = st.text_area(translate("interests", selected_lang), "", key="interests")
skills = st.text_area(translate("skills", selected_lang), "", key="skills")

# Selección de país para el sistema de calificación
countries = {
    "México": "México",
    "Venezuela": "Venezuela",
    "España": "España",
    "Colombia": "Colombia",
    "Estados Unidos": "Estados Unidos",
    "Brasil": "Brasil",
    "Italia": "Italia"
}
selected_country = st.selectbox(translate("select_country", selected_lang), list(countries.keys()), format_func=lambda x: translate(x, selected_lang), key="country_selection")

# Mostrar opciones de calificaciones solo si es estudiante
if is_student == translate("yes", selected_lang):
    # Ajuste del rendimiento académico según el país seleccionado
    if selected_country == "México":
        min_grade, max_grade = 0, 100
        step = 1
        default = 60
    elif selected_country == "Venezuela":
        min_grade, max_grade = 0, 20
        step = 1
        default = 10
    elif selected_country in ["Colombia", "Estados Unidos"]:
        min_grade, max_grade = 0.0, 5.0
        step = 0.1
        default = 3.0
    elif selected_country == "Brasil":
        min_grade, max_grade = 0.0, 4.0
        step = 0.1
        default = 2.0
    else:
        min_grade, max_grade = 1, 10
        step = 1
        default = 5

    # Crear sliders para cada materia
    subject_grades = {}
    for subject in subjects_by_country[selected_country]:
        subject_grades[subject] = st.slider(
            translate(subject, selected_lang),
            min_value=min_grade,
            max_value=max_grade,
            value=default,
            step=step,
            key=f"grade_{subject}"
        )

    # Calcular el promedio general
    average_grade = sum(subject_grades.values()) / len(subject_grades)

    # Mostrar el promedio general
    if selected_country == "México":
        performance_text = f"{average_grade:.1f}/100"
    elif selected_country == "Venezuela":
        performance_text = f"{average_grade:.1f}/20"
    elif selected_country in ["Colombia", "Estados Unidos"]:
        performance_text = f"{average_grade:.1f}/5.0"
    elif selected_country == "Brasil":
        performance_text = f"{average_grade:.1f}/4.0"
    else:
        performance_text = f"{average_grade:.1f}/10"

    st.write(translate("current_performance", selected_lang).format(performance=performance_text))

if st.button(translate("get_suggestions", selected_lang)):
    if interests and skills:
        with st.spinner(translate("generating_suggestions", selected_lang)):
            if is_student == translate("yes", selected_lang):
                subject_grades_tuple = tuple(subject_grades.items())
                suggestions = get_ai_suggestions(interests, skills, subject_grades_tuple, selected_country, selected_lang, True)
            else:
                suggestions = get_ai_suggestions(interests, skills, tuple(), selected_country, selected_lang, False)
        st.subheader(translate("trajectory_suggestions", selected_lang))
        st.markdown(suggestions, unsafe_allow_html=True)
    else:
        st.warning(translate("input_warning", selected_lang))
