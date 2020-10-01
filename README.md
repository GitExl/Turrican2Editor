# Turrican II Editor

## Description
This is a level editor for the CDTV version of Turrican II. It supports editing of the tilemaps of all levels, as well as their entities and starting locations.

## Limitations
Because Turrican II's levels are a mix of data and code, not everything is editable or as flexible as might be desirable.

* Level exit locations cannot currently be modified.
* The lift platforms in L5-2 are stored separately from entities and cannot currently be modified.
* The amount of room for new entities is limited.
* Some effects like player waterfall splashes in L1-1 are hardcoded.
* Boss encounter locations are hardcoded. The boss entities merely trigger a boss fight, and will move the camera to the hardcoded coordinates.
* Event locations like the L1-1 wind and the L2-2 wind tunnel are hardcoded.

## Game files
You will need Turrican II CDTV files to use the editor with. These can be copied directly from the root directory of any Turrican II CDTV disc or disc image. If you want to use the same directory for playtesting, copy the C, DEVS and S directories as well. Upon startup of the Turrican II Editor, select Open from the Game menu and choose the directory where the game files are located.

## Usage
The currently active level can be selected in the top left. Moving around a level can be done by holding down the right mouse button on the level viewport and dragging the level. 32 levels of undo are available for each level by using the Undo option in the Edit menu or by using Ctrl+Z. There are three editing modes:

### Tiles
The tiles mode (F1) is used to modify a level's tiles. You can select one or more tiles to draw with from the tile selector on the left. Clicking and dragging allows you to select a block of tiles to draw with. Use the left mouse button in the level viewport to draw with the current tile selection. You can also create a tile selection from the level viewport by holding down Shift and clicking and dragging over the tiles for the new selection. You can fill an area with the current tile selection by holding down Ctrl and selecting the area to fill.

To toggle the precise collision areas of tiles, use the Show collision option in the Level menu, or use the C key.

### Entities
The entities mode (F2) is used to edit the location of entities and add or remove entities from a level. You can select an entity to place from the entity selector on the left. By holding down Ctrl and clicking in the level viewport a new entity can be placed. Entities can be moved and\or selected by clicking and dragging their transparent white handle. Multiple entities can be selected by clicking and dragging a selection box around them (without holding down any keys). The currently selected entity or entities can be removed by pressing the Delete key.

Note that there is a hard limit to the number of entities that can be placed in a level. The amount of room left is displayed in the bottom left of the editor window. Normally, each entity will take up 3 bytes of space, but in some situations this can be up to 10 bytes. The editor will warn you if there is not enough room left for new entities, and will not save your level if too many entities are present in it.

### Start
Editing a level's starting location (F3) is done by dragging the camera rectangle around the level viewport. The player rectangle can be dragged around as well, but is limited to the camera rectangle.

## Playtesting
If you want to play your modified level, you can do so using WinUAE if the C, DEVS and S directories are present in the game data directory.

* Open the S/STARTUP-SEQUENCE file and remove or comment out the first two lines (rmtm and cdtvprefs).
* Create a new WinUAE quickstart configuration: A500, 1.3 ROM, ECS Agnus, 1 Mb Chip RAM.
* Add the game data directory as a harddrive under the CD & Harddrives section. The device name should be "hd0" and have the label "TURRICAN_II". It must be set as bootable.
* Configure any other settings as you see fit.

## Building
The Turrican II Editor was written in Python 3 and C. Together with wxWidgets, Python is used for the UI and game data reading\writing. The "renderlib" C component is used for 2D rendering and bitstream reading\writing.

To run the editor you will need a 32 bit version of Python 3.8 or higher, and wxPython 4.1 or higher. Execute src/main.py from the program's root directory to start.

To build the "renderlib" component you will need GCC and Win32 header files, as well as libpng. A basic MinGW installation will provide most of these. Running the makefile should be sufficient to build a renderlib.dll file in the program's root directory.
