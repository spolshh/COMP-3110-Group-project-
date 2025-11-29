# run_test_set.py

import pandas as pd
from src.line_tracker import track_lines, read_file
from evaluation.evaluator import calculate_metrics_with_bonus # Import the evaluation function

# --- 1. Load Data ---
# Read the two Java files
old_lines = read_file("ArrayReference_1.java")
new_lines = read_file("ArrayReference_2.java")

# Load the XML-parsed ground truth (saved as CSV in the previous step)
ground_truth_df = pd.read_csv("ArrayReference_ground_truth.csv")

# NOTE: Since this is just one change, we use a simple mock commit message.
COMMIT_MESSAGE = "Bug fix: Corrected array element type checking"

# --- 2. Run the LHDiff Tool ---
print("Running LHDiff line_tracker...")
# The key for the tool output should be the file name
tool_output_map = {
    "ArrayReference_1.java": track_lines(old_lines, new_lines, COMMIT_MESSAGE)
}

# --- 3. Run Evaluation ---
print("\nComparing Tool Output against Ground Truth...")
# The evaluator expects a DataFrame of all ground truth mappings
results = calculate_metrics_with_bonus(ground_truth_df, tool_output_map)

# --- 4. Print Results ---
if results:
    print("\n--- LHDiff Performance Metrics ---")
    results_df = pd.DataFrame(results.items(), columns=['Metric', 'Value'])
    print(results_df.to_markdown(index=False))

    # Optional: Print the detailed tool output for manual inspection
    print("\n--- Tool's Mapped Lines ---")
    tool_map = tool_output_map["ArrayReference_1.java"]
    for old_num, result in tool_map.items():
        # result is a list: [new_line_num1, new_line_num2, ..., bug_potential_string]
        new_lines = [r for r in result if isinstance(r, int)]
        category = result[-1] if isinstance(result[-1], str) else "NONE"
        print(f"Old Line {old_num}: Mapped to {new_lines} | Category: {category}")