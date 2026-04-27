# 🖱 Mouse Coordinate Tracker

A lightweight Tkinter utility for capturing and mapping mouse coordinates —
built specifically to assist with pyautogui-based Windows automation workflows.

## Features
- Live X, Y coordinate display updated 20x per second
- Press SPACE to capture and save current position
- Press C to copy latest coordinate to clipboard
- Press ENTER to clear the captured list
- On close, exports all captured points as a ready-to-paste Python dictionary

## Requirements
- Python 3.x
- pyautogui

## Installation
pip install pyautogui

## Usage
python mouse_tracker.py

## Keyboard Shortcuts
| Key   | Action                        |
|-------|-------------------------------|
| SPACE | Capture current coordinate    |
| C     | Copy last coordinate          |
| ENTER | Clear list                    |

## Output Example
When you close the window, coordinates are printed in terminal ready to paste:

ITEM_COORDS = {
    "Item 1": (72, 670),
    "Item 2": (72, 686),
    "Item 3": (72, 714),
}

## Notes
- Window stays always on top for easy use alongside other applications
- Auto-copies each captured coordinate to clipboard on capture
