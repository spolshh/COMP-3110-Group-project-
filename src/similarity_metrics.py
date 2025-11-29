# src/similarity_metrics.py

# --- Imports for external libraries ---
try:
    from datasketch import SimHash 
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    print("WARNING: datasketch or scikit-learn not found. Simhash/TFIDF will use placeholders.")

# Global vectorizer for context similarity (initialized lazily)
CONTEXT_VECTORIZER = None

# --- Step 3: Efficient Candidate Generation ---

def generate_simhash(line_content: str, context_text: str, num_bits: int = 64) -> int:
    """Generates a Simhash value for the combined content."""
    combined_text = (line_content + " " + context_text).encode('utf8')
    try:
        s_hash = SimHash(combined_text, num_bits=num_bits)
        return s_hash.hash
    except NameError:
        # Placeholder if datasketch is not installed
        return hash(combined_text) % (2**num_bits)


def hamming_distance(hash1: int, hash2: int) -> int:
    """Calculates the number of differing bits between two Simhash values."""
    return bin(hash1 ^ hash2).count('1')

# --- Step 4: Accurate Match Resolution ---

def get_context_similarity(context1: str, context2: str) -> float:
    """
    Calculates Cosine Similarity on context vectors (TF-IDF).
    """
    global CONTEXT_VECTORIZER
    
    if not CONTEXT_VECTORIZER:
        # Initialize TF-IDF Vectorizer
        CONTEXT_VECTORIZER = TfidfVectorizer(stop_words='english')

    # Handle empty contexts
    if not context1 and not context2:
        return 1.0
    if not context1 or not context2:
        return 0.0

    documents = [context1, context2]
    try:
        # Fit and transform requires a list of documents
        tfidf_matrix = CONTEXT_VECTORIZER.fit_transform(documents)
        # Calculate cosine similarity (returns matrix, we take the 1,0 element)
        sim_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return sim_matrix[0][0]
    except NameError:
        # Placeholder if scikit-learn is not installed
        return 1.0 if context1 == context2 else 0.5


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculates the standard Levenshtein distance (edit distance)."""
    if len(s1) < len(s2):
        s1, s2 = s2, s1

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def normalized_levenshtein_distance(s1: str, s2: str) -> float:
    """Normalizes LD to a score between 0 and 1."""
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 0.0
        
    ld = levenshtein_distance(s1, s2)
    return ld / max_len

def content_similarity(s1: str, s2: str) -> float:
    """Content Sim. = 1 - Normalized LD."""
    return 1.0 - normalized_levenshtein_distance(s1, s2)

def calculate_combined_score(content_sim: float, context_sim: float) -> float:
    """
    Calculates the combined similarity score (0.6 * Content + 0.4 * Context).
    """
    return (0.6 * content_sim) + (0.4 * context_sim)