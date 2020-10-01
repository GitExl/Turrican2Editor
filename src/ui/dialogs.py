# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import ui.tileselector
import ui.entitypicker

EDIT_TILES = 1000
EDIT_ENTITIES = 1001
EDIT_START = 1002

###########################################################################
## Class FrameMainBase
###########################################################################

class FrameMainBase ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Turrican 2 Editor", pos = wx.DefaultPosition, size = wx.Size( 1024,728 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.Size( 1024,728 ), wx.DefaultSize )

		SizerMain = wx.BoxSizer( wx.HORIZONTAL )

		self.Properties = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 357,-1 ), wx.TAB_TRAVERSAL|wx.BORDER_NONE )
		self.Properties.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

		SizerProperties = wx.BoxSizer( wx.VERTICAL )

		LevelSelectChoices = []
		self.LevelSelect = wx.Choice( self.Properties, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, LevelSelectChoices, 0 )
		self.LevelSelect.SetSelection( 0 )
		SizerProperties.Add( self.LevelSelect, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 8 )


		SizerProperties.Add( ( 0, 8), 0, wx.EXPAND, 0 )

		self.PanelModeTiles = wx.Panel( self.Properties, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TAB_TRAVERSAL )
		TilesSizer = wx.BoxSizer( wx.VERTICAL )

		self.PanelTitleTiles = wx.Panel( self.PanelModeTiles, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.PanelTitleTiles.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT ) )

		SizerTitleTiles = wx.BoxSizer( wx.VERTICAL )

		self.TitleTiles = wx.StaticText( self.PanelTitleTiles, wx.ID_ANY, u"Tiles", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.TitleTiles.Wrap( -1 )

		self.TitleTiles.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.TitleTiles.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHTTEXT ) )

		SizerTitleTiles.Add( self.TitleTiles, 0, wx.ALL, 4 )


		self.PanelTitleTiles.SetSizer( SizerTitleTiles )
		self.PanelTitleTiles.Layout()
		SizerTitleTiles.Fit( self.PanelTitleTiles )
		TilesSizer.Add( self.PanelTitleTiles, 0, wx.ALL|wx.EXPAND, 8 )

		self.Tiles = ui.tileselector.TileSelector(self.PanelModeTiles)
		self.Tiles.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )

		TilesSizer.Add( self.Tiles, 1, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 8 )


		self.PanelModeTiles.SetSizer( TilesSizer )
		self.PanelModeTiles.Layout()
		TilesSizer.Fit( self.PanelModeTiles )
		SizerProperties.Add( self.PanelModeTiles, 1, wx.EXPAND, 0 )

		self.PanelModeEntities = wx.Panel( self.Properties, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		EntitiesSizer = wx.BoxSizer( wx.VERTICAL )

		self.PanelTitleEntities = wx.Panel( self.PanelModeEntities, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.PanelTitleEntities.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT ) )

		SizerTitleEntities = wx.BoxSizer( wx.VERTICAL )

		self.TitleEntities = wx.StaticText( self.PanelTitleEntities, wx.ID_ANY, u"Entities", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.TitleEntities.Wrap( -1 )

		self.TitleEntities.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.TitleEntities.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHTTEXT ) )

		SizerTitleEntities.Add( self.TitleEntities, 0, wx.ALL, 4 )


		self.PanelTitleEntities.SetSizer( SizerTitleEntities )
		self.PanelTitleEntities.Layout()
		SizerTitleEntities.Fit( self.PanelTitleEntities )
		EntitiesSizer.Add( self.PanelTitleEntities, 0, wx.ALL|wx.EXPAND, 8 )

		self.Entities = ui.entitypicker.EntityPicker(self.PanelModeEntities)
		self.Entities.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )

		EntitiesSizer.Add( self.Entities, 1, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 8 )


		self.PanelModeEntities.SetSizer( EntitiesSizer )
		self.PanelModeEntities.Layout()
		EntitiesSizer.Fit( self.PanelModeEntities )
		SizerProperties.Add( self.PanelModeEntities, 1, wx.EXPAND, 0 )

		self.PanelModeStart = wx.Panel( self.Properties, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		SizerStart = wx.BoxSizer( wx.VERTICAL )

		self.PanelTitleStart = wx.Panel( self.PanelModeStart, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.PanelTitleStart.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT ) )

		SizerTitleStart = wx.BoxSizer( wx.VERTICAL )

		self.TitleStart = wx.StaticText( self.PanelTitleStart, wx.ID_ANY, u"Start", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.TitleStart.Wrap( -1 )

		self.TitleStart.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.TitleStart.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHTTEXT ) )

		SizerTitleStart.Add( self.TitleStart, 0, wx.ALL, 4 )


		self.PanelTitleStart.SetSizer( SizerTitleStart )
		self.PanelTitleStart.Layout()
		SizerTitleStart.Fit( self.PanelTitleStart )
		SizerStart.Add( self.PanelTitleStart, 0, wx.EXPAND |wx.ALL, 8 )

		self.StartGoTo = wx.Button( self.PanelModeStart, wx.ID_ANY, u"Go to start", wx.DefaultPosition, wx.DefaultSize, 0 )
		SizerStart.Add( self.StartGoTo, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 8 )


		self.PanelModeStart.SetSizer( SizerStart )
		self.PanelModeStart.Layout()
		SizerStart.Fit( self.PanelModeStart )
		SizerProperties.Add( self.PanelModeStart, 1, wx.EXPAND, 0 )


		self.Properties.SetSizer( SizerProperties )
		self.Properties.Layout()
		SizerMain.Add( self.Properties, 0, wx.EXPAND, 0 )

		self.Viewport = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE )
		self.Viewport.SetBackgroundColour( wx.Colour( 0, 0, 0 ) )

		SizerMain.Add( self.Viewport, 1, wx.EXPAND, 0 )


		self.SetSizer( SizerMain )
		self.Layout()
		self.Status = self.CreateStatusBar( 1, wx.STB_SIZEGRIP|wx.BORDER_NONE, wx.ID_ANY )
		self.Menu = wx.MenuBar( 0|wx.BORDER_NONE )
		self.MenuGame = wx.Menu()
		self.GameOpen = wx.MenuItem( self.MenuGame, wx.ID_ANY, u"Open..."+ u"\t" + u"CTRL+O", wx.EmptyString, wx.ITEM_NORMAL )
		self.MenuGame.Append( self.GameOpen )

		self.GameSave = wx.MenuItem( self.MenuGame, wx.ID_ANY, u"Save"+ u"\t" + u"CTRL+S", wx.EmptyString, wx.ITEM_NORMAL )
		self.MenuGame.Append( self.GameSave )

		self.MenuGame.AppendSeparator()

		self.GameExit = wx.MenuItem( self.MenuGame, wx.ID_ANY, u"Exit"+ u"\t" + u"CTRL+Q", wx.EmptyString, wx.ITEM_NORMAL )
		self.MenuGame.Append( self.GameExit )

		self.Menu.Append( self.MenuGame, u"Game" )

		self.MenuLevel = wx.Menu()
		self.LevelShowEntities = wx.MenuItem( self.MenuLevel, wx.ID_ANY, u"Always show entities"+ u"\t" + u"E", wx.EmptyString, wx.ITEM_CHECK )
		self.MenuLevel.Append( self.LevelShowEntities )

		self.LevelShowCollision = wx.MenuItem( self.MenuLevel, wx.ID_ANY, u"Show collision"+ u"\t" + u"C", wx.EmptyString, wx.ITEM_CHECK )
		self.MenuLevel.Append( self.LevelShowCollision )

		self.LevelShowBlockmap = wx.MenuItem( self.MenuLevel, wx.ID_ANY, u"Show blockmap"+ u"\t" + u"B", wx.EmptyString, wx.ITEM_CHECK )
		self.MenuLevel.Append( self.LevelShowBlockmap )

		self.Menu.Append( self.MenuLevel, u"Level" )

		self.MenuEdit = wx.Menu()
		self.EditUndo = wx.MenuItem( self.MenuEdit, wx.ID_ANY, u"Undo"+ u"\t" + u"CTRL+Z", wx.EmptyString, wx.ITEM_NORMAL )
		self.MenuEdit.Append( self.EditUndo )

		self.MenuEdit.AppendSeparator()

		self.EditTiles = wx.MenuItem( self.MenuEdit, EDIT_TILES, u"Edit tiles"+ u"\t" + u"F1", wx.EmptyString, wx.ITEM_NORMAL )
		self.MenuEdit.Append( self.EditTiles )

		self.EditEntities = wx.MenuItem( self.MenuEdit, EDIT_ENTITIES, u"Edit entities"+ u"\t" + u"F2", wx.EmptyString, wx.ITEM_NORMAL )
		self.MenuEdit.Append( self.EditEntities )

		self.EditStart = wx.MenuItem( self.MenuEdit, EDIT_START, u"Edit start"+ u"\t" + u"F3", wx.EmptyString, wx.ITEM_NORMAL )
		self.MenuEdit.Append( self.EditStart )

		self.Menu.Append( self.MenuEdit, u"Edit" )

		self.MenuHelp = wx.Menu()
		self.HelpAbout = wx.MenuItem( self.MenuHelp, wx.ID_ANY, u"About...", wx.EmptyString, wx.ITEM_NORMAL )
		self.MenuHelp.Append( self.HelpAbout )

		self.Menu.Append( self.MenuHelp, u"Help" )

		self.SetMenuBar( self.Menu )


		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.close )
		self.LevelSelect.Bind( wx.EVT_CHOICE, self.level_choice )
		self.StartGoTo.Bind( wx.EVT_BUTTON, self.goto_start )
		self.Viewport.Bind( wx.EVT_LEAVE_WINDOW, self.viewport_mouse_leave )
		self.Viewport.Bind( wx.EVT_LEFT_DOWN, self.viewport_mouse_left_down )
		self.Viewport.Bind( wx.EVT_LEFT_UP, self.viewport_mouse_left_up )
		self.Viewport.Bind( wx.EVT_MOTION, self.viewport_mouse_move )
		self.Viewport.Bind( wx.EVT_MOUSEWHEEL, self.viewport_mouse_wheel )
		self.Viewport.Bind( wx.EVT_PAINT, self.viewport_paint )
		self.Viewport.Bind( wx.EVT_RIGHT_DOWN, self.viewport_mouse_right_down )
		self.Viewport.Bind( wx.EVT_RIGHT_UP, self.viewport_mouse_right_up )
		self.Viewport.Bind( wx.EVT_SIZE, self.viewport_resize )
		self.Bind( wx.EVT_MENU, self.open, id = self.GameOpen.GetId() )
		self.Bind( wx.EVT_MENU, self.save, id = self.GameSave.GetId() )
		self.Bind( wx.EVT_MENU, self.close_menu, id = self.GameExit.GetId() )
		self.Bind( wx.EVT_MENU, self.set_show_entities_menu, id = self.LevelShowEntities.GetId() )
		self.Bind( wx.EVT_MENU, self.set_show_collision_menu, id = self.LevelShowCollision.GetId() )
		self.Bind( wx.EVT_MENU, self.set_show_blockmap_menu, id = self.LevelShowBlockmap.GetId() )
		self.Bind( wx.EVT_MENU, self.undo, id = self.EditUndo.GetId() )
		self.Bind( wx.EVT_MENU, self.set_mode_from_menu, id = self.EditTiles.GetId() )
		self.Bind( wx.EVT_MENU, self.set_mode_from_menu, id = self.EditEntities.GetId() )
		self.Bind( wx.EVT_MENU, self.set_mode_from_menu, id = self.EditStart.GetId() )
		self.Bind( wx.EVT_MENU, self.about, id = self.HelpAbout.GetId() )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def close( self, event ):
		event.Skip()

	def level_choice( self, event ):
		event.Skip()

	def goto_start( self, event ):
		event.Skip()

	def viewport_mouse_leave( self, event ):
		event.Skip()

	def viewport_mouse_left_down( self, event ):
		event.Skip()

	def viewport_mouse_left_up( self, event ):
		event.Skip()

	def viewport_mouse_move( self, event ):
		event.Skip()

	def viewport_mouse_wheel( self, event ):
		event.Skip()

	def viewport_paint( self, event ):
		event.Skip()

	def viewport_mouse_right_down( self, event ):
		event.Skip()

	def viewport_mouse_right_up( self, event ):
		event.Skip()

	def viewport_resize( self, event ):
		event.Skip()

	def open( self, event ):
		event.Skip()

	def save( self, event ):
		event.Skip()

	def close_menu( self, event ):
		event.Skip()

	def set_show_entities_menu( self, event ):
		event.Skip()

	def set_show_collision_menu( self, event ):
		event.Skip()

	def set_show_blockmap_menu( self, event ):
		event.Skip()

	def undo( self, event ):
		event.Skip()

	def set_mode_from_menu( self, event ):
		event.Skip()



	def about( self, event ):
		event.Skip()


