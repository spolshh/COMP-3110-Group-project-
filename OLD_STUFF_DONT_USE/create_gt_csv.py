# create_gt_csv.py (Run this once to fix the FileNotFoundError)

import xml.etree.ElementTree as ET
import pandas as pd
from typing import Dict, Set

def parse_xml_ground_truth(xml_file_path: str) -> Dict[int, Set[int]]:
    """
    Parses the ArrayReference.xml file to extract the ground truth line mappings.
    Returns: A dictionary mapping old line numbers to a set of new line numbers.
    """
    try:
        tree = ET.parse(xml_file_path)
    except FileNotFoundError:
        print(f"Error: XML file not found at {xml_file_path}. Ensure it's in the root folder.")
        return {}
        
    root = tree.getroot()
    ground_truth_map: Dict[int, Set[int]] = {}
    
    version_2 = root.find("VERSION[@NUMBER='2']")
    if version_2 is None:
        print("Error: Could not find VERSION NUMBER='2' in the XML.")
        return ground_truth_map

    for location_tag in version_2.findall('LOCATION'):
        orig_line_str = location_tag.get('ORIG')
        new_line_str = location_tag.get('NEW')
        
        try:
            orig_line = int(orig_line_str)
            new_line = int(new_line_str)
        except (ValueError, TypeError):
            continue
            
        if orig_line not in ground_truth_map:
            ground_truth_map[orig_line] = set()
            
        # -1 means the line was deleted (unmapped)
        if new_line != -1:
            ground_truth_map[orig_line].add(new_line)
            
    return ground_truth_map

# 1. Parse the XML
xml_file = "ArrayReference.xml"
ground_truth = parse_xml_ground_truth(xml_file)

# 2. Convert to DataFrame (using the required project structure)
gt_list = []
for orig, new_set in ground_truth.items():
    # Since the ground truth only contains start/end for 1:1 and N:1, we use a simplified structure
    if new_set:
        min_new = min(new_set)
        max_new = max(new_set)
        # Note: We assume the mapping block is contiguous (start=end for old line)
        gt_list.append({
            'file_name': 'ArrayReference_1.java',
            'old_start': orig, 
            'old_end': orig, 
            'new_start': min_new, 
            'new_end': max_new, 
            'mapping_type': '1:1_OR_N:M'
        })
    else:
        # For deleted lines, we still include the row for metric calculation
        gt_list.append({
            'file_name': 'ArrayReference_1.java',
            'old_start': orig, 
            'old_end': orig, 
            'new_start': -1, 
            'new_end': -1, 
            'mapping_type': 'DELETED'
        })

columns = ['file_name', 'old_start', 'old_end', 'new_start', 'new_end', 'mapping_type']
gt_df = pd.DataFrame(gt_list, columns=columns)

# 3. Save the dataset to the expected CSV file name
output_file_name = "ArrayReference_ground_truth.csv"
gt_df.to_csv(output_file_name, index=False)

print(f"✅ Success! Created the Ground Truth file: '{output_file_name}'")