# SegY-EBCDIC-Editor

A Tkinter GUI program wrapped around a Python script for updating SegY EBCDIC text headers.

SegY files are often created with incorrect/missing info in their EBCDIC text headers; there are some software to manually edit and update these info but they can be time-consuming to do for each single file. The SegY-EBCDIC-Editor automates this process, along with an easy-to-use GUI user interface for users who are not comfortable working from command line.

The program takes a list of all SEGY files in folder, and loops through the list to read each file's EBCDIC header and the first 50 trace headers, and re-writes the following info in the text header:
- FILE NAME
- TRACE PER SAMPLE
- TOTAL TRACES
- WATER COLUMN SV (if different from traces)

On success, GUI will display with the list of successfully edited SegY files.

The program's editing script is configured for use with the text format in "EBCDIC_template.txt" (in folder), so it will not work properly for a different template (which may have the script's target string characters on different lines in the text header).

If required for use with a different template, send a copy of the template to k3z3nw4k4@gmail.com to revise the script for you at no cost.

## How To Use

### EXE file (Windows only):

To use:
- Simply double-click the "segy-editor.exe" file to open the program.
- Click on "Browse" to select the folder with SegY files, and then "Get SEGY files list" to load the SegY files.
- You can view the current EBCDIC text of any of the loaded SegY files by selecting the file and clicking "Read File".
- Click on "Update All" to update the EBCDIC text of all loaded SegY files (note that this will overwrite the original EBCIDIC text, so ensure to keep backups before updating).

**WARNING: THE SCRIPT ACTION CANNOT BE REVERSED; KEEP A BACKUP OF ALL SEGY FILES BEFORE RUNNING THE PROGRAM!**

### Python File (Linux & Windows):

The repository is bundled with the Python py file.

1. Install python (version 3 minimum required). Skip this step if python is already installed. Download and install from https://www.python.org/downloads/. Ensure to check on "Add Python to environment variables" during installation.

2. Install the segyio library. Also skip if segyio is already installed. To install, just open command prompt (cmd) and type/enter: `python -m pip install segyio`

3. You can now run the script. Simply copy to the folder containing the segy files (ensure to make a backup of the files first), then double-click the script to run. To see a textual read-out, you can instead open CMD from the folder and type (without quotes): `python segy_ebcdic_editor_3_0.py`

**WARNING: THE SCRIPT ACTION CANNOT BE REVERSED; KEEP A BACKUP OF ALL SEGY FILES BEFORE RUNNING THE PROGRAM!**

## Acknowledgements

- This program utilizes the `segyio` library for reading and writing the texts to the SegY files. `segyio` developed in 2018 by Equinor's Software Innovation team (led by Jørgen Kvalsvik)). Further details can be found at the (segyio repository)[https://github.com/equinor/segyio].


## Revision History

segy_ebcdic_editor_2_0_2.py
(c) Kingsley Ezenwaka (kezenwaka@gmail.com)

v.2.0 - 2024.06.20

v.2.0.1 - 2024.06.26 (Edited by Alejandro Lemmo)
- Modified to fixed wrong amount of padding in update_header() (line90).
	
v.2.0.2 - 2024.07.04
- Modified to include update water column SV if different from value in traces.

v.2.0.3 - 2024.08.03 (Edited by Alejandro Lemmo & Efrain Dinis)
- Modified to include: 
	1. Add C02 LINE for no KPs files. 
	2. Fix C11 SAMPLES/TRACE: Trace Samples  
	3. C12 DATA TRACES: Traces - Previous values inverted -

v.3.0 - 2025.02.25
- Implemented tktinter GUI wrapper.