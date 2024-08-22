# Introducing MPRUN, the ultimate snowboard and ski competition run planning software.

With MPRUN, you can set up custom courses matching the competition environment, and print out these setups to achieve the best competition performance and communication between coaches and athletes[^1]

> [!NOTE]
> ## Building from Source
> 1. Clone the git with `https://github.com/ktechhydle/mprun_repo.git`.
> 2. Install the project requirements with `pip install -r requirements.txt`.
> 3. Run `main.py`, and see the full app.
> 4. MPRUN is licensed under the GNU General Public Licence v3.0. [***If you are not familiar with this license, read it.***](license.txt)

## How It Works...
### 1. Set up the course:
- Use the libraries tab to add course features as needed, such as rails or jumps. You can also
import your own SVG files to add features to the scene.
- Scale, rotate, or edit items to achieve the desired course setup.
### 2. Draw your path:
- Use the `Path` tool to draw your line along the course.
- The path item colors and stroke styles can be changed for any reason you find necessary.
### 3. Label your path:
- Use the `Line and Label` tool to label tricks along your path.
### 4. And it's that simple. 
> [!IMPORTANT]
> A full tutorial of all these steps can be found on [our website](https://sites.google.com/view/mprun/home).

## Included Tools
- Select Tool:
	> Select items by dragging.
- Pan Tool:
	> Pan the scene with the left mouse button.
- Path Draw Tool:
	> Draw paths and shapes with the path tool, use different colors, pen styles and more.
- Pen Draw Tool:
	> Similar to the Path Draw Tool, but as you draw, the path smooths via a Savitzky–Golay Filter resulting in beautiful curves (less hand drawn appearance).
- Sculpt Tool:
	> Sculpt (edit) path items by clicking and dragging.
- Line and Label Tool:
	> Draw AutoCAD like leader lines and labels with editable text.
- Text Tool:
	> Place text anywhere on the scene, click and drag to position the text before placing.
- Scale Tool:
	> Interactively scale items with the mouse.
- Rotate Tool:
	> Interactively rotate items with the mouse.
- Hide Element Tool:
	> Hide selected items from the scene (they will not show on export).
- Unhide All Tool:
	> Unhide any hidden items.
- Add Canvas Tool:
	> Rearrange or add canvases to the scene by clicking and dragging.
- Insert Image Tool:
	> Insert various image types into the scene (including SVG!).

# Why MPRUN Though?
MPRUN can build a solid plan going into competitions, creating a proper mindset for athletes. This is important
because it ensures athletes don't go into competitions without a plan and a 'just wing it' mindset.

# TL;DR
> [!IMPORTANT]
> MPRUN is a comprehensive software designed for planning snowboard and ski competition runs. Users can customize 
> courses, draw their path, label tricks, and do so much more. It promotes strategic planning for athletes, preventing 
> a 'whatever' mentality and fostering a focused mindset for competitions.

# See also
[^1]: Read the acknowledgments at: https://docs.google.com/document/d/1r-HFww2g-71McWNktCsRq363_n6Pjlog89ZnsTmf3ec/edit
