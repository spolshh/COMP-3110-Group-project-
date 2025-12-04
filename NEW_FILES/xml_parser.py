import xml.etree.ElementTree as ET

def parse_all_versions(xml_path):
    """
    Parses the XML file and extracts mappings for ALL versions found.
    
    Returns:
        dict: { version_number (int): { old_line_idx: new_line_idx } }
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        all_versions_truth = {}
        
        # Iterate over every <VERSION> tag found in the XML
        for version in root.findall('VERSION'):
            try:
                ver_num = int(version.get('NUMBER'))
            except (ValueError, TypeError):
                continue

            ground_truth = {}
            for loc in version.findall('LOCATION'):
                try:
                    orig = int(loc.get('ORIG'))
                    new_val_str = loc.get('NEW')
                    new_loc = int(new_val_str)
                    
                    # Convert 1-based to 0-based indexing
                    orig_idx = orig - 1
                    
                    if new_loc == -1:
                        ground_truth[orig_idx] = None
                    else:
                        ground_truth[orig_idx] = new_loc - 1
                except (ValueError, TypeError):
                    continue
            
            all_versions_truth[ver_num] = ground_truth
                        
        return all_versions_truth
    except Exception as e:
        print(f"Error parsing XML {xml_path}: {e}")
        return {}