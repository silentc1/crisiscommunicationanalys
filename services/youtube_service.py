from youtube_transcript_api import YouTubeTranscriptApi
import re
from .utils import limit_word_count
import time
from functools import lru_cache

# Cache for transcript results (1 hour expiry)
@lru_cache(maxsize=100)
def get_cached_transcript(video_id: str) -> str:
    return _get_youtube_transcript_internal(video_id)

def extract_video_id(url: str) -> str:
    # Support different YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]+)',
        r'(?:youtube\.com\/shorts\/)([\w-]+)',
        r'(?:youtube\.com\/embed\/)([\w-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_youtube_transcript(url: str) -> str:
    try:
        video_id = extract_video_id(url)
        print(f"\n=== YouTube Transcript Processing ===")
        print(f"URL: {url}")
        print(f"Extracted Video ID: {video_id}")
        
        if not video_id:
            print("Error: Invalid YouTube URL - Could not extract video ID")
            raise ValueError("Geçersiz YouTube URL'si")
        
        # Try to get from cache first
        try:
            return get_cached_transcript(video_id)
        except Exception as e:
            print(f"Cache miss or error: {str(e)}")
            # If cache fails, wait a bit and try direct fetch
            time.sleep(2)  # Add delay between requests
            return _get_youtube_transcript_internal(video_id)
            
    except Exception as e:
        print(f"Error in get_youtube_transcript: {str(e)}")
        if "Video transkripti boş" in str(e):
            raise ValueError("Video transkripti boş. Lütfen başka bir video deneyin.")
        if "Too Many Requests" in str(e):
            raise ValueError("Çok fazla istek gönderildi. Lütfen birkaç dakika bekleyip tekrar deneyin.")
        raise

def _get_youtube_transcript_internal(video_id: str) -> str:
    transcript = None
    try_languages = ['tr', 'en']
    available_transcripts = []
    
    try:
        # Önce mevcut transkript listesini al
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        print(f"Available transcripts: {[tr.language_code for tr in transcript_list._manually_created_transcripts.values()]}")
        available_transcripts = [tr.language_code for tr in transcript_list._manually_created_transcripts.values()]
    except Exception as e:
        print(f"Error listing transcripts: {str(e)}")
        available_transcripts = []
    
    print(f"Attempting to fetch transcript in languages: {try_languages}")
    print(f"Available transcripts: {available_transcripts}")
    
    for lang in try_languages:
        try:
            print(f"Attempting to fetch transcript in language: {lang}")
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
            print(f"Successfully found transcript in {lang}")
            break
        except Exception as e:
            print(f"Failed to get transcript in {lang}: {str(e)}")
            time.sleep(1)  # Add delay between language attempts
            continue
            
    if not transcript:
        try:
            print("Attempting to fetch transcript in any available language")
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            print("Successfully found transcript in fallback language")
        except Exception as e:
            error_msg = str(e)
            print(f"No transcript found in any language: {error_msg}")
            if "No transcript found" in error_msg:
                raise ValueError("Video için transkript bulunamadı. Lütfen altyazısı olan bir video deneyin.")
            raise ValueError(f"Transkript alınırken hata oluştu: {error_msg}")
    
    if not transcript:
        print("Error: Transcript is None after all attempts")
        raise ValueError("Video transkripti alınamadı")
        
    full_transcript = ' '.join(entry['text'] for entry in transcript)
    
    if not full_transcript or len(full_transcript.strip()) == 0:
        print("Error: Empty transcript text")
        raise ValueError("Video transkripti boş")
        
    limited_transcript = limit_word_count(full_transcript)
    
    print(f"Original Transcript Length: {len(full_transcript.split())} words")
    print(f"Limited Transcript Length: {len(limited_transcript.split())} words")
    print("Transcript processing completed successfully")
    
    return limited_transcript