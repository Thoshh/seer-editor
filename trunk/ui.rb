@ui_info = %Q[
<ui>
  <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menuitem action='New'/>
      <menuitem action='Open'/>
      <separator/>
      <menuitem action='Close'/>
      <separator/>
      <menuitem action='Save'/>
      <menuitem action='Save As'/>
      <separator/>
      <menuitem action='Quit'/>
    </menu>
    <menu action='EditMenu'>
      <menuitem action='Undo'/>
      <menuitem action='Redo'/>
      <separator/>
      <menuitem action='Cut'/>
      <menuitem action='Copy'/>
      <menuitem action='Paste'/>
    </menu>
    <menu action='ViewMenu'>
    </menu>
    <menu action='ProgramMenu'>
      <menuitem action='Compile'/>
      <menuitem action='Run'/>
    </menu>
    <menu action='HelpMenu'>
      <menuitem action='About'/>
    </menu>
  </menubar>
  <toolbar  name='ToolBar'>
    <toolitem action='New'/>
    <toolitem action='Open'/>
    <separator action='Sep1'/>
    <toolitem action='Save'/>
    <toolitem action='Save As'/>
    <separator action='Sep2'/>
    <toolitem action='Undo'/>
    <toolitem action='Redo'/>
    <separator action='Sep3'/>
    <toolitem action='Quit'/>
    <separator action='Sep4'/>
  </toolbar>
</ui>]

require 'gtk2'
require 'sEdit'

def read_file
  File.open(@filename){|f| ret = f.readlines.join }
end

callback = Proc.new {|actiongroup, action| 
  puts "`#{action.name}' is clicked. "
  if action.is_a? Gtk::ToggleAction
    puts "active? = #{action.active?}"
  end
}

callback_new = Proc.new {
  if @buffer.modified?
    dialog = Gtk::FileChooserDialog.new("Open File", @window,
                           Gtk::FileChooser::ACTION_OPEN, nil,
                           [Gtk::Stock::CANCEL, Gtk::Dialog::RESPONSE_CANCEL],
                           [Gtk::Stock::OPEN, Gtk::Dialog::RESPONSE_ACCEPT])
    dialog.hide
    if dialog.run == Gtk::Dialog::RESPONSE_ACCEPT
      @filename = dialog.filename
      @window.set_title(TITLE + ":" + @filename)
      dialog.destroy
      #dialog.hide
    else
      dialog.hide
    end
    
    if @filename
      text = read_file
      @buffer.set_text(text)
    end
    @buffer.place_cursor(@buffer.start_iter)
    @sourceview.has_focus = true
  end
  @filename = nil
  on_clear()
}

callback_open = Proc.new {
  p "Open is Called"
    dialog = Gtk::FileChooserDialog.new("Open File", @window,
                           Gtk::FileChooser::ACTION_OPEN, nil,
                           [Gtk::Stock::CANCEL, Gtk::Dialog::RESPONSE_CANCEL],
                           [Gtk::Stock::OPEN, Gtk::Dialog::RESPONSE_ACCEPT])
    dialog.hide
    if dialog.run == Gtk::Dialog::RESPONSE_ACCEPT
      @filename = dialog.filename
      @window.set_title(TITLE + ":" + @filename)
      dialog.destroy
      #dialog.hide
    else
      dialog.hide
    end
    
    if @filename
      text = read_file
      @buffer.set_text(text)
    end
  @buffer.place_cursor(@buffer.start_iter)
  @sourceview.has_focus = true
}

callback_save = Proc.new {
  if @filename
    File.open(@filename, "w"){|f| 
      f.write(@buffer.get_text(*@buffer.bounds)) 
    }
    @buffer.modified = false
  else
    dialog = Gtk::FileChooserDialog.new("Open File", @window,
                           Gtk::FileChooser::ACTION_OPEN, nil,
                           [Gtk::Stock::CANCEL, Gtk::Dialog::RESPONSE_CANCEL],
                           [Gtk::Stock::OPEN, Gtk::Dialog::RESPONSE_ACCEPT])
    dialog.hide
    if dialog.run == Gtk::Dialog::RESPONSE_ACCEPT
      @filename = dialog.filename
      @window.set_title(TITLE + ":" + @filename)
      dialog.destroy
      #dialog.hide
    else
      dialog.hide
    end
    
    if @filename
      text = read_file
      @buffer.set_text(text)
    end
    
    @buffer.place_cursor(@buffer.start_iter)
    @sourceview.has_focus = true
    
    if @filename
      File.open(@filename, "w"){|f| 
        f.write(@buffer.get_text(*@buffer.bounds)) 
      }
      @buffer.modified = false
    end
  end
}

callback_quit = Proc.new {
  p "Quit is called."
  Gtk.main_quit
}

@actions = [
  ["FileMenu", nil, "_File"],
  ["EditMenu", nil, "_Edit"],
  ["ViewMenu", nil, "_View"],
  ["ProgramMenu", nil, "_Program"],
  ["HelpMenu", nil, "_Help"],
  ["New", Gtk::Stock::NEW, "_New", "<control>N", "Create a new file", callback_new],
  ["Open", Gtk::Stock::OPEN, "_Open", "<control>O", "Open a file", callback_open],
  ["Close", Gtk::Stock::CLOSE, "_Close", "<control>W", "Close a file", callback],
  ["Save", Gtk::Stock::SAVE, "_Save", "<control>S", "Save current file", callback_save],
  ["Save As", Gtk::Stock::SAVE_AS, "Save _As...", nil, "Save to a file", callback],
  ["Quit", Gtk::Stock::QUIT, "_Quit", "<control>Q", "Quit", callback_quit],
  ["Undo", Gtk::Stock::UNDO , "_Undo", nil, "Undo", callback],
  ["Redo", Gtk::Stock::REDO, "_Redo", nil, "Redo", callback],
  ["Cut", Gtk::Stock::CUT, "_Cut", "<control>X", "Cut", callback],
  ["Copy", Gtk::Stock::COPY, "_Copy", "<control>C", "Copy", callback],
  ["Paste", Gtk::Stock::PASTE, "_Paste", "<control>V", "Paste", callback],
  ["Compile", Gtk::Stock::PASTE, "_Compile", "<control>B", "Compile", callback],
  ["Run", Gtk::Stock::PASTE, "_Run", nil, "Run", callback],
  ["About", nil, "_About", "<control>A", "About", callback]
]


