import math
import re
from collections import Counter

def preprocess_line(line):
    """
    Standardizes a line for comparison: 
    - Trims whitespace
    - Lowercases
    - Normalizes internal spacing
    """
    line = line.strip().lower()
    line = re.sub(r'\s+', ' ', line)
    return line

def levenshtein_distance(s1, s2):
    """
    Calculates the Levenshtein distance between two strings.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def normalized_levenshtein(s1, s2):
    """
    Returns a score between 0.0 (different) and 1.0 (identical).
    """
    max_len = max(len(s1), len(s2))
    if max_len == 0: return 1.0
    dist = levenshtein_distance(s1, s2)
    return 1.0 - (dist / max_len)

def cosine_similarity(text1, text2):
    """
    Calculates Cosine Similarity for Context.
    """
    vec1 = Counter(text1.split())
    vec2 = Counter(text2.split())
    
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    
    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    if not denominator:
        return 0.0
    return numerator / denominator

def simple_simhash(text):
    """
    Generates a 32-bit integer fingerprint for a string using a simple SimHash approach.
    """
    features = text.split()
    v = [0] * 32
    for feature in features:
        h = hash(feature)
        for i in range(32):
            bit = (h >> i) & 1
            if bit: v[i] += 1
            else:   v[i] -= 1
    fingerprint = 0
    for i in range(32):
        if v[i] > 0:
            fingerprint |= (1 << i)
    return fingerprint

def hamming_distance(h1, h2):
    """
    Calculates hamming distance between two 32-bit integers.
    """
    x = h1 ^ h2
    return bin(x).count('1')