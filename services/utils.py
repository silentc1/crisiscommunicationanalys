def limit_word_count(text: str, max_words: int = 1500) -> str:
    words = text.split()
    if len(words) > max_words:
        return ' '.join(words[:max_words])
    return text 