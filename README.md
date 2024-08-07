# Introducing MPRUN, the ultimate snowboard and ski competition run planning software.

With MPRUN, you can set up custom courses matching the competition environment, and print out these setups to achieve the best competition performance and communication between coaches and athletes[^1]

> [!NOTE]
> # Building from Source
> 1. Clone the git with `https://github.com/ktechhydle/mprun_repo.git`.
> 2. Install the project requirements with `pip install -r requirements.txt`.
> 3. Run `main.py`, and see the full app.
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
	> Select elements by dragging.
- Pan Tool:
	> Pan the scene with the left mouse button with the tool active.
- Path Draw Tool:
	> Draw paths and shapes with the path tool, use different colors, pen styles and more.
- Pen Draw Tool:
	> Similar to the Path Draw Tool, but as you draw, the path smooths via a Savitzky–Golay Filter resulting in beautiful curves (less hand drawn appearance).
- Line and Label Tool:
	> Draw AutoCAD like leader lines and labels with editable text.
- Text Tool:
	> Place text anywhere on the scene, click and drag to position the text before placing.
- Scale Tool:
	> Interactively scale elements with the mouse by clicking and dragging on the element.
- Hide Element Tool:
	> Hide selected elements from the scene (they will not show on export).
- Unhide All Tool:
	> Unhide any previously hidden elements.
- Add Canvas Tool:
	> Rearrange or add canvases to the scene by clicking and dragging with the Shift key active, optionally go to the `Canvas` panel to edit sizes and names for selected canvases.
- Insert Image Tool:
	> Insert various image types into the scene (including SVG!).

# Additional tools (found in the menu bar)
- Smooth Path Tool:
	> Smooth selected path elements (if not already smoothed) with the Savitzky–Golay Filter.
- Close Path Tool:
	> Close selected path elements into solid shapes.
- Name Tool:
	> Name selected elements to whatever name you want (canvas items are not nameable with this tool).
- Duplicate Tool:
	> Duplicate selected elements (canvas items do not have the ability to duplicate).
- Trace Image Tool:
	> Trace imported Bitmap images into SVG format (this tool is customizable with the `Image Trace` panel).
- Save:
	> Save documents in an `.mp` format.
- Save As:
	> Save documents with a new name in an `.mp` format.
- Open:
    > Open `.mp` documents for further editing.
- And more...

# Primary Functionality
- Vector Graphics:
	> MPRUN uses a Vector Graphics Engine, and OpenGL functions to make rendering significantly faster using your GPU (if you have it).
- Layer management:
	> Elements can be raised and lowered.
- Elements are named:
	> You will often see elements tagged `Path` or `Text` on the scene. ***Hover your mouse over an element to see the element name.***
- Insert different files:
	> Insert PNG, JPEG, SVG, or even TIFF files onto the scene.
- Export multiple file types:
	> Export the selected canvas as a PNG, JPEG, SVG, or even a PDF file ***(beta)***.
- Pen and fill customization:
	> Customize pen styles, caps, and more, also included is the ability to change fill colors.
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

# See also
[^1]: Read the acknowledgments at: https://docs.google.com/document/d/1r-HFww2g-71McWNktCsRq363_n6Pjlog89ZnsTmf3ec/edit
