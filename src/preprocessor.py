
def normalize_line(line_text: str) -> str:
    """Applies normalization to a single line of code."""
    if not line_text:
        return ""
        
    normalized = line_text.lower()
    normalized = normalized.strip()
    normalized = ' '.join(normalized.split())
    # Additional cleanup (e.g., removing semicolons, parentheses) could go here
    return normalized

def preprocess_file(file_content: list) -> list:
    """Applies normalization to every line in a file."""
    return [normalize_line(line) for line in file_content]

def get_context(lines: list, line_index: int, window: int = 4) -> str:
    """
    Extracts the surrounding lines (context) for a given line index.
    A context window of 4 lines above and 4 lines below is standard.
    """
    start = max(0, line_index - window)
    end = min(len(lines), line_index + window + 1)
    
    context_lines = []
    for i in range(start, end):
        if i != line_index:
            context_lines.append(lines[i])
            
    # Normalize context lines before concatenating
    return " ".join([normalize_line(line) for line in context_lines])