###########################################################################
## Class DialogAboutBase
###########################################################################

class DialogAboutBase ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"About", pos = wx.DefaultPosition, size = wx.Size( 800,512 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		Sizer = wx.BoxSizer( wx.VERTICAL )

		self.Panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		SizerC1 = wx.BoxSizer( wx.VERTICAL )

		SizerText = wx.BoxSizer( wx.VERTICAL )

		self.AppName = wx.StaticText( self.Panel, wx.ID_ANY, u"Turrican 2 Editor", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.AppName.Wrap( -1 )

		self.AppName.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

		SizerText.Add( self.AppName, 0, wx.LEFT|wx.RIGHT|wx.TOP, 8 )

		self.AppVersion = wx.StaticText( self.Panel, wx.ID_ANY, u"Version 1.0.2", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.AppVersion.Wrap( -1 )

		SizerText.Add( self.AppVersion, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 8 )

		self.License = wx.TextCtrl( self.Panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_DONTWRAP|wx.TE_MULTILINE|wx.TE_READONLY|wx.BORDER_NONE )
		self.License.SetFont( wx.Font( 9, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Courier New" ) )
		self.License.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

		SizerText.Add( self.License, 1, wx.ALL|wx.EXPAND, 8 )


		SizerC1.Add( SizerText, 1, wx.EXPAND, 5 )

		SizerButton = wx.BoxSizer( wx.HORIZONTAL )


		SizerButton.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.Ok = wx.Button( self.Panel, wx.ID_ANY, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )

		self.Ok.SetDefault()
		SizerButton.Add( self.Ok, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )


		SizerC1.Add( SizerButton, 0, wx.EXPAND, 5 )


		self.Panel.SetSizer( SizerC1 )
		self.Panel.Layout()
		SizerC1.Fit( self.Panel )
		Sizer.Add( self.Panel, 1, wx.EXPAND |wx.ALL, 8 )


		self.SetSizer( Sizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Ok.Bind( wx.EVT_BUTTON, self.ok )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def ok( self, event ):
		event.Skip()


