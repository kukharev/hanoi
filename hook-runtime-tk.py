import os
import sys
import tkinter

tk_dir = os.path.dirname(tkinter.__file__)
tcl_dir = os.path.join(tk_dir, 'tcl')

tcl_version = None
tk_version = None
for d in os.listdir(tcl_dir):
    if d.startswith('tcl'):
        tcl_version = d
    if d.startswith('tk'):
        tk_version = d

if tcl_version:
    os.environ['TCL_LIBRARY'] = os.path.join(tcl_dir, tcl_version)
if tk_version:
    os.environ['TK_LIBRARY'] = os.path.join(tcl_dir, tk_version)
