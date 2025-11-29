# src/unix_diff_matcher.py

import difflib
from src.preprocessor import get_context

# Structure for line data: (line_num, normalized_content, context_text)
LineData = tuple[int, str, str]

def apply_unix_diff(old_lines: list, new_lines: list, old_normalized: list, new_normalized: list) -> tuple:
    """
    Uses difflib to find identical lines and separates the rest into change blocks.
    
    Returns:
    - mapped_lines: dict {old_line_num: [new_line_num]} for identical lines (1-based index).
    - left_list: list of unmapped LineData from old file (deleted/changed lines).
    - right_list: list of unmapped LineData from new file (added/changed lines).
    """
    mapped_lines: dict[int, list[int]] = {}
    
    # Use the normalized versions for matching
    matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Map identical lines (1:1)
            for k in range(i2 - i1):
                # Using 1-based indexing for the project report/output
                old_num = i1 + k + 1
                new_num = j1 + k + 1
                mapped_lines[old_num] = [new_num]

    # Identify indices that were NOT mapped (0-based)
    old_unmapped_indices = set(range(len(old_lines))) - set(i - 1 for i in mapped_lines.keys())
    new_unmapped_indices = set(range(len(new_lines))) - set(j[0] - 1 for j in mapped_lines.values())
    
    left_list: list[LineData] = []
    right_list: list[LineData] = []

    # Populate Left List (Unmapped Old Lines)
    for i in sorted(list(old_unmapped_indices)):
        old_num = i + 1
        content = old_normalized[i]
        # Context is generated from the normalized file content
        context = get_context(old_normalized, i)
        left_list.append((old_num, content, context))

    # Populate Right List (Unmapped New Lines)
    for j in sorted(list(new_unmapped_indices)):
        new_num = j + 1
        content = new_normalized[j]
        context = get_context(new_normalized, j)
        right_list.append((new_num, content, context))

    return mapped_lines, left_list, right_list