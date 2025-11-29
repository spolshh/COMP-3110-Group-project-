# evaluator.py

import pandas as pd
from typing import Dict, List, Tuple

# Mock data for demonstration (You'd replace this with running line_tracker.py)
def mock_tool_output(ground_truth_df: pd.DataFrame) -> Dict[str, Dict[int, List[int]]]:
    """
    CONCEPTUAL: Generates mock tool output. 
    A real implementation would run track_lines() on the actual files.
    """
    mock_output = {}
    for file_name in ground_truth_df['file_name'].unique():
        # Mock tool output: 90% correct, 10% spurious 1:1 match
        mock_output[file_name] = {
            10: [10],   # Correct 1:1
            15: [15],   # Correct 1:1
            40: [41, 42], # Partially correct split (missed line 43)
            5: [50],    # Correct reorder
            100: [101] # Spurious match (tool found a match where none exists in GT)
        }
    return mock_output

def calculate_metrics(ground_truth: pd.DataFrame, tool_output: Dict[str, Dict[int, List[int]]]) -> Tuple[float, float, float, float]:
    """
    Calculates the required evaluation metrics: %Correct, %Spurious, %Eliminate.
    """
    total_gt_mappings = ground_truth.shape[0]
    total_tool_mappings = 0 # Count tool outputs
    correct_matches = 0
    
    # --- 1. COUNT CORRECT MATCHES ---
    
    # Convert GT to a simpler dictionary for lookup: {file_name: {old_start: set(new_lines)}}
    gt_map = {}
    for _, row in ground_truth.iterrows():
        file_name = row['file_name']
        if file_name not in gt_map:
            gt_map[file_name] = {}
        
        # Handle N:M mappings by treating them as a block of lines
        old_lines = set(range(row['old_start'], row['old_end'] + 1))
        new_lines = set(range(row['new_start'], row['new_end'] + 1))
        
        for old_line in old_lines:
            gt_map[file_name][old_line] = new_lines

    # Compare tool output against GT
    for file_name, tool_file_output in tool_output.items():
        if file_name not in gt_map: continue

        for old_line, mapped_new_lines in tool_file_output.items():
            total_tool_mappings += 1
            
            # Check if this old_line is tracked in the ground truth
            if old_line in gt_map[file_name]:
                gt_new_lines = gt_map[file_name][old_line]
                
                # Check for correctness: Does the tool map to the correct set of lines?
                # For simplicity in this mock, we check if all tool-mapped lines are in the GT set.
                if all(nl in gt_new_lines for nl in mapped_new_lines):
                    correct_matches += 1

    # --- 2. CALCULATE METRICS ---
    
    # %Correct: Percentage of all mappings in GT that the tool correctly found.
    # Note: %Correct definition can vary (correctly identified line vs. correctly identified block).
    percent_correct = (correct_matches / total_gt_mappings) * 100 if total_gt_mappings > 0 else 0.0

    # %Spurious: Tool found a match where GT says nothing changed (False Positives).
    spurious_matches = 0 # Tool map where GT has no corresponding entry
    
    # This calculation is tricky without real full file data (deleted/added lines).
    # Placeholder: Assuming any tool map that doesn't perfectly match a GT entry is potentially spurious.
    percent_spurious = 10.0 # Placeholder for conceptual 10% Spurious rate
    
    # %Eliminate: GT says a line was changed/tracked, but tool missed it (False Negatives).
    percent_eliminate = 10.0 # Placeholder for conceptual 10% Elimination rate
    
    # %Change: Correctly identified mappings divided by the number of actual changed lines (GT changes)
    # A true calculation requires knowing the total number of changed lines from the full file diff.
    percent_change = percent_correct # Placeholder, often similar to %Correct

    return percent_correct, percent_change, percent_spurious, percent_eliminate

def evaluate():
    """Runs the mock evaluation."""
    # 1. Create Ground Truth
    # create_mock_ground_truth(file_path="evaluation/mock_ground_truth.csv")
    
    # 2. Read Ground Truth
    try:
        # Using a dummy DataFrame since mock_data.py isn't executed here
        gt_df = pd.DataFrame([
            ('file_01.java', 10, 10, 10, 10, '1:1'),
            ('file_01.java', 15, 15, 15, 15, '1:1'),
            ('file_02.c', 40, 40, 41, 43, '1:N_SPLIT'),
            ('file_03.py', 5, 5, 50, 50, '1:1_REORDER'),
        ], columns=['file_name', 'old_start', 'old_end', 'new_start', 'new_end', 'mapping_type'])
    except Exception as e:
        print(f"Error reading mock data: {e}. Using conceptual data.")
        return

    # 3. Generate Mock Tool Output (Replace with actual tool run)
    tool_output = mock_tool_output(gt_df)
    
    # 4. Calculate Metrics
    correct, change, spurious, eliminate = calculate_metrics(gt_df, tool_output)
    
    print("\n--- LHDiff Tool Evaluation Results (Conceptual) ---")
    print(f"Total GT Mappings: {gt_df.shape[0]}")
    print(f"| %Correct | {correct:.2f}%")
    print(f"| %Change  | {change:.2f}%")
    print(f"| %Spurious| {spurious:.2f}% (False Positives)")
    print(f"| %Eliminate| {eliminate:.2f}% (False Negatives)")
    print("--------------------------------------------------")
    
    # 5. Save Results (Conceptual)
    results_df = pd.DataFrame({
        'Metric': ['%Correct', '%Change', '%Spurious', '%Eliminate'],
        'Value': [correct, change, spurious, eliminate]
    })
    results_df.to_csv("evaluation/results.csv", index=False)

if __name__ == '__main__':
    evaluate()