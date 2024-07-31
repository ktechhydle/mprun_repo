# Commit Message Standards
## Iteration 1.0.3

> [!NOTE]
> This document defines the standards for commit messages in the software repository

# Chapter 1: First Sentence
### Section 1: Building the commit name and number
The first sentence should include the commit number as so:

`#257`

### Section 2: Building the commit description
The first sentence should also include the commit description, and what's changed as so:

`#257 fixed error on export`

### Section 3 (Optional): Adding any issues
As this is optional (sometimes there aren't issues) but if there are issues, define them with an 'ISSUE:' as so:

`#257 fixed error on export ISSUE: export doesn't work for PDF files`

### Section 4: Describing Changes
Define changes with a list using '-' and all lowercase as so:

```
#257 fixed error on export ISSUE: export doesn't work for PDF files

-export issues now support error dialogs
-error dialogs include options for helping the user combat any errors
```

# Final format (copy and paste)

```
#CommitNumber Commit Description ISSUE: Commit Issue

-commit changes

```

# We will add to this constantly, but for now this defines a basic structure for commit messages.