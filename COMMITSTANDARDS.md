# Commit Message Standards
## Iteration 1.0.0

> [!NOTE]
> This document defines the standards for commit messages in the software repository

# Chapter 1: First Sentence
### Section 1: Building the commit name and number
The first sentence should include the commit name and number in curly braces as so:

`{F#257}`

What is a commit name though? Commit names define the type of commit. Commit names include:
- `F`: A fix or bug fix.
- `N`: New features or added files.
- `T`: Removed or fine tuned things throughout the software.

### Section 2: Building the commit description
The first sentence should also include the commit description, and what's changed in parenthesis as so:

`{F#257} (Fixed error on export)`

### Section 3 (Optional): Adding any issues
As this is optional (sometimes there aren't issues) but if there are issues, define them with brackets and an 'I:' as so:

`{F#257} (Fixed error on export) [I: Export doesn't work for PDF files]`

# We will add to this constantly, but for now this defines a basic structure for commit messages.