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

@app.after_request
def after_request(response):
    response.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept',
        'Access-Control-Max-Age': '3600'
    })
    return response

# API anahtarınızı buraya ekleyin
GOOGLE_API_KEY = "AIzaSyBXTLs-v2qe3gDFimx1xCACfUENgV6dqCk"
genai.configure(api_key=GOOGLE_API_KEY)

# Fine-tune edilmiş model ID'nizi tanımlayın
MODEL_ID = "tunedModels/crisis-communication-gh20ehxj5b3b"

# Redis bağlantısı
try:
    redis_client = redis.Redis(
        host='localhost',
        port=6380,  # Port değiştirildi
        db=0,
        decode_responses=True,
        socket_connect_timeout=2
    )
    redis_client.ping()  # Test connection
    print("Redis connection successful")
except redis.ConnectionError as e:
    print(f"Redis connection failed: {e}")
    redis_client = None

def get_cached_result(key):
    try:
        if redis_client:
            return redis_client.get(key)
    except:
        return None
    return None

def set_cached_result(key, value):
    try:
        if redis_client:
            redis_client.setex(key, CACHE_EXPIRATION, value)
            print(f"Cache set for key: {key}")
    except Exception as e:
        print(f"Cache set error: {str(e)}")
        pass

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze_crisis():
    if request.method == 'OPTIONS':
        return make_cors_preflight_response()

    try:
        data = request.json
        input_text = data.get('text', '')
        input_url = data.get('url', '')
        youtube_url = data.get('youtube_url', '')

        # URL veya YouTube içeriğini al
        if youtube_url:
            print(f"\n=== YouTube URL Processing ===\nURL: {youtube_url}")
            input_text = get_youtube_transcript(youtube_url)
            if not input_text:
                return jsonify({
                    'success': False,
                    'error': 'Video için transkript bulunamadı. Lütfen altyazısı olan bir video deneyin.'
                }), 400

        elif input_url:
            print(f"\n=== News URL Processing ===\nURL: {input_url}")
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

        # Cache key oluştur
        cache_key = hashlib.md5(
            f"{input_text}{input_url}{youtube_url}".encode()
        ).hexdigest()

        # Cache'den kontrol et
        cached_result = get_cached_result(cache_key)
        if cached_result:
            print(f"Cache hit for key: {cache_key}")
            return jsonify({
                'success': True,
                'result': cached_result,
                'cached': True
            })

        # Gemini AI analizi
        prompt = f"""Structure and analyze the following case using the provided structure and give me an output like first ,structured form of the case than analyze of that case and (do these by the perspective of a crisis communication perspective)
input case[{input_text}]"""
        
        response = genai.GenerativeModel(MODEL_ID).generate_content(prompt)
        result = response.text

        # Sonucu cache'e kaydet
        set_cached_result(cache_key, result)

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