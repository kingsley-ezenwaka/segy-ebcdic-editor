# segy_ebcdic_editor_2_0_3.py
# (c) Kingsley Ezenwaka (kezenwaka@gmail.com)

# v.2.0 - 2024.06.20

# v.2.0.1 - 2024.06.26 (Edited by Alejandro Lemmo)
# Modified to fixed wrong amount of padding in update_header() (line90).
	
# v.2.0.2 - 2024.07.04
# Modified to include update water column SV if different from value in traces.

# v.2.0.3 - 2024.08.03 (Edited by Alejandro Lemmo & Efrain Dinis)
# Modified to include: 
#	1. Add C02 LINE for no KPs files. 
#	2. Fix C11 SAMPLES/TRACE: Trace Samples  
#	3. C12 DATA TRACES: Traces - Previous values inverted -

# v.3.0 - 2025.02.25
# Implemented tktinter GUI wrapper

'''
** ALERT: THE SCRIPT ACTION CANNOT BE REVERSED **
** KEEP A BACKUP OF ALL SEGY FILES BEFORE RUNNING SCRIPT! **

The EBCDIC editor modifies the EBCDIC text header of all segy files in the folder.
It reads each file's text header and the first 50 trace headers, and re-writes
the following info in the text header:
- FILE NAME
- LINE NAME
- TRACE PER SAMPLE
- TOTAL TRACES
- WATER COLUMN SV (if different from traces)

On success, GUI will update with the list of successfully edited SegY files.

** FINAL ALERT: THE SCRIPT ACTION CANNOT BE REVERSED **
** KEEP A BACKUP OF ALL SEGY FILES BEFORE RUNNING SCRIPT! **
'''
import os
import tkinter as tk
from tkinter import filedialog
import segyio
import segyio.tools

