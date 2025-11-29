# src/line_tracker.py

from src.preprocessor import preprocess_file, get_context
from src.similarity_metrics import (
    generate_simhash, hamming_distance, 
    content_similarity, get_context_similarity, 
    calculate_combined_score
)
from src.unix_diff_matcher import apply_unix_diff
from src.linesplit_detector import detect_line_split
from src.metadata_analyzer import analyze_commit_message, get_change_type_risk, categorize_bug_potential

MATCH_THRESHOLD = 0.75 
CANDIDATE_K = 15      

def read_file(filepath: str) -> list[str]:
    """Helper function to read content into a list of lines."""
    try:
        with open(filepath, 'r') as f:
            # Keep original lines for context in debugging, but normalized lines are what's processed
            return [line.strip('\n') for line in f.readlines()]
    except FileNotFoundError:
        return []

def track_lines(old_file_lines: list, new_file_lines: list, commit_message: str = "") -> dict: 
    """
    Main function implementing the 5-step LHDiff algorithm, now including bug potential.
    Returns: {old_line_num: [new_line_num(s), bug_potential_string]}
    """
    
    # 1. ANALYZE METADATA (Bonus Step)
    commit_intent = analyze_commit_message(commit_message)
    
    # 2. PREPROCESSING & UNIX DIFF (Steps 1 & 2)
    old_normalized = preprocess_file(old_file_lines)
    new_normalized = preprocess_file(new_file_lines)
    initial_maps, left_list, right_list = apply_unix_diff(
        old_file_lines, new_file_lines, old_normalized, new_normalized
    )
    
    # Map identical lines as NEUTRAL_CHANGE
    mapped_lines = {k: [v[0], 'NEUTRAL_CHANGE'] for k, v in initial_maps.items()}
    
    right_data = {num: (content, context) for num, content, context, in right_list}
    
    # 3. GENERATE CANDIDATE LIST (Simhash)
    right_hashes = []
    for num, content, context in right_list:
        hash_value = generate_simhash(content, context)
        right_hashes.append((num, hash_value))

    candidate_maps = {} 
    for old_num, old_content, old_context in left_list:
        old_hash = generate_simhash(old_content, old_context)
        
        distances = []
        for new_num, new_hash in right_hashes:
            distances.append((new_num, hamming_distance(old_hash, new_hash)))
            
        distances.sort(key=lambda x: x[1])
        candidate_maps[old_num] = [d[0] for d in distances[:CANDIDATE_K]]

    # 4. RESOLVE CONFLICT (Textual Similarity)
    unmapped_left_for_step_5 = []
    mapped_new_lines_step_4 = set()
    
    for old_num, old_content, old_context in left_list:
        # Check if already mapped in Step 2 or 4
        if old_num in mapped_lines: continue 

        best_match = None
        max_score = -1.0
        
        for new_num in candidate_maps.get(old_num, []):
            # Check if new line is already used in Step 2 or 4
            if new_num in mapped_new_lines_step_4 or new_num in [v[0] for v in mapped_lines.values() if len(v)==2]: continue
            
            new_content, new_context = right_data.get(new_num, ('', ''))
            
            c_sim = content_similarity(old_content, new_content)
            x_sim = get_context_similarity(old_context, new_context)
            combined_score = calculate_combined_score(c_sim, x_sim)

            if combined_score > max_score:
                max_score = combined_score
                best_match = new_num

        if best_match is not None and max_score >= MATCH_THRESHOLD:
            # Categorize the change before mapping
            change_risk = get_change_type_risk(max_score)
            bug_potential = categorize_bug_potential(commit_intent, change_risk)
            
            mapped_lines[old_num] = [best_match, bug_potential] 
            mapped_new_lines_step_4.add(best_match)
        else:
            unmapped_left_for_step_5.append((old_num, old_content))

    # 5. DETECT LINE SPLIT (1:N maps)
    all_mapped_new_lines = set(n for sublist in mapped_lines.values() for n in sublist if isinstance(n, int))
    remaining_right_data = [
        (num, content) for num, content, context in right_list 
        if num not in all_mapped_new_lines
    ]
    
    for old_num, old_content in unmapped_left_for_step_5:
        mapping = detect_line_split(old_content, remaining_right_data)
        if mapping:
            # Assume 1:N split is a major structural change
            change_risk = 'HIGH_RISK_MAJOR_REWRITE'
            bug_potential = categorize_bug_potential(commit_intent, change_risk)
            
            # Append the bug potential string to the list of new line numbers
            mapped_lines[old_num] = mapping + [bug_potential] 
            
            # Remove mapped lines from remaining_right_data to avoid reuse
            remaining_right_data = [item for item in remaining_right_data if item[0] not in mapping]
            
    # Sort the final map by old line number
    sorted_map = {k: mapped_lines[k] for k in sorted(mapped_lines.keys())}
    return sorted_map