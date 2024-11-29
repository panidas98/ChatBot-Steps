import telebot
import pandas as pd
import spacy
import numpy as np

# Token del bot de Telegram
TELEGRAM_TOKEN = '7248645379:AAH77BaCBNn_-nh6nJSGa6joKtXNA3tNwRU'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Ruta del archivo de productos
ruta_productos = 'C:/Users/juan.ochoa/OneDrive - INMEL INGENIERIA SAS/Documentos/Python_Codigos/Bot_GPT/Arts.xlsx'

# Cargar modelo de lenguaje en español
nlp = spacy.load('es_core_news_sm')

# Cargar el archivo Excel con productos
df = pd.read_excel(ruta_productos)

def calcular_similitud_semantica(texto1, texto2):
    """
    Calcula la similitud semántica entre dos textos usando spaCy.
    
    Args:
        texto1 (str): Primer texto para comparar
        texto2 (str): Segundo texto para comparar
    
    Returns:
        float: Puntuación de similitud entre 0 y 1
    """
    # Asegurar que los textos sean strings
    texto1 = str(texto1).lower()
    texto2 = str(texto2).lower()
    
    # Procesar textos
    doc1 = nlp(texto1)
    doc2 = nlp(texto2)
    
    # Calcular similitud, manejar casos de textos vacíos
    try:
        similitud = doc1.similarity(doc2)
        return similitud
    except:
        return 0

def encontrar_producto_similar(texto_consulta):
    """
    Busca productos usando similitud semántica en nombre y descripción.
    
    Args:
        texto_consulta (str): Texto de búsqueda del usuario
    
    Returns:
        pandas.Series or None: Producto encontrado o None
    """
    # Procesar el texto de consulta
    doc_consulta = nlp(texto_consulta.lower())
    
    # Puntuaciones de similitud para cada producto
    similitudes = []
    
    for index, row in df.iterrows():
        # Calcular similitud con nombre del producto
        similitud_nombre = calcular_similitud_semantica(texto_consulta, row['Producto'])
        
        # Calcular similitud con descripción del producto
        similitud_descripcion = calcular_similitud_semantica(texto_consulta, row['Descripción'])
        
        # Combinar similitudes con más peso para el nombre
        similitud_combinada = (similitud_nombre * 0.7) + (similitud_descripcion * 0.3)
        
        similitudes.append((similitud_combinada, row))
    
    # Ordenar por similitud descendente
    similitudes_ordenadas = sorted(similitudes, key=lambda x: x[0], reverse=True)
    
    # Si la mejor similitud es significativa, devolver el producto
    if similitudes_ordenadas and similitudes_ordenadas[0][0] > 0.5:
        return similitudes_ordenadas[0][1]
    
    return None

def procesar_pregunta(pregunta):
    """
    Procesa la pregunta buscando productos por consulta.
    
    Args:
        pregunta (str): Pregunta del usuario
    
    Returns:
        str: Respuesta con información del producto
    """
    # Buscar producto similar
    producto = encontrar_producto_similar(pregunta)
    
    if producto is not None:
        return f"""
Producto encontrado:
- Nombre: {producto['Producto']}
- Descripción: {producto['Descripción']}
- Precio: {producto['Precio']}
- Link de compra: {producto['Link']}
"""
    return "Lo siento, no pude encontrar ningún producto relacionado con tu consulta."

# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "¡Hola! Soy un VerbumBot inteligente de productos. Puedes preguntarme sobre cualquier producto usando su nombre o descripción. Parada es gei.")

# Manejador de mensajes
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    texto = message.text
    respuesta = procesar_pregunta(texto)
    bot.reply_to(message, respuesta)

# Iniciar el bot
bot.polling()