# 
class EditManager():
    def __init__(self, fpath = '', files = ''):
        self.fpath = fpath
        self.files = files

    # get_dir method with tk.Entry widget arg
    def get_dir(self, entry):
        self.files = ''
        entry.delete(0, tk.END)
        entry.insert(0, filedialog.askdirectory())
        self.fpath = entry.get()

    # get_files method with tk.Listbox arg
    def get_files(self, listb, log_txt):
        # clears current list content
        listb.delete(0, 'end')

        # Attempts to find and load SEGy files names in directory
        try:
            folder_path = self.fpath
            flist = os.listdir(folder_path)
            file_names = [f for f in flist
                if os.path.isfile(os.path.join(folder_path,f))
                and f.endswith(".sgy")
            ]
            if file_names:
                self.files = file_names
                listb.insert(tk.END, *file_names) # Adds file names to Listbox widget
                updateview(log_txt, f"{len(file_names)} SEGY files loaded.\n") # Updates log
            else:
                pass
                updateview(log_txt, f"No SEGy files loaded.") # Updates log
        
        except Exception as e:
            updateview(log_txt, f"{e}. Please select a folder.")

    def read_segy(self, file_path):
        try:
            with segyio.open(file_path, "r", ignore_geometry=True) as segyfile:
                ebcdic_header = segyfile.text[0]
                # Convert EBCDIC to ASCII
                ascii_header = segyio.tools.wrap(ebcdic_header)
                
                # Retrieve the number of samples per trace
                samples_per_trace = segyfile.trace.shape

                # Retrieve the total number of traces
                total_traces = segyfile.tracecount

                # Iterate over first 50 traces to extract water column SV (value is static within file)
                SV = []
                for i in range(50):
                    trace_header = str(segyfile.header[i])
                    c = trace_header.find("WeatheringVelocity")
                    SV.append(int(trace_header[c+20: c+24]))
                water_column_SV = int(sum(SV)/len(SV))
                
                return [ascii_header, samples_per_trace, total_traces, water_column_SV]
            
        except Exception as e:
            return 

    def rewrite_header(self, segy_info, new_name):
        # Split header by lines
        header = segy_info[0].splitlines()
        
        # Update line name (line C02)
        part = new_name[:new_name.find("_KP")]
        linename = part[part.rfind("_")+1:]
        header[1] = header[1].replace(header[1], header[1][:10] + linename)
    
        # Update file name in text header (line C07)
        header[6] = header[6].replace(header[6][22:], new_name)
        
        # Add correct number of samples per trace (line C11)
        header[10] = header[10].replace(header[10][header[10].find("SAMPLES/TRACE: ")+14 : ], str(segy_info[2]))

        # Add correct number of traces (line 12)
        a = header[11].find("DATA TRACES: ")
        b = header[11].find("AUX. TRACES")
        header[11] = header[11].replace(header[11][a+13:b], str(segy_info[1]) + "    ", 1)     
        #header[11] = header[11].replace(" 1", " " + str(segy_info[1]), 1)

        # Update water column SV in line C22 if different from water column SV in trace
        c = header[21].lower().find("water velocity: ")
        SV_from_header = int(header[21][c+15 : -3])
        if not (SV_from_header == segy_info[3]):
            header[21] = header[21].replace(header[21][c:], f"Water velocity: {segy_info[3]} m/s")
            
        #Clean up each line in header
        new_header = ""
        i = 0
        for line in header:
            # Remove chars in front of CXX prefix
            i += 1
            num = str(i)
            if len(num) == 1:
                prefix = "C0" + num
            else:
                prefix = "C" + num
            c = line.find(prefix)
            line = line[c:]

            # Make up 80 chars for each line
            ccount = 79 - len(line)
            if ccount == 0:
                pass
            elif ccount < 0:
                line = line[0:79]
            elif ccount > 0:
                line = line + (" " * ccount)

            new_header = new_header + line + "\n"

        return new_header

    def update_all(self, log_txt):
        # Check current file list status
        if not self.files:
            # Update GUI log
            updateview(log_txt, f"No SEGy files found.")

        try:
            # Loop through SEGy file list to update each file's EBCDIC header
            for file in self.files:
                file_path = self.fpath + '\\' + file

                # Get segy file's info (EBCDIC header, traces and samples per trace)
                info = self.read_segy(file_path)
                
                # Rewrite the EBCDIC header with new info
                new_header = self.rewrite_header(info, file.rstrip(".sgy"))
                
                # Update the segy file with corrected EBCDIC header        
                with segyio.open(file_path, "r+", ignore_geometry=True) as segyfile:
                    segyfile.text[0] = new_header

                # Update GUI log
                updateview(log_txt, f"EBCDIC header updated successfully for {file}")

        except Exception as e:
            # Update GUI log
            updateview(log_txt, f"Failed to write SEG-Y file: {e}")
    
    def show_ebcdic(self, display_txt, list_item, log_txt):     #GUI display and log widgets passed in with index no of the file clicked on by user
        updateview(display_txt,'',1)
        try:
            # Make up full file path using the file's index number on loaded filie list
            file_name = self.files[list_item[0]]
            file_path = self.fpath + "\\" + file_name
            
            # Read the segy file's info and post the text header to display
            info = self.read_segy(file_path)
            updateview(display_txt, info[0], 1)
            
            # Post result to GUI log
            updateview(log_txt,f"File {file_name[:20]}...: Text header read successfully.")

        except Exception as e:
            updateview(log_txt, f"{str(e).capitalize()}. Please click to select a file in the list or Browse for a SEGy folder.")

# 'Clear' button function
def clear(em: EditManager, entryb, listb, display_txt, log_txt):
    # clears all class variables of the instantiated EditManager
    em.fpath = ''
    em.files = ''

    # clears contents of entry and listbox widgets
    entryb.delete(0, tk.END)
    listb.delete(0, tk.END)

    # clears the display widget
    updateview(display_txt,'',1)
    updateview(log_txt,f"File list cleared.\n")

# Function to update/clear GUI display widgets' text
def updateview(wdg, txt, clean_slate = 0):    # "clean_slate": 0 = update, 1 = clear

    # Enables normal state to modify widget text
    wdg.configure(state='normal')

    # Check if function was called from 'Clear' button
    if clean_slate == 1:
        wdg.delete('1.0','end')

    # Updates display widget with input text
    wdg.insert('end', "\n" + txt)

    # Scrolls to end of display (to show latest entry)
    if clean_slate == 0:
        wdg.see('end')

    # Disables normal state
    wdg.configure(state='disabled')

