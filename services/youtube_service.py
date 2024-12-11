from youtube_transcript_api import YouTubeTranscriptApi
import re
from .utils import limit_word_count

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
            raise ValueError("Invalid YouTube URL")
        
        transcript = None
        try_languages = ['en']
        
        for lang in try_languages:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                break
            except:
                continue
                
        if not transcript:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
            except Exception as e:
                print(f"No transcript found in any language: {str(e)}")
                return None
        
        full_transcript = ' '.join(entry['text'] for entry in transcript)
        limited_transcript = limit_word_count(full_transcript)
        
        print(f"Original Transcript Length: {len(full_transcript.split())} words")
        print(f"Limited Transcript Length: {len(limited_transcript.split())} words")
        
        return limited_transcript
        
    except Exception as e:
        print(f"Error extracting YouTube transcript: {str(e)}")
        return None 