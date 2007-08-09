require 'gtk2'
require 'ui'
require 'sEdit'
require 'sFile'

callback = Proc.new {|actiongroup, action| 
  puts "`#{action.name}' is clicked. "
  print 'callback unimplemented'
  if action.is_a? Gtk::ToggleAction
    puts "active? = #{action.active?}"
  end
}

callback_quit = Proc.new {
  Gtk.main_quit
}

@actions = [
  ["FileMenu", nil, "_File"],
  ["EditMenu", nil, "_Edit"],
  ["ViewMenu", nil, "_View"],
  ["ProgramMenu", nil, "_Program"],
  ["HelpMenu", nil, "_Help"],
  ["New", Gtk::Stock::NEW, "_New", "<control>N", "Create a new file", on_new_file],
  ["Open", Gtk::Stock::OPEN, "_Open", "<control>O", "Open a file", on_open_file],
  ["Close", Gtk::Stock::CLOSE, "_Close", "<control>W", "Close a file", callback],
  ["Save", Gtk::Stock::SAVE, "_Save", "<control>S", "Save current file", on_save_file],
  ["Save As", Gtk::Stock::SAVE_AS, "Save _As...", nil, "Save to a file", on_save_as_file],
  ["Quit", Gtk::Stock::QUIT, "_Quit", "<control>Q", "Quit", callback_quit],
  ["Undo", Gtk::Stock::UNDO , "_Undo", "<control>Z", "Undo", on_undo],
  ["Redo", Gtk::Stock::REDO, "_Redo", "<controlY", "Redo", on_redo],
  ["Select All", Gtk::Stock::SELECT_ALL, "_Select All", "<controlA", "Select All", on_selectall],
  ["Cut", Gtk::Stock::CUT, "_Cut", "<control>X", "Cut", on_cut],
  ["Copy", Gtk::Stock::COPY, "_Copy", "<control>C", "Copy", on_copy],
  ["Paste", Gtk::Stock::PASTE, "_Paste", "<control>V", "Paste", on_paste],
  ["Compile", Gtk::Stock::PASTE, "_Compile", "<control>B", "Compile", callback],
  ["Run", Gtk::Stock::PASTE, "_Run", nil, "Run", callback],
  ["About", Gtk::Stock::ABOUT, "_About", "<control>O", "About", callback]
]


