LHDiff & SZZ Implementation

This is a Python implementation of the LHDiff (Language-Independent Hybrid Line Mapping) technique and the SZZ Algorithm (Bonus) for tracking bug-introducing changes.
Project Structure

    lhdiff.py: Core implementation of the LHDiff algorithm (preprocessing, SimHash, Hybrid Scoring).

    utils.py: Helper functions for Levenshtein distance, Cosine Similarity, and SimHash.

    xml_parser.py: Utility to parse the ground truth XML files provided in the dataset.

    bonus_szz.py: Implementation of the Bug Identifying Logic (SZZ).

    main.py: Entry point to run evaluations and demos.

How to Run

    Prepare Data:

        Create a folder (e.g., dataset_folder) in the project root.

        Place your test files inside. The tool expects triplets of files for each test case:

            Name_1.ext (Old version, e.g., ArrayReference_1.java or Test_1.cpp)

            Name_2.ext (New version, e.g., ArrayReference_2.java or Test_2.cpp)

            Name.xml (Ground truth mapping, e.g., ArrayReference.xml)

    Configure:

        Open main.py.

        Update the DATASET_PATH variable to point to your data folder.

        DATASET_PATH = "./dataset_folder"

    Execute:

        Run the script using Python 3:

        python main.py

Features

    Language Independent: Works on Java, C++, Python, or any text-based source code.

    Modular Design: Separated concerns into distinct files.

    Zero Dependencies: Runs on standard Python 3 without pip install.

    Bonus SZZ: Includes a simulation of the bug-tracking algorithm at the end of execution.