import json
import os.path

from src.scripts.imports import *

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

supported_file_importing = '''
SVG files (*.svg);;
PNG files (*.png);;
JPG files (*.jpg);;
JPEG files (*.jpeg);;
TIFF files (*.tiff);;
BMP files (*.bmp);;
ICO files (*.ico);;
TXT files (*.txt);;
Markdown files (*.md);;
CSV files (*.csv)
'''

supported_file_exporting = '''
SVG files (*.svg);;
PNG files (*.png);;
JPG files (*.jpg);;
JPEG files (*.jpeg);;
TIFF files (*.tiff);;
PDF files (*.pdf);;
WEBP files (*.webp);;
HEIC files (*.heic);;
ICO files (*.ico)
'''

filter_extensions = {
    'SVG files (*.svg)': '.svg',
    'PNG files (*.png)': '.png',
    'JPG files (*.jpg)': '.jpg',
    'JPEG files (*.jpeg)': '.jpeg',
    'TIFF files (*.tiff)': '.tiff',
    'PDF files (*.pdf)': '.pdf',
    'WEBP files (*.webp)': '.webp',
    'ICO files (*.ico)': '.ico',
    'HEIC files (*.heic)': '.heic'
}

export_all_file_types = {
    'SVG files (*.svg)': '.svg',
    'PNG files (*.png)': '.png',
    'JPG files (*.jpg)': '.jpg',
    'JPEG files (*.jpeg)': '.jpeg',
    'TIFF files (*.tiff)': '.tiff',
    'WEBP files (*.webp)': '.webp',
    'ICO files (*.ico)': '.ico',
    'HEIC files (*.heic)': '.heic'
}

default_text = 'Athlete:\nCompetition:\nDate:'

copyright_message = open('internal data/_copyright.txt', 'r').read()
