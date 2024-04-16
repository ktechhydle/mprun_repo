# Introducing MPRUN, the ultimate snowboard and ski competion run planning software.

With MPRUN, you can set up custom courses matching the competition environment, and print out these setups to achieve the best competition performance and communication between coaches and athletes[^1]

> [!NOTE]
> # Install
> 1. Clone the git with `https://github.com/ktechhydle/mprun_repo.git`.
> 2. Install the project requirements with `pip install -r requirements.txt`.
> 3. Run `launcher.py`, and see the full app.
> 4. MPRUN is licensed under the GNU General Public Licence v3.0. [***If you are not familiar with this license, read it.***](license.txt)

# How It Works...
### 1. Set up the course:
- Use the `Course Elements Picker`, or import your own SVG files to add features to the Canvas.
- Scale, Rotate, or Group Elements to achieve the desired course setup.
- Lock Element positions to prevent further editing.
### 2. Draw your path:
- Use the `Path` tool to draw your line along the course.
- The Path colors and stroke styles can be changed for any reason you find necessary.
- Lock the Path position to prevent further editing.
### 3. Label your path:
- Use the `Line and Label` tool to create Leader lines along your Path.
- Edit these labels to include your tricks along each part of the Path.
- Lock Element positions to prevent further editing.
### 4. And it's that simple. 
> [!IMPORTANT]
> MPRUN can be a simple software, and a powerful software when necessary.

# Additional Features
- Vector Graphics:
	> MPRUN uses a Vector Graphics Engine (`QGraphicsScene`), making the use of SVG or any Vector format a better choice for import.
- Panning and zooming:
	> Pan and zoom on the Canvas.
- Layer management:
	> Elements can be layered depending on the type of element (Text, Path, Course element)
- Element management:
	> Elements are managed according to their current state (Locked, Grouped, etc.)
- Elements are named:
	> You will often see elements named `Editable Text Block` or `Free MPRUN Element` on the Canvas. ***Hover your mouse over an element to see the element name.***
- Insert different files:
	> Insert PNG, JPEG, SVG, or even TIFF files onto the canvas.
- Export multiple file types:
	> Export the canvas as a PNG, JPEG, SVG, or even a PDF file ***(beta)***.
- Add text blocks:
	> Add `Editable Text Block`'s on to the Canvas.
- Vector conversion:
  	> Use the `Vectorize` tool ***(beta)*** to convert raster imagery to Vector tiles.
- Element position managment:
  	> Lock or unlock element positions, or even use the `Permanent Lock Tool` to lock Elements permanently.
> [!TIP]
> - Snap-to-grid functionality:
> 	> Enable `GSNAP` in the action toolbar to enable grid-snapping for grouped items.

# Why MPRUN Though?
MPRUN can build a solid plan going into competitions, creating a proper mindset for athletes.
#### Why is that important though? 
This is important because it ensures athletes don't go into competitions without a plan and a 'just wing it' mindset.

# TL;DR
> [!IMPORTANT]
> MPRUN is a comprehensive software designed for planning snowboard and ski competition runs. Users can customize courses, draw their path, label tricks, and lock elements for optimal performance. It promotes strategic planning for athletes, preventing a 'just wing it' mentality and fostering a focused mindset for competitions.

# For More Info,
[^1]: Read the acknowledgments at: https://docs.google.com/document/d/1r-HFww2g-71McWNktCsRq363_n6Pjlog89ZnsTmf3ec/edit
