# linesplit_detector.py

from similarity_metrics import normalized_levenshtein_distance

def detect_line_split(old_content: str, remaining_right_list: list) -> list:
    """
    Detects 1-to-N mappings (line splits) by iteratively combining adjacent
    unmapped lines in the new file and checking similarity.
    """
    if not remaining_right_list:
        return []

    # remaining_right_list structure: [(new_num, content), ...]
    
    best_match_indices = []
    current_similarity = -1.0
    
    # We only look at contiguous blocks, starting from the first remaining line
    for i in range(len(remaining_right_list)):
        
        # Iteratively build the combined new line text
        combined_content = "".join([item[1] for item in remaining_right_list[:i+1]])
        
        # Calculate similarity (1 - Normalized LD)
        sim = 1.0 - normalized_levenshtein_distance(old_content, combined_content)
        
        if sim > current_similarity:
            current_similarity = sim
            # Store the line numbers
            best_match_indices = [item[0] for item in remaining_right_list[:i+1]]
        elif sim < current_similarity:
            # Stop when similarity decreases (Heuristic used in LHDiff)
            break
            
    # Apply a final threshold check for the best match found
    FINAL_SPLIT_THRESHOLD = 0.65 
    if current_similarity >= FINAL_SPLIT_THRESHOLD:
        return best_match_indices
    else:
        return []