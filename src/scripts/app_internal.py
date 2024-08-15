import json
import os.path

from src.scripts.imports import *

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

default_text = """Run #:
Page #:
Competition:
Athlete:
Date:"""

use_disclaimer = '''MPRUN does NOT guarantee any success in planning competitions, MPRUN is a tool that will HELP plan successful competitions/runs. 

MPRUN and MP Software are NOT responsible for any mistakes, injuries, or casualties caused during any competitions/runs. 

YOU are responsible for your own safety and ultimately your own mindset. MPRUN is a Free, Open-Source, Competition Run Planning App that ASSISTS users.

Do you accept?'''

copyright_message = '''

Copyright (C) 2023-2024 MPRUN Document
<https://github.com/ktechhydle/mprun_repo> All Rights Reserved.

MPRUN is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

MPRUN is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with MPRUN. If not, see <http://www.gnu.org/licenses/>.

!DO NOT EDIT ANY INFORMATION FOUND IN THIS DOCUMENT!

'''
