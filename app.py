from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
from services.scraper import extract_text_from_url
from services.youtube_service import get_youtube_transcript
from concurrent.futures import ThreadPoolExecutor
import atexit
import redis
import hashlib

# Cache süresini tanımla (1 saat = 3600 saniye)
CACHE_EXPIRATION = 3600

app = Flask(__name__, static_url_path='/static', static_folder='static')
# Updated CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": ["http://127.0.0.1:5000", "http://localhost:5000", 
                   "http://127.0.0.1:5500", "http://localhost:5500",
                   "null", "http://localhost:3000", "*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "X-CSRFToken"],
        "max_age": 3600
    }
})

# Global executor oluştur
executor = ThreadPoolExecutor(max_workers=3)

# Uygulama kapatıldığında executor'ı temizle
def cleanup_executor():
    global executor
    if executor:
        executor.shutdown(wait=True)
        executor = None

atexit.register(cleanup_executor)

ALLOWED_ORIGINS = [
    "https://your-app-name.onrender.com",
    "http://localhost:5000",
    "http://127.0.0.1:5000"
]

@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in ALLOWED_ORIGINS:
        response.headers.update({
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        })
    return response

# API anahtarınızı buraya ekleyin
GOOGLE_API_KEY = "AIzaSyBXTLs-v2qe3gDFimx1xCACfUENgV6dqCk"
genai.configure(api_key=GOOGLE_API_KEY)

# Fine-tune edilmiş model ID'nizi tanımlayın
MODEL_ID = "tunedModels/crisis-communication-gh20ehxj5b3b"

# Redis bağlantısı
redis_client = None

def get_cached_result(key):
    return None  # Redis olmadığı için her zaman None dön

def set_cached_result(key, value):
    pass  # Redis olmadığı için hiçbir şey yapma

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze_crisis():
    if request.method == 'OPTIONS':
        return jsonify({'success': True})
    
    try:
        data = request.json
        input_text = data.get('text', '')
        input_url = data.get('url', '')
        youtube_url = data.get('youtube_url', '')

        if youtube_url:
            input_text = get_youtube_transcript(youtube_url)
            if not input_text:
                return jsonify({
                    'success': False,
                    'error': 'Video için transkript bulunamadı. Lütfen altyazısı olan bir video deneyin.'
                }), 400

        elif input_url:
            input_text = extract_text_from_url(input_url)
            if not input_text:
                return jsonify({
                    'success': False,
                    'error': 'URL içeriği alınamadı. Lütfen geçerli bir haber URL\'si girin.'
                }), 400

        if not input_text:
            return jsonify({
                'success': False,
                'error': 'Geçerli bir metin bulunamadı.'
            }), 400

        # Gemini AI analizi
        prompt = f"""Structure and analyze the following case using the provided structure and give me an output like first ,structured form of the case than analyze of that case and (do these by the perspective of a crisis communication perspective)
input case[{input_text}]"""
        generation_config = {
            'temperature': 0,  # 0 = en deterministik sonuç
            'top_p': 1,
            'top_k': 1
        }

        model = genai.GenerativeModel(MODEL_ID)
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        result = response.text

        return jsonify({
            'success': True,
            'result': result,
            'cached': False
        })

    except Exception as e:
        print(f"\n=== Hata Detayı ===\n{str(e)}")
        error_message = "İşlem sırasında bir hata oluştu. Lütfen daha sonra tekrar deneyin."
        return jsonify({'success': False, 'error': error_message}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Server is running'
    })

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/clear-cache', methods=['POST', 'OPTIONS'])
def clear_cache():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    try:
        if redis_client:
            redis_client.flushdb()  # Tüm cache'i temizle
            print("Cache cleared successfully")
            return jsonify({'success': True, 'message': 'Cache cleared'})
        return jsonify({'success': False, 'error': 'Redis not connected'})
    except Exception as e:
        print(f"Cache clear error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 