def editor_gui(editmgr):
    # main window
    root = tk.Tk()
    root.resizable(False, False)

    # GUI frames
    frm1 = tk.Frame(root,relief=tk.RIDGE,borderwidth=1)
    frm1.grid(row = 0, column = 0, padx = 0, pady = 0, columnspan=3, sticky='nsew')
    frm2 = tk.Frame(root,relief=tk.RIDGE,borderwidth=1)
    frm2.grid(row = 1, column = 0,padx = 0, pady = 0, sticky='nsew')
    frm3 = tk.Frame(root,relief=tk.RIDGE,borderwidth=1)
    frm3.grid(row = 1, column = 1, padx = 0, pady = 0)
    frm4 = tk.Frame(frm3,relief=tk.RIDGE,borderwidth=1)
    frm4.grid(row = 0, column = 0, padx = 0, pady = 0, sticky='nsew')
    frm5 = tk.Frame(frm3,relief=tk.RIDGE,borderwidth=1)
    frm5.grid(row = 0, column = 1, padx = 0, pady = 0)
    frm6 = tk.Frame(frm3,relief=tk.RIDGE,borderwidth=1)
    frm6.grid(row = 1, column = 0, padx = 0, pady = 0, columnspan=3, sticky='nsew')
    frm7 = tk.Frame(frm2,relief=tk.RIDGE,borderwidth=1)
    frm7.grid(row = 0, column = 0, padx = 0, pady = 0, sticky='nsew')

    frames = [root, frm1, frm2, frm3, frm4, frm5, frm6, frm7]
    for frame in frames:
        frame.rowconfigure(0,weight=1)
        frame.columnconfigure(0,weight=1)

    # Button widgets
    btn1 = tk.Button(frm1,width=15,text = 'Browse folder', command = lambda: editmgr.get_dir(ent))
    btn1.pack(padx = 10, pady = 5, side='left')

    btn2 = tk.Button(frm1,width=15,text = 'Get SEGY files list', command = lambda: editmgr.get_files(lbx, log))
    btn2.pack(padx = 5, pady = 5)

    btn3 = tk.Button(frm7,width=10,height=2,text = 'Read File', command = lambda: editmgr.show_ebcdic(display, lbx.curselection(), log))
    btn3.pack(padx = 5, pady=50)
    
    btn4 = tk.Button(frm7, text = 'Update All',width=10,height=3, command = lambda: editmgr.update_all(log))
    btn4.pack(expand='y',padx = 5, pady = 10)
    
    btn5 = tk.Button(frm7, text = 'Clear',width=10,height=1, command = lambda: clear(editmgr, ent, lbx, display, log))
    btn5.pack(padx = 5, pady = 50)

    btn6 = tk.Button(frm7, width=10,height=1,text = 'Exit', command = root.destroy)
    btn6.pack(padx = 5, pady = 20)

    # Entry widget for import folder dialog
    ent = tk.Entry(frm1,width=80)
    ent.pack(padx = 10, pady = 5, side='left',fill='y')

    # Listbox widget for import files list
    lbx = tk.Listbox(frm4,width=50,relief=tk.SUNKEN,borderwidth=1)
    lbx.grid(row = 0, column = 0, sticky='ns')
    
    # Display widget for files processing result
    display = tk.Text(frm5, state='disabled', width=60, height=30, relief=tk.SUNKEN, borderwidth=1)
    display.grid(row=0,column=0,padx=5,pady=3)
    
    # scrollbar widgets
    scr1 = tk.Scrollbar(frm4,command=lbx.yview)
    scr2 = tk.Scrollbar(frm4,orient='horizontal',command=lbx.xview)
    scr3 = tk.Scrollbar(frm5,command=display.yview)
    scr4 = tk.Scrollbar(frm5,orient='horizontal',command=display.xview)
    scr1.grid(row=0,column=1,sticky='nsew')
    scr2.grid(row=1,column=0,sticky='nsew')
    scr3.grid(row=0,column=1,sticky='nsew')
    scr4.grid(row=1,column=0,sticky='nsew')
    
    lbx['yscrollcommand'] = scr1.set
    lbx['xscrollcommand'] = scr2.set

    display['yscrollcommand'] = scr3.set
    display['xscrollcommand'] = scr4.set
    
    # Display widget for Log messages 
    log = tk.Text(frm6, state='disabled', height=3, relief=tk.SUNKEN, borderwidth=2)
    log.grid(row=0,column=0,padx=5,pady=3, sticky='ew')

    scr3 = tk.Scrollbar(frm6,command=log.yview)
    scr3.grid(row=0,column=1,sticky='nsew')
    log['yscrollcommand'] = scr3.set
    
    # Menu bar
    menubar = tk.Menu(root)

    # About and Help menus
    menubar.add_command(label='About')
    menubar.add_command(label='Help')
    root.config(menu=menubar)

    # Run GUI main loop
    root.mainloop()
    
def main():
    # Instantiate the SEGY editor
    em = EditManager()

    # Pass the editor to GUI function
    editor_gui(em)

if __name__ == "__main__":
    main()
