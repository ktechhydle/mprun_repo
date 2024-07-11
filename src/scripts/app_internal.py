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

use_disclaimer = '''This app collects user data, including...

Content You Read in App:
This app stores the content you read in app (like this dialog) so that you don't get popup after popup everytime you open the app. The content you read includes this dialog, the What's New Dialog, and the Tutorial Video Dialog.

Computer Info:
This app also stores the platform you are running for cross-platform differences.

Any data you are curious about can be found in the user_data.mpdat file included with this distribution.

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

user_data = [{
    'recent_files': [os.path.abspath('examples/example_run.mp'), os.path.abspath('examples/welcome.mp')],
    'disclaimer_read': False,
    'whatsnew_read': False,
    'tutorial_watched': False,
    'platform': sys.platform
}]

if os.path.exists(os.path.abspath('internal data/user_data.mpdat')):
    pass

else:
    with open('internal data/user_data.mpdat', 'w') as f:
        json.dump(user_data, f)
