![MPRUN_logo_rounded_corners_version copy](https://github.com/ktechhydle/mprun_repo/assets/151480646/ebc27d9a-651a-430e-bfe4-d345d6bef3fe)
# Introducing MPRUN, the ultimate snowboard and ski competion run planning software.

With MPRUN, you can set up custom courses matching the competition environment, and print out these setups to achieve the best competition performance and communication between coaches and athletes[^1]

> [!NOTE]
> # Install
> 1. Clone the git with `https://github.com/ktechhydle/mprun_repo.git`.
> 2. Install the project requirements with `pip install -r IMPORTANT/requirements.txt`.
> 3. Run `launcher.py`, and see the full app.
> 4. MPRUN is licensed under the GNU General Public Licence v3.0. [***If you are not familiar with this license, read it.***](license.txt)

# How It Works...
### 1. Set up the course:
- Use the libraries tab to add Course Elements as needed, or import your own SVG files to add features to the Canvas.
- Scale, Rotate, or Group Elements to achieve the desired course setup.
### 2. Draw your path:
- Use the `Path` tool to draw your line along the course.
- The Path colors and stroke styles can be changed for any reason you find necessary.
### 3. Label your path:
- Use the `Line and Label` tool to create Leader lines along your Path.
- Edit these labels to include your tricks along each part of the Path.
### 4. And it's that simple. 
> [!IMPORTANT]
> MPRUN can be a simple software, and a powerful software when necessary.

# Full Toolset
- Select Tool:
	> Select elements by dragging, or clicking on multiple elements with Control + Left Button.
- Pan Tool:
	> Pan the canvas with the left mouse button with the tool active.
- Path Draw Tool:
	> Draw paths and shapes with the path tool, use different colors, pen styles and more.
- Pen Draw Tool:
	> Similar to the Path Draw Tool, but as you draw, the path smooths via a Savitzky–Golay Filter resulting in beautiful curves (less hand drawn appearance).
- Line and Label Tool:
	> Draw AutoCAD like leader lines and labels with editable text.
- Text Tool:
	> Place text anywhere on the canvas, click and drag to position the text before placing.
- Scale Tool:
	> Interactively scale elements with the mouse by clicking and dragging on the element.
- Hide Element Tool:
	> Hide selected elements from the canvas (they will not show on export).
- Unhide All Tool:
	> Unhide any previously hidden elements.
- Add Canvas Tool:
	> Rearrange or add canvases to the scene by clicking and dragging with the Shift key active, optionally go to the `Canvas` panel to edit sizes and names for selected canvases.
- Insert Image Tool:
	> Insert various image types into the scene (including SVG!).

# Additional tools (found in the `Tools` and `Edit` menu)
- Smooth Path Tool:
	> Smooth selected path elements (if not already smoothed) with the Savitzky–Golay Filter.
- Close Path Tool:
	> Close selected path elements into solid shapes.
- Add Text Along Path Tool:
	> Brings up the `Text Along Path` panel, and allows you to type text along selected path elements (the text font and color is also customizable with the `Characters` panel).
- Name Tool:
	> Name selected elements to whatever name you want (canvas items are not nameable with this tool).
- Duplicate Tool:
	> Duplicate selected elements (canvas items do not have the ability to duplicate).
- Group Selected Tool:
	> Group selected elements.
- Ungroup Selected Tool:
	> Ungroup selected element groups.
- Trace Image Tool:
	> Trace imported Bitmap images into SVG format (this tool is customizable with the `Image Trace` panel).

# Additional Features
- Vector Graphics:
	> MPRUN uses a Vector Graphics Engine, and recently added OpenGL functions to make rendering significantly faster.
- Layer management:
	> Elements can be raised and lowered or set to a specific layer height via the `Layers` panel.
- Elements are named:
	> You will often see elements named `Path` or `Group` on the Canvas. ***Hover your mouse over an element to see the element name, or name the element via the `Name` tool.***
- Insert different files:
	> Insert PNG, JPEG, SVG, or even TIFF files onto the canvas.
- Export multiple file types:
	> Export the canvas as a PNG, JPEG, SVG, or even a PDF file ***(beta)***.
- Pen and fill customization:
	> Customize pen styles, caps, and more, also included is the ability to change fill colors in the `Appearance` panel.
- Font editing:
	> Edit font families, colors, and more in the `Characters` panel.
> [!TIP]
> - Snap-to-grid functionality:
> 	> Enable `GSNAP` in the action toolbar to enable grid-snapping for grouped items.

# Why MPRUN Though?
MPRUN can build a solid plan going into competitions, creating a proper mindset for athletes.
#### Why is that important though? 
This is important because it ensures athletes don't go into competitions without a plan and a 'just wing it' mindset.

# TL;DR
> [!IMPORTANT]
> MPRUN is a comprehensive software designed for planning snowboard and ski competition runs. Users can customize courses, draw their path, label tricks, and do so much more. It promotes strategic planning for athletes, preventing a 'just wing it' mentality and fostering a focused mindset for competitions.

# Screenshots
Home screen UI
![mprun_homescreen_screenshot.png](Examples%2Fmprun_homescreen_screenshot.png)

Workspace UI
![Screenshot 2024-05-21 191939](https://github.com/ktechhydle/mprun_repo/assets/151480646/e6ccd3b5-f269-48a0-bf3f-7b88b065d2e1)

Halfipe run example
![mprun_halfpipe_run_example](https://github.com/ktechhydle/mprun_repo/assets/151480646/ce52950f-e929-4f02-a482-2adcc3d061be)

Cool line design using MPRUN
![mprun_graphicsdesign_example](https://github.com/ktechhydle/mprun_repo/assets/151480646/35f5a602-3bc8-4837-930d-9c6a38c78107)

# See also
[^1]: Read the acknowledgments at: https://docs.google.com/document/d/1r-HFww2g-71McWNktCsRq363_n6Pjlog89ZnsTmf3ec/edit
