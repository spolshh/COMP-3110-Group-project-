# line_tracker.py

from preprocessor import preprocess_file, get_context
from similarity_metrics import (
    generate_simhash, hamming_distance, 
    content_similarity, context_similarity, 
    calculate_combined_score
)
from unix_diff_matcher import apply_unix_diff
from linesplit_detector import detect_line_split

MATCH_THRESHOLD = 0.75 # Threshold for final 1:1 match in Step 4
CANDIDATE_K = 15       # Number of candidates to consider in Step 3

def track_lines(old_file_lines: list, new_file_lines: list) -> dict:
    """
    Main function implementing the 5-step LHDiff algorithm.
    Returns a dictionary mapping {old_line_num: [new_line_num, ...]}
    """
    # 1. PREPROCESSING
    old_normalized = preprocess_file(old_file_lines)
    new_normalized = preprocess_file(new_file_lines)
    
    # 2. DETECT UNCHANGED LINES (UNIX DIFF)
    # The lists will contain (line_num, normalized_content, context)
    initial_maps, left_list, right_list = apply_unix_diff(old_normalized, new_normalized)
    
    mapped_lines = initial_maps.copy()
    
    # --- Data structures for easier lookup ---
    # In a real tool, left/right lists would be populated by apply_unix_diff
    # For this mock, we assume left/right lists are already populated with all change data
    
    # 3. GENERATE CANDIDATE LIST (Simhash for efficiency)
    right_hash_map = {} # {new_num: hash_value}
    for num, content, context in right_list:
        hash_value = generate_simhash(content, context)
        right_hash_map[num] = hash_value

    candidate_maps = {} # {old_num: [new_num_1, new_num_2, ...]}
    for old_num, old_content, old_context in left_list:
        old_hash = generate_simhash(old_content, old_context)
        
        # Calculate Hamming distance to all right lines and select top K
        distances = []
        for new_num, new_hash in right_hash_map.items():
            distances.append((new_num, hamming_distance(old_hash, new_hash)))
            
        distances.sort(key=lambda x: x[1]) # Sort by distance (ascending)
        candidate_maps[old_num] = [d[0] for d in distances[:CANDIDATE_K]]

    # 4. RESOLVE CONFLICT (Textual Similarity)
    unmapped_left = []
    
    # Create reverse lookup for content/context (Conceptual)
    right_data = {num: (content, context) for num, content, context in right_list}
    
    for old_num, old_content, old_context in left_list:
        if old_num in mapped_lines: continue # Already mapped by Step 2 or previous iteration

        best_match = None
        max_score = -1.0
        
        for new_num in candidate_maps.get(old_num, []):
            if new_num in mapped_lines.values(): continue # Already mapped as a 1:1 target
            
            new_content, new_context = right_data.get(new_num, ('', ''))
            
            # Recalculate score using textual similarity (Levenshtein + Cosine)
            c_sim = content_similarity(old_content, new_content)
            x_sim = context_similarity(old_context, new_context)
            combined_score = calculate_combined_score(c_sim, x_sim)

            if combined_score > max_score:
                max_score = combined_score
                best_match = new_num

        if best_match is not None and max_score >= MATCH_THRESHOLD:
            mapped_lines[old_num] = [best_match]
            # Remove line from subsequent consideration in right_list for 1:1 maps
        else:
            unmapped_left.append((old_num, old_content, old_context))

    # 5. DETECT LINE SPLIT (1:N maps)
    # Prepare remaining right list for line split detector (contiguous chunks)
    remaining_right_data = [(num, content) for num, content, context in right_list 
                            if num not in [item[0] for sublist in mapped_lines.values() for item in sublist]]
                            
    for old_num, old_content, old_context in unmapped_left:
        # NOTE: A real implementation needs to search through *contiguous blocks* # in the remaining_right_data, not the whole list at once.
        mapping = detect_line_split(old_content, remaining_right_data)
        if mapping:
            mapped_lines[old_num] = mapping # mapping is a list of new line numbers
            
    return mapped_lines

# --- Example Usage (Conceptual) ---
def main():
    old_code = ["def foo(a):", "    return a + 1"]
    new_code = ["def bar(a):", "    # This line added", "    return a + 1"]
    
    # NOTE: The conceptual placeholder data will prevent this from returning real maps
    # without replacing the Step 2-4 conceptual logic.
    # mapping = track_lines(old_code, new_code)
    # print("Mapping Result:", mapping)

if __name__ == '__main__':
    main()