# Introducing MPRUN - the ultimate competition run planning software for on-snow athletes
## But what is that?

MPRUN's intention is to **help athletes create proper mindsets** going into competitions.

Tricks are getting harder in competitions, and nowadays _mental game is 90% part of it_. Our main goal is to help increase the performance of your mental game by using a simple technic, **Physical Visualization**.

**Physical Visualization (PZ)**, is the process of taking something we normally visualize in our brain and putting it on a physical object (like a piece of paper). MPRUN does exactly that, where you draw your competition run and print it out to a piece of paper. You can even export your run and save it to your phone.

> [!WARNING]
> PZ does not guarantee perfect results; it is a tool that can be used to ASSIST athletes (our full disclaimer can be found in the "DISCLAIMER" window shown on startup of MPRUN).

## Why does it exist?

As you may know, everything is in a constant change. That's why MPRUN was created, to help improve adapting to this constant change. 

It doesn't help everybody, but as an on-snow athlete myself, I know it can assist those that struggle in competition environments reduce stress and pressure to perform.

## How does it work? 

_You can find a demo video on <kbd>[MPRUN's website↗️](https://sites.google.com/view/mprun/home)</kbd>, but here's a simplification on how the process works._

1. Create your course
> Use a drag and drop editor to drag **Course Elements** on to the scene (**Course Elements** are just SVG items representing course features like rails, jumps, and even halfpipes)

2. Draw your line
> Use line drawing tools to draw your "path" along the course (where your going to ride, what features your going to hit)

3. Label your line
> Use labelling tools to label your tricks along your "path" (what tricks you do on each feature)

#### And that's it! You can then export your run and print it out to a piece of paper.

## How can I get involved?
There's two ways you can develop and work off of MPRUN. You can either:

### Build from source
> 1. Clone the git with `git clone https://github.com/ktechhydle/mprun_repo.git`.
> 2. Install the project requirements with `pip install -r requirements.txt`.
> 3. Run `main.py`, and see the full app.
> 4. MPRUN is licensed under the GNU General Public Licence v3.0. [***If you are not familiar with this license, read it***](license.txt).

**Or...**

### Fork the repository
> 1. Navigate to _Fork_ on this repository.
> 2. Create a new fork and copy the `master` branch only.
> 3. If you are trying to edit the source code, make sure you install the project requirements with 
`pip install -r requirements.txt`, or you can also just use GitHub's website tools to make changes.
> 4. Submit a _Pull Request (PR)_ for your edits, and we will potentially merge your code.

## Do you have an something to report (bug, issue, or feature request)?
Report it to the _Issues_ section on this repository by clicking `New`, and follow 
the instructions.

## TL;DR
MPRUN is a comprehensive software designed for planning snowboard and ski competition runs. Users can customize 
courses, draw their path, label tricks, and do so much more. It promotes strategic planning for athletes, preventing 
a 'whatever' mentality and fostering a focused mindset for competitions.

## TODO
- [x] Fix align tools creating multiple QUndoCommands
- [ ] Fix arrange tool not moving items with canvases
- [ ] Combine Export/Export All dialogs into one main dialog
- [ ] Add erase tool
 