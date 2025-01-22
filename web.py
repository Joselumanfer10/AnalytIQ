import sqlite3
import streamlit as st
from PIL import Image
import io
import time
import base64
import json
import os
from dotenv import load_dotenv
import re

# Configuración inicial
st.set_page_config(page_title="AnalytIQ", page_icon="Logos/favicon.ico", layout="wide")

# Cargar variables de entorno
load_dotenv()

# Ruta del archivo de la base de datos SQLite
DB_PATH = "newsletter.db"

# Función para conectarse a la base de datos SQLite
def connect_to_database():
    return sqlite3.connect(DB_PATH)

# Crear la tabla para la newsletter si no existe
def setup_database():
    conn = connect_to_database()
    cursor = conn.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS newsletter (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(query)
    conn.commit()
    conn.close()

# Guardar un suscriptor en la base de datos
def save_subscriber(name, email):
    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        query = "INSERT INTO newsletter (name, email) VALUES (?, ?);"
        cursor.execute(query, (name, email))
        conn.commit()
    except sqlite3.IntegrityError:
        st.error("Este correo ya está registrado en nuestra Newsletter.")
    finally:
        conn.close()

# Crear la tabla de contactos en la base de datos si no existe
def setup_contact_table():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

# Configurar la base de datos al inicio
setup_database()  # Crea la tabla de la newsletter
setup_contact_table()  # Crea la tabla de contactos


# Cargar el logo y convertirlo a base64
logo_path = "Logos/AnalytIQ.png"  # Reemplaza con la ruta real de tu logo
imagen_logo = Image.open(logo_path)
logo_bytes = io.BytesIO()
imagen_logo.save(logo_bytes, format="PNG")
logo_bytes = logo_bytes.getvalue()
logo_base64 = base64.b64encode(logo_bytes).decode()

# Cargar la imagen de fondo y convertirla a base64
background_path = "Logos/Cabecera.png"  # Reemplaza con la ruta de la imagen de fondo
imagen_fondo = Image.open(background_path)
fondo_bytes = io.BytesIO()
imagen_fondo.save(fondo_bytes, format="PNG")
fondo_bytes = fondo_bytes.getvalue()
fondo_base64 = base64.b64encode(fondo_bytes).decode()

# Estilos CSS personalizados
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:ital,wght@0,300;1,900&display=swap');

    /* Fondo del encabezado con imagen */
    .dark-background {{
        background-image: url("data:image/jpeg;base64,{fondo_base64}");
        background-size: cover;
        background-position: center;
        padding: 60px 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
    }}

    /* Estilo del título principal */
    .custom-title {{
        font-family: 'Nunito Sans', sans-serif;
        font-style: italic;
        font-weight: 900;
        font-size: 48px;
        margin: 0;
    }}

    /* Texto destacado */
    .highlight {{
        color: #00ADB5; /* Color destacado del logo (personalizable) */
    }}

    /* Subtítulo */
    .custom-subtitle {{
        font-family: 'Nunito Sans', sans-serif;
        font-weight: 300;
        font-size: 18px;
        margin-top: 10px;
    }}
    </style>
""", unsafe_allow_html=True)

# Encabezado con fondo de imagen y logo
st.markdown(f"""
    <div class="dark-background">
        <h1 class="custom-title">Bienvenido a <span class="highlight">AnalytIQ</span></h1>
        <p class="custom-subtitle" style="background-color:hsla(0, 0.00%, 1.20%, 0.74); color: white; display: inline; padding: 3px;">Automatización y optimización al alcance de tu negocio.</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin: 40px 0;">
    <hr style="border: none; height: 2px; background: linear-gradient(to right, #00ADB5, #FFFFFF, #00ADB5);">
</div>
""", unsafe_allow_html=True)

# Barra lateral con logo y navegación
with st.sidebar:
    # Logo centrado y estilizado
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="data:image/png;base64,{logo_base64}" style="max-width: 120px; border-radius: 10px;"/>
        </div>
        <style>
            .sidebar .sidebar-content {{
                padding: 20px;
                background-color: #f7f9fc;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
        </style>
    """, unsafe_allow_html=True)

    # Línea divisoria decorativa
    st.markdown("""
        <div style="margin: 40px 0;">
            <hr style="border: none; height: 2px; background: linear-gradient(to right, #00ADB5, #FFFFFF, #00ADB5);">
        </div>
    """, unsafe_allow_html=True)

    # Selector de pestañas con `st.radio`
    options = st.radio(
        "Navegación",
        ["Inicio", "Servicios", "Demo", "Contacto", "Blog", "Política y Términos"],
        label_visibility="collapsed"  # Oculta el título "Navegación"
    )

