// Dil ayarlarını başlat
let currentLang = localStorage.getItem('language') || 'tr';

const translations = {
    tr: {
        title: "Kriz Analiz Sistemi",
        university: "Bahçeşehir Üniversitesi - İletişim Fakültesi",
        faculty: "Yapay Zeka Destekli Kriz Yönetimi - Can Büyükalkan",
        textInput: "Metin Girişi",
        newsUrlInput: "Haber URL",
        youtubeUrlInput: "YouTube URL",
        textPlaceholder: "Analiz edilecek metni buraya girin...",
        newsUrlPlaceholder: "Haber URL'ini buraya girin...",
        youtubeUrlPlaceholder: "YouTube URL'ini buraya girin...",
        analyzeButton: "Analiz Et",
        loading: "Analiz ediliyor...",
        switchLang: "EN",
        emptyInput: "Lütfen bir metin veya URL girin",
        invalidUrl: "Geçersiz URL formatı",
        error: "Hata: "
    },
    en: {
        title: "Crisis Analysis System",
        university: "Bahçeşehir University",
        faculty: "AI-Assisted Crisis Management - Can Büyükalkan",
        textInput: "Text Input",
        newsUrlInput: "News URL",
        youtubeUrlInput: "YouTube URL",
        textPlaceholder: "Enter text to be analyzed...",
        newsUrlPlaceholder: "Enter news URL...",
        youtubeUrlPlaceholder: "Enter YouTube URL...",
        analyzeButton: "Analyze",
        loading: "Analyzing...",
        switchLang: "TR",
        emptyInput: "Please enter a text or URL",
        invalidUrl: "Invalid URL format",
        error: "Error: "
    }
};

function updateLanguage() {
    const t = translations[currentLang];
    
    // Update all text content
    document.title = t.title;
    document.querySelector('h1').textContent = t.title;
    document.querySelector('.university-name').textContent = t.university;
    document.querySelector('.faculty-name').textContent = t.faculty;
    
    // Update input type buttons with icons
    document.querySelector('button[onclick="switchInputType(\'text\')"]').innerHTML = 
        `<i class="fas fa-keyboard"></i> ${t.textInput}`;
    document.querySelector('button[onclick="switchInputType(\'newsUrl\')"]').innerHTML = 
        `<i class="fas fa-newspaper"></i> ${t.newsUrlInput}`;
    document.querySelector('button[onclick="switchInputType(\'youtubeUrl\')"]').innerHTML = 
        `<i class="fab fa-youtube"></i> ${t.youtubeUrlInput}`;
    
    // Update placeholders
    document.querySelector('#inputText').placeholder = t.textPlaceholder;
    document.querySelector('#newsUrlInput').placeholder = t.newsUrlPlaceholder;
    document.querySelector('#youtubeUrlInput').placeholder = t.youtubeUrlPlaceholder;
    
    // Update analyze button and footer
    document.querySelector('button[onclick="analyzeText()"]').textContent = t.analyzeButton;
    document.querySelector('.language-switch').textContent = t.switchLang;
    document.querySelector('.footer').innerHTML = `© 2024 ${t.university} ${t.faculty}`;
}

async function analyzeText() {
    const textInput = document.getElementById('inputText');
    const newsUrlInput = document.getElementById('newsUrlInput');
    const youtubeUrlInput = document.getElementById('youtubeUrlInput');
    const resultDiv = document.getElementById('result');
    
    const isNewsUrlMode = newsUrlInput.style.display !== 'none';
    const isYoutubeMode = youtubeUrlInput.style.display !== 'none';
    const inputValue = isYoutubeMode ? youtubeUrlInput.value : 
                      isNewsUrlMode ? newsUrlInput.value : 
                      textInput.value;
    
    if (!inputValue) {
        resultDiv.innerHTML = translations[currentLang].emptyInput;
        return;
    }
    
    if ((isNewsUrlMode || isYoutubeMode) && !validateUrl(inputValue)) {
        resultDiv.innerHTML = translations[currentLang].invalidUrl;
        return;
    }
    
    resultDiv.innerHTML = translations[currentLang].loading;
    
    try {
        console.log("Request Payload:", {
            text: isNewsUrlMode || isYoutubeMode ? '' : inputValue,
            url: isNewsUrlMode ? inputValue : '',
            youtube_url: isYoutubeMode ? inputValue : ''
        });
        
        const response = await fetch('http://127.0.0.1:5000/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            credentials: 'omit',
            mode: 'cors',
            body: JSON.stringify({
                text: isNewsUrlMode || isYoutubeMode ? '' : inputValue,
                url: isNewsUrlMode ? inputValue : '',
                youtube_url: isYoutubeMode ? inputValue : ''
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            resultDiv.innerHTML = `
                <div class="section-content">
                    ${data.cached ? '<div class="cached-badge">Önbellek Sonucu</div>' : ''}
                    <pre class="analysis-result">${data.result}</pre>
                </div>`;
        } else {
            resultDiv.innerHTML = 'Hata: ' + data.error;
        }
    } catch (error) {
        console.error('API Error:', error);
        resultDiv.innerHTML = `<div class="error-message">
            ${translations[currentLang].error} ${error.message}
        </div>`;
    }
}

// Dil değiştirme fonksiyonu
function toggleLanguage() {
    currentLang = currentLang === 'tr' ? 'en' : 'tr';
    updateLanguage();
    localStorage.setItem('language', currentLang);
}

// Sayfa yüklendiğinde dil ayarlarını uygula
document.addEventListener('DOMContentLoaded', () => {
    updateLanguage();
});

function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? '' : 'dark';
    
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update theme icon
    const themeButton = document.querySelector('.theme-switch');
    themeButton.innerHTML = newTheme === 'dark' ? '☀️' : '🌓';
}

// Apply saved theme on page load
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
        const themeButton = document.querySelector('.theme-switch');
        themeButton.innerHTML = savedTheme === 'dark' ? '☀️' : '🌓';
    }
});

// API endpoint'ini güncelle
const API_URL = 'https://your-app-name.onrender.com';

async function clearCache() {
    try {
        const response = await fetch(`${API_URL}/clear-cache`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            credentials: 'omit',
            mode: 'cors'
        });
        
        if (!response.ok) {
            throw new Error('Cache temizleme başarısız');
        }

        const data = await response.json();
        if (data.success) {
            alert('Cache başarıyla temizlendi!');
            document.getElementById('result').innerHTML = '';
        } else {
            throw new Error(data.error || 'Cache temizleme başarısız');
        }
    } catch (error) {
        console.error('Cache temizleme hatası:', error);
        alert('Cache temizlenirken bir hata oluştu: ' + error.message);
    }
}
