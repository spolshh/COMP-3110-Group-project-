import os
import glob
from lhdiff import LHDiff
from xml_parser import parse_all_versions

# ==========================================
# CONFIGURATION
# ==========================================
# Change this path to the folder containing your file sets
DATASET_PATH = "./tests" 

def evaluate_directory(path):
    """
    Scans directory for files matching *_1.* (the base versions).
    Then looks for ALL subsequent versions defined in the corresponding XML.
    """
    print(f"Scanning directory: {path}...")
    
    # 1. Find all Base Files (Version 1)
    search_pattern = os.path.join(path, "*_1.*")
    base_files = glob.glob(search_pattern)
    
    total_files_checked = 0
    total_correct_mappings = 0
    total_lines_checked = 0
    
    if not base_files:
        print(f"No base files found matching '{search_pattern}'.")
        return

    for base_file_path in base_files:
        if base_file_path.endswith(".xml"): continue

        # Extract info: "tests/BaseTypes_1.java" -> dir="tests", base="BaseTypes", ext=".java"
        dirname, filename = os.path.split(base_file_path)
        name_root, ext = os.path.splitext(filename)
        
        if not name_root.endswith("_1"): continue
        base_name = name_root[:-2] # Remove "_1"
        
        xml_file_path = os.path.join(dirname, f"{base_name}.xml")
        
        if not os.path.exists(xml_file_path):
            print(f"Skipping {base_name}: XML Ground Truth not found.")
            continue

        # 2. Parse XML to find out which versions we need to test
        # returns { 1: {...}, 2: {...}, 3: {...} }
        truth_versions = parse_all_versions(xml_file_path)
        
        if not truth_versions:
            print(f"Skipping {base_name}: XML contained no valid version data.")
            continue

        print(f"Processing Group: {base_name}...")
        
        # Read Base Content (Version 1)
        try:
            with open(base_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content_base = f.read()
        except Exception as e:
            print(f"  Error reading base file: {e}")
            continue

        # 3. Iterate through all versions found in the XML
        for ver_num, truth_mapping in sorted(truth_versions.items()):
            # Version 1 is usually identity (comparing file to itself), we can skip or check it.
            # Usually we care about changes, so let's check if the file for this version exists.
            
            # Construct target filename: "BaseTypes_3.java"
            target_filename = f"{base_name}_{ver_num}{ext}"
            target_path = os.path.join(dirname, target_filename)
            
            if not os.path.exists(target_path):
                # If XML has Version 5 but file isn't there, skip
                continue
            
            print(f"  -> Comparing v1 vs v{ver_num} ({target_filename})...")
            
            try:
                with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content_target = f.read()
            except:
                print(f"     [Error reading {target_filename}]")
                continue

            # 4. Run LHDiff (Base vs Target)
            tool = LHDiff(content_base, content_target)
            computed_mapping = tool.run()
            
            # 5. Evaluate
            file_correct = 0
            file_total_lines = 0
            
            for old_idx, true_new_idx in truth_mapping.items():
                file_total_lines += 1
                
                # Get prediction
                predicted_indices = computed_mapping.get(old_idx, [])
                predicted_first = predicted_indices[0] if predicted_indices else None
                
                # Check correctness
                if true_new_idx is None:
                    if not predicted_indices: file_correct += 1
                else:
                    if predicted_first == true_new_idx:
                        file_correct += 1
            
            acc = (file_correct / file_total_lines * 100) if file_total_lines else 0
            print(f"     Accuracy: {acc:.2f}% ({file_correct}/{file_total_lines})")
            
            total_correct_mappings += file_correct
            total_lines_checked += file_total_lines
            total_files_checked += 1

    if total_lines_checked > 0:
        print("\n" + "="*40)
        print(f"OVERALL AVERAGE ACCURACY: {(total_correct_mappings/total_lines_checked)*100:.2f}%")
        print(f"Files Checked: {total_files_checked}")
        print("="*40)

def run_bonus_demo():
    from bonus_szz import BugIdentifier
    print("\n" + "="*40)
    print("RUNNING BONUS SZZ DEMO")
    print("="*40)
    # Demo data remains same...
    c1 = {'id': 'C1', 'msg': 'Init', 'file_prev': '', 'file_curr': 'lineA\nlineB', 'parent_id': None}
    c2 = {'id': 'C2', 'msg': 'Add bug', 'file_prev': 'lineA\nlineB', 'file_curr': 'lineA\nlineB\nif(bug)', 'parent_id': 'C1'}
    c3 = {'id': 'C3', 'msg': 'Fix bug #101', 'file_prev': 'lineA\nlineB\nif(bug)', 'file_curr': 'lineA\nlineB', 'parent_id': 'C2'}
    szz = BugIdentifier([c1, c2, c3])
    szz.identify_fixes()

if __name__ == "__main__":
    evaluate_directory(DATASET_PATH)
    run_bonus_demo()