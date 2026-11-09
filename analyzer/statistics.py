from collections import Counter


def calculate_statistics(text : str, words : list[str]) -> dict:
    """Calculate text statistics"""

    
    number_of_lines = len(text.splitlines())
    number_of_words = len(text.split())
    number_of_characters = len(text)
    
    number_of_sentences = (text.count(".") 
                         + text.count("!") 
                         + text.count("?")
                         )

    number_of_ai = words.count("ai")

    longest_words = sorted(words, key=len, reverse=True)[:3]

    unique_words = len(set(words))
    longest_word = max(words, key=len, default="N/A")
    shortest_word = min(words, key=len, default="N/A")
    
    averg_len = (
        sum(len(word) for word in words)/ len(words)
        if words else 0
    )
    
    counter = Counter(words)
    frequent_words = counter.most_common(5)

    results = {
        'number_of_lines': number_of_lines,
        'number_of_words' : number_of_words,
        'number_of_characters' : number_of_characters,
        'number_of_sentences': number_of_sentences,
        'number_of_ai': number_of_ai,
        'longest_words': longest_words,
        'unique_words': unique_words,
        'longest_word' : longest_word,
        'shortest_word': shortest_word,
        'averg_len': averg_len,
        'frequent_words': frequent_words
    }
    return results