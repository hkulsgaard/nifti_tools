import tkinter as tk
from tkinter import filedialog as fd

def selectFiles(folder):
# This function opens a window for multiple file seleccion

	# creates the main window
	root = tk.Tk()

	# create an instance of the open file dialog assigned to the main window
	diag = fd.Open(root)

	# set the file types to be filtered (parameterizable)
	filetypes = (('Nifti Image', ['*.nii','*.nii.gz']), ('Compressed Nifti Image', '*.nii.gz'),('All files', '*.*'))
	
	# show the file selection dialog and get the selected files
	fnames = diag.show(filetypes=filetypes, initialdir = folder, multiple=1)
	
	#destroy the main window
	root.destroy()

	return fnames

def askFiles(folder):
# Deprecated function for multiple file seleccion, please intead use 'selectFiles'
	filetypes = (('Nifti Image', ['*.nii','*.nii.gz']), ('Compressed Nifti Image', '*.nii.gz'),('All files', '*.*'))
	fnames = fd.askopenfilenames(filetypes=filetypes,initialdir = folder)
	return fnames
