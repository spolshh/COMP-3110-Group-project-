# src/linesplit_detector.py

from src.similarity_metrics import normalized_levenshtein_distance

def detect_line_split(old_content: str, remaining_right_list: list) -> list:
    """
    Detects 1-to-N mappings by iteratively combining adjacent lines and checking similarity.
    (Remaining right list: [(new_num, content), ...])
    """
    if not remaining_right_list:
        return []

    best_match_indices = []
    current_similarity = -1.0
    FINAL_SPLIT_THRESHOLD = 0.65 

    for i in range(len(remaining_right_list)):
        # Combined content up to the current line (i)
        combined_content = "".join([item[1] for item in remaining_right_list[:i+1]])
        
        # Calculate similarity (1 - Normalized LD)
        sim = 1.0 - normalized_levenshtein_distance(old_content, combined_content)
        
        if sim >= current_similarity:
            current_similarity = sim
            # Store the line numbers corresponding to the current best match
            best_match_indices = [item[0] for item in remaining_right_list[:i+1]]
        elif sim < current_similarity:
            # Stop when similarity decreases (heuristic)
            break
            
    # Return the best match if it exceeds the final threshold
    if current_similarity >= FINAL_SPLIT_THRESHOLD:
        return best_match_indices
    else:
        return []