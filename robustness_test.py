from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from matcher import lexical_similarity, normalize_aliases


def character_similarity(left_text, right_text):
    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
    )

    matrix = vectorizer.fit_transform(
        [left_text, right_text]
    )

    return float(
        cosine_similarity(
            matrix[0:1],
            matrix[1:2],
        )[0, 0]
    )


def print_comparison(label, left_text, right_text):
    word_score = lexical_similarity(
        left_text,
        right_text,
    )

    alias_score = lexical_similarity(
        normalize_aliases(left_text),
        normalize_aliases(right_text),
    )

    char_score = character_similarity(
        left_text,
        right_text,
    )

    print(f"\n{label}")
    print(f"Word TF-IDF:       {word_score:.3f}")
    print(f"Alias-aware TF-IDF:{alias_score:.3f}")
    print(f"Character TF-IDF:  {char_score:.3f}")


# Character overlap can soften spelling variation,
# but it is not semantic understanding.

print_comparison(
    "Abbreviation test",
    "Built ML pipelines for forecasting",
    "Machine learning engineer",
)

print_comparison(
    "Typo test",
    "Built Pythn apps with Streamlit",
    "Python Streamlit developer",
)