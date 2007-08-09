require 'gtk2'
require 'ui'
require 'sView'
require 'sEdit'

@window = Gtk::Window.new("Seir Text Editor")
actiongroup = Gtk::ActionGroup.new("Actions")
@sw = Gtk::ScrolledWindow.new
@box = Gtk::VBox.new
@status = Gtk::Statusbar.new

actiongroup.add_actions(@actions)
uimanager = Gtk::UIManager.new
uimanager.insert_action_group(actiongroup, 0)
@window.add_accel_group(uimanager.accel_group)
uimanager.add_ui(@ui_info)
  
@sw.add(@sourceview)
@window.signal_connect("delete-event"){Gtk::main_quit}
  
@box.pack_start(uimanager["/MenuBar"], false, false)
@box.pack_start(uimanager["/ToolBar"], false, false)
@box.pack_start(@sw)
@box.pack_start(@status, false)
  
@window.add(@box)
@window.set_default_size(400,300)
@window.show_all

Gtk.main