# Función para mostrar todas las publicaciones
def display_all_blog_posts(posts):
    for post in posts:
        st.markdown(f"""
        <div style="background-color: #00ADB5; padding: 30px; border-radius: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); margin-bottom: 20px;">
            <h2 style="color: white; font-family: 'Nunito Sans', sans-serif; font-weight: bold;">{post['title']} {post.get('emoji', '')}</h2>
            <p style="color: #EEEEEE; font-family: 'Nunito Sans', sans-serif;">{post['date']}</p>
            <p style="color: #EEEEEE; font-family: 'Nunito Sans', sans-serif;">{post['summary']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Botón para mostrar el contenido completo
        if st.button(f"Leer más - {post['title']}", key=f"read_more_{post['title']}"):
            st.markdown(f"""
            <div style="background-color: #222831; padding: 20px; border-radius: 10px; margin-bottom: 20px; color: #EEEEEE;">
                <p style="font-family: 'Nunito Sans', sans-serif; font-size: 16px; line-height: 1.6;">{post['content']}</p>
            </div>
            """, unsafe_allow_html=True)


# Páginas
if options == "Inicio":
    st.title("Inicio")
    st.write("""
En **AnalytIQ**, ofrecemos servicios innovadores en **Inteligencia Artificial**, **Automatización de Procesos**, 
**Business Intelligence** y **Data Science**. Nuestro objetivo es ayudarte a optimizar tu negocio, 
mejorar la toma de decisiones y prepararte para el futuro tecnológico.

Ya seas una **empresa interesada en soluciones tecnológicas personalizadas**, 
o una **persona que busca aprender sobre IA y Data Science mediante clases individuales**,
¡tenemos algo para ti!

### **¿Qué hacemos?**
- **Servicios de IA y Automatización**: Implementamos soluciones inteligentes para optimizar procesos empresariales.
- **Business Intelligence (BI)**: Diseñamos sistemas que convierten tus datos en decisiones estratégicas.
- **Data Science**: Te ayudamos a explorar, analizar y aprovechar el poder de tus datos.
- **Capacitación Individual**: Ofrecemos clases personalizadas de IA, BI y Data Science para particulares o equipos de empresas.
- **Desarrollo de Proyectos**: Trabajamos contigo en la creación de proyectos innovadores adaptados a tus necesidades.

### **¿A quién va dirigido?**
- **Empresas:** Optimización y soluciones a medida para mejorar la eficiencia y productividad.
- **Profesionales y estudiantes:** Formación práctica en herramientas y conceptos clave de IA, BI y Data Science.
- **Emprendedores:** Desarrollo de proyectos que maximicen el impacto de tus ideas.

### **Nuestro Compromiso**
En AnalytIQ, nos enfocamos en entregar resultados prácticos y tangibles, combinando innovación, profesionalismo y cercanía. Creemos que la tecnología debe ser accesible y útil para todos.

### **Contáctanos**
Descubre cómo podemos ayudarte a transformar tus ideas en realidad. Explora más en las secciones de Servicios y Demo.
""")
    # Imagen decorativa
    st.image("Logos/inicio.png", caption="Visualiza el futuro de tu empresa con nuestras soluciones analíticas.", 
         use_container_width=True, output_format="PNG")

    st.markdown("""
        ### Lo que dicen nuestros clientes
        <div style="background-color: #393E46; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
            <p style="font-style: italic; color: #EEEEEE;">"Gracias a AnalytIQ, he podido gestionar mejor mi tiempo y aumentar la eficiencia de mi negocio."</p>
            <p style="text-align: right; font-weight: bold; color: #00ADB5;">— Juan Pérez, Autónomo</p>
        </div>

        <div style="background-color: #393E46; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
            <p style="font-style: italic; color: #EEEEEE;">"El análisis de datos personalizado nos ayudó a entender mejor el comportamiento de nuestros clientes y a incrementar nuestras ventas en un 25%."</p>
            <p style="text-align: right; font-weight: bold; color: #00ADB5;">— María López, Dueña de una pequeña tienda de ropa</p>
        </div>
        """, unsafe_allow_html=True)

    # Línea divisoria decorativa
    st.markdown("""
        <div style="margin: 40px 0;">
            <hr style="border: none; height: 2px; background: linear-gradient(to right, #00ADB5, #FFFFFF, #00ADB5);">
        </div>
    """, unsafe_allow_html=True)

    # Función para validar el formato del correo electrónico
    def is_valid_email(email):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email)

    # Función para verificar si el correo ya está registrado en la base de datos
    def is_email_registered(email):
        conn = connect_to_database()
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM newsletter WHERE email = ?;"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        conn.close()
        return result[0] > 0  # Devuelve True si el correo ya está registrado


    # Sección de Newsletter con diseño mejorado
    st.markdown("""
    <div style="background-color: #00ADB5; padding: 30px; border-radius: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);">
        <h2 style="color: white; font-family: 'Nunito Sans', sans-serif; font-weight: bold; margin-bottom: 15px;">
            💌 ¡Únete a Nuestra Newsletter!
        </h2>
        <p style="color: #EEEEEE; font-family: 'Nunito Sans', sans-serif; font-size: 18px; line-height: 1.6; margin-bottom: 25px;">
            Sé el primero en recibir actualizaciones exclusivas, consejos prácticos sobre IA y automatización, y contenido diseñado 
            para ayudarte a optimizar tu negocio.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Formulario de suscripción
    with st.form("newsletter_form"):
        name = st.text_input("Nombre", placeholder="Ingresa tu nombre completo")
        email = st.text_input("Correo electrónico", placeholder="Ingresa tu correo electrónico")
        submitted = st.form_submit_button("🎉 ¡Suscribirme ahora!")

        if submitted:
            if not name or not email:
                st.error("Por favor, completa todos los campos para suscribirte.")
            elif not is_valid_email(email):
                st.error("Por favor, introduce un correo electrónico válido.")
            elif is_email_registered(email):
                st.error("Este correo ya está registrado en nuestra Newsletter.")
            else:
                save_subscriber(name, email)  # Llama a tu función para guardar el usuario
                st.success(f"¡Gracias {name}! Te has unido a nuestra Newsletter.")
                st.balloons()  # Solo aparecen si el correo es válido y no está registrado

elif options == "Servicios":
    st.title("Nuestros Servicios")

    # Estilos CSS para los bloques de servicios
    st.markdown("""
        <style>
        .service-box {
            background-color: #393E46;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .service-title {
            color: #00ADB5;
            font-family: 'Nunito Sans', sans-serif;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .service-description {
            color: #EEEEEE;
            font-family: 'Nunito Sans', sans-serif;
            font-size: 16px;
            line-height: 1.6;
        }
        .cta-button {
            display: inline-block;
            background-color: #00ADB5;
            color: white;
            font-family: 'Nunito Sans', sans-serif;
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            transition: background-color 0.3s ease;
        }
        .cta-button:hover {
            background-color: #007A7E;
        }
        </style>
    """, unsafe_allow_html=True)

    # Servicio 1
    st.markdown("""
    <div class="service-box">
        <p class="service-title">🤖 Aprender a usar la IA y GPTs Personalizados</p>
        <p class="service-description">Aprende a usar ChatGPT de forma eficiente y configura asistentes personalizados para automatizar tareas y mejorar tu productividad.</p>
    </div>
    """, unsafe_allow_html=True)

    # Servicio 2
    st.markdown("""
    <div class="service-box">
        <p class="service-title">🔄 Creación de Modelos Automatizados</p>
        <p class="service-description">Automatiza tareas repetitivas con soluciones personalizadas que optimizan tu tiempo y mejoran la eficiencia.</p>
    </div>
    """, unsafe_allow_html=True)

    # Servicio 3
    st.markdown("""
    <div class="service-box">
        <p class="service-title">💬 Creación de Chatbots</p>
        <p class="service-description">Desarrollamos chatbots personalizados para tu página web o plataformas de mensajería, ofreciendo atención rápida y eficiente a tus clientes.</p>
    </div>
    """, unsafe_allow_html=True)

    # Servicio 4
    st.markdown("""
    <div class="service-box">
        <p class="service-title">📊 Diseño de Dashboards Interactivos</p>
        <p class="service-description">Visualiza el rendimiento de tu negocio en tiempo real con dashboards personalizados para la toma de decisiones estratégicas.</p>
    </div>
    """, unsafe_allow_html=True)

    # Servicio 5
    st.markdown("""
    <div class="service-box">
        <p class="service-title">📈 Modelos de Machine Learning</p>
        <p class="service-description">Implementamos modelos predictivos y de segmentación para optimizar tus decisiones estratégicas y maximizar resultados.</p>
    </div>
    """, unsafe_allow_html=True)

    # Servicio 6
    st.markdown("""
    <div class="service-box">
        <p class="service-title">🛠️ Auditoría Tecnológica y Consultoría</p>
        <p class="service-description">Identificamos áreas de mejora en tus procesos y te proponemos soluciones tecnológicas adaptadas a las necesidades de tu negocio.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin-top: 30px;">
        <p style="color: #EEEEEE; font-size: 18px;">
            ¿Quieres ver ejemplos en acción? Visita nuestra sección <a href="#demo" style="color: #00ADB5; text-decoration: none; font-weight: bold;">Demo</a> para descubrir cómo funcionan nuestras automatizaciones y soluciones personalizadas.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Variable para controlar si se muestra el formulario
    show_form = st.session_state.get("show_form", False)

    

    # Botón que alterna el formulario de contacto
    if st.button("¡Contáctanos para Más Información!"):
        st.session_state["show_form"] = not st.session_state.get("show_form", False)  # Alternar el estado

    # Mostrar el formulario si el estado es True
    if st.session_state.get("show_form", False):
        st.markdown("""
            <div style="background-color: #00ADB5; padding: 20px; border-radius: 10px; text-align: center; color: white;">
                <h3>Déjanos tus datos de contacto</h3>
                <p>Completa el siguiente formulario y nos pondremos en contacto contigo lo antes posible.</p>
            </div>
        """, unsafe_allow_html=True)

        # Formulario para recoger los datos de contacto
        name = st.text_input("Nombre", placeholder="Ingresa tu nombre completo")
        email = st.text_input("Correo electrónico", placeholder="Ingresa tu correo electrónico")
        message = st.text_area("Mensaje", placeholder="Escribe qué necesitas")

        # Botón para enviar los datos del formulario
        if st.button("Enviar"):
            if name and email and message:
                # Guardar los datos en la base de datos
                conn = connect_to_database()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO contacts (name, email, message) VALUES (?, ?, ?);",
                    (name, email, message),
                )
                conn.commit()
                conn.close()
                st.success("¡Gracias por contactarnos! Nos pondremos en contacto contigo pronto.")
            else:
                st.error("Por favor, completa todos los campos antes de enviar el mensaje.")



elif options == "Demo":
    st.title("Demo Interactiva")

    # Introducción
    st.write("""
    En esta sección, te mostramos ejemplos prácticos de nuestras soluciones en acción.
    Descubre cómo nuestras automatizaciones pueden transformar tu día a día.
    """)

    # Ejemplo 1: Automatización de WhatsApp
    st.markdown("""
    <div class="service-box">
        <p class="service-title">🌟 Gestión de Mensajes de WhatsApp</p>
        <p class="service-description">
            Con este flujo de trabajo automatizado:
            <ul>
                <li>Los mensajes que recibes en WhatsApp se procesan automáticamente.</li>
                <li>El sistema interpreta el contenido (texto, audio o imágenes) y crea un evento en tu calendario.</li>
                <li>Recibirás notificaciones de confirmación y recordatorios automáticos.</li>
            </ul>
            Este tipo de automatización ahorra tiempo y garantiza que nunca pierdas una tarea o cita importante.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.image("Logos/make.png", caption="Flujo automatizado para la gestión de mensajes de WhatsApp", use_container_width=True)

    # Espacio para otros ejemplos
    st.markdown("""
    <div class="service-box">
        <p class="service-title">📊 Dashboards Interactivos</p>
        <p class="service-description">
            Descubre cómo nuestros dashboards pueden mostrarte datos clave de tu negocio en tiempo real.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.image("Logos/PowerBI.png", caption="Dashboard interactivo en PowerBI para control de facturación de negocio", use_container_width=True)

    # Alternar entre llamada a la acción y formulario
    if "show_demo_form" not in st.session_state:
        st.session_state["show_demo_form"] = False

    if not st.session_state["show_demo_form"]:
        # Llamada a la acción
        if st.button("Rellenar Formulario de Contacto"):
            st.session_state["show_demo_form"] = True
    else:
        # Formulario de contacto
        st.markdown("""
        <div style="background-color: #00ADB5; padding: 20px; border-radius: 10px; text-align: center; color: white;">
            <h3>Déjanos tus datos de contacto</h3>
            <p>Completa el siguiente formulario y nos pondremos en contacto contigo lo antes posible.</p>
        </div>
        """, unsafe_allow_html=True)

        name = st.text_input("Nombre", placeholder="Ingresa tu nombre completo")
        email = st.text_input("Correo electrónico", placeholder="Ingresa tu correo electrónico")
        message = st.text_area("Mensaje", placeholder="Escribe tu consulta o mensaje aquí...")

        if st.button("Enviar"):
            if name and email and message:
                # Guardar los datos en la base de datos
                conn = connect_to_database()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO contacts (name, email, message) VALUES (?, ?, ?);",
                    (name, email, message),
                )
                conn.commit()
                conn.close()
                st.success("¡Gracias por contactarnos! Nos pondremos en contacto contigo pronto.")
                st.session_state["show_demo_form"] = False
            else:
                st.error("Por favor, completa todos los campos antes de enviar el mensaje.")


elif options == "Contacto":
    st.title("Contáctanos")

    # Estilos CSS personalizados
    st.markdown("""
    <style>
        .contact-form {
            background-color: #393E46;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            color: #EEEEEE;
            font-family: 'Nunito Sans', sans-serif;
        }
        .contact-form h2 {
            color: #00ADB5;
            margin-bottom: 20px;
        }
        .contact-form label {
            font-weight: bold;
        }
        .contact-form input, .contact-form textarea {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #00ADB5;
            border-radius: 5px;
            background-color: #222831;
            color: white;
            font-family: 'Nunito Sans', sans-serif;
        }
        .contact-form button {
            background-color: #00ADB5;
            color: white;
            font-weight: bold;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s ease;
        }
        .contact-form button:hover {
            background-color: #007A7E;
        }
    </style>
    """, unsafe_allow_html=True)

    # Formulario de contacto
    st.markdown("""
    <div class="contact-form">
        <h2>Estamos aquí para ayudarte</h2>
        <p>Déjanos tu información y nos pondremos en contacto contigo lo antes posible.</p>
    </div>
    """, unsafe_allow_html=True)

    # Elementos del formulario
    name = st.text_input("Nombre", placeholder="Ingresa tu nombre completo")
    email = st.text_input("Email", placeholder="Tu correo electrónico")
    message = st.text_area("Mensaje", placeholder="Escribe tu consulta o mensaje aquí...")

    # Botón de envío
    if st.button("Enviar Mensaje"):
        if name and email and message:
            try:
                # Guardar los datos en la base de datos
                conn = connect_to_database()
                cursor = conn.cursor()
                query = """
                INSERT INTO contacts (name, email, message) VALUES (?, ?, ?);
                """
                cursor.execute(query, (name, email, message))
                conn.commit()
                conn.close()

                st.success(f"¡Gracias por tu mensaje, {name}! Te contactaremos pronto a través de {email}.")
            except sqlite3.IntegrityError as e:
                st.error(f"Error al guardar los datos: {str(e)}")
        else:
            st.error("Por favor, completa todos los campos antes de enviar tu mensaje.")

    # Información adicional de contacto
    st.markdown("""
    <div class="contact-form">
        <h2>Otras formas de contacto</h2>
        <p>📧 Email: analytiq.es@gmail.com</p>
        <p>📞 Teléfono: +34 655 312 243</p>
    </div>
    """, unsafe_allow_html=True)


if options == "Blog":
    st.title("Blog")
    st.markdown("### Publicaciones Recientes")

    # Cargar las entradas del blog
    try:
        with open("blog_entries.json", "r") as f:
            blog_entries = json.load(f)
        # Mostrar todas las publicaciones
        display_all_blog_posts(blog_entries)
    except FileNotFoundError:
        st.error("No se encontró el archivo de entradas del blog.")
    except json.JSONDecodeError:
        st.error("Error al leer el archivo de entradas del blog.")



# Pestaña Política de Privacidad y Términos de Uso
elif options == "Política y Términos":
    st.title("Política de Privacidad y Términos de Uso")

    # Política de Privacidad
    st.markdown("""
    ## Política de Privacidad
    AnalytIQ se compromete a proteger tu privacidad. Recopilamos información personal, como tu nombre y correo electrónico, exclusivamente para responder a tus consultas y mejorar nuestros servicios.
    - **Datos recopilados:** Información de contacto y datos relacionados con el uso de este sitio web.
    - **Uso de datos:** Los datos se utilizarán únicamente para comunicación y análisis interno.
    - **Protección de datos:** Implementamos medidas de seguridad para proteger tu información.
    Si tienes alguna pregunta sobre nuestra política de privacidad, contáctanos en: **analytiq.es@gmail.com**
    """)

    # Términos de Uso
    st.markdown("""
    ## Términos de Uso
    Al usar este sitio web, aceptas los siguientes términos:
    - **Propiedad intelectual:** Todo el contenido de este sitio, incluidos textos, imágenes y diseños, es propiedad de AnalytIQ y está protegido por derechos de autor.
    - **Uso permitido:** Puedes utilizar este sitio únicamente con fines personales y no comerciales.
    - **Limitación de responsabilidad:** AnalytIQ no se hace responsable de cualquier daño derivado del uso de este sitio.
    - **Modificaciones:** Nos reservamos el derecho de actualizar estos términos en cualquier momento.
    Si tienes alguna duda sobre los términos, contáctanos en: **analytiq.es@gmail.com**
    """)
