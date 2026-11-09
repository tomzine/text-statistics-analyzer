from pathlib import Path

from analyzer import load_text,normalize_words, calculate_statistics



def display_statistics(results):
    """ Display results"""
    # Simple statistice
    print("====== TEXT STATISTICS =======")
    print(f"Number of lines : {results['number_of_lines']}")
    print(f"Number of words : {results['number_of_words']}")
    print(f"Number of characters : {results['number_of_characters']}")
    print(f"Number of sentencese : {results['number_of_sentences']}")
    print(f"Number of AI : {results['number_of_ai']}")

    print("======Advanced statistics======")

    print(f"Unique words :{results['unique_words']}")
    print(f"longest word : {results['longest_word']}")
    print(f"Shortest word: {results['shortest_word']}")
    print(f"Aerage word length: {results['averg_len']}")
    
    print("---------Longest Words---------")
    for i, word in enumerate(results['longest_words'], start=1):
        print(f"{i}. {word} ({len(word)} characters)")

    print("\n------- MOST FREQUENT WORDS -----")

    for word, frequency in results["frequent_words"]:
        print(f"{word}: {frequency}")

    print("==============================")



def main():
    """ Run the application """

    file_path = Path(__file__).parent / "text.txt"

    text = load_text(file_path)

    if text is None:
        return

    words = normalize_words(text)

    results = calculate_statistics(text, words)
    
    display_statistics(results)


if __name__ == "__main__":
    main()