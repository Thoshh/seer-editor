#!/usr/bin/env ruby

#
# Utility functions for file access

# Start File access
def save_file
  File.open(@filename, "w"){|f| 
    f.write(@buffer.get_text(*@buffer.bounds)) 
  }
  @buffer.modified = false
end
def read_file
  File.open(@filename){|f| ret = f.readlines.join }
end
#def open_file
#  text = read_file
  # 
  # experimental source highlighting
  # @slm = SourceLanguagesManager.new
  # @filename = 
  #
#  @buffer.text = text
#end
# file chooser dialog
# TODO: make dialog more intelligent, i.e., @buffer.modified?
def selected_file
    dialog = Gtk::FileChooserDialog.new("Open File", @window,
                             Gtk::FileChooser::ACTION_OPEN, nil,
                             [Gtk::Stock::CANCEL, Gtk::Dialog::RESPONSE_CANCEL],
                             [Gtk::Stock::OPEN, Gtk::Dialog::RESPONSE_ACCEPT])
    if dialog.run == Gtk::Dialog::RESPONSE_ACCEPT
      @filename = dialog.filename
      @window.set_title(TITLE + ":" + @filename)
      dialog.destroy
      @filechooser.hide
    else
      @filechooser.hide
  end
end

def on_open_file
  selected_file
  if @filename
    text = read_file
    @buffer.set_text(text)
  end
  @buffer.place_cursor(@buffer.start_iter)
  @sourceview.has_focus = true
end
def on_new_file
  if @buffer.modified?
    on_save_as_file
  end
  @filename = nil
  on_clear
end
def on_save_as_file
  selected_file
  save_file if @filename
end
def on_save_file
  if @filename
    save_file
  else
    on_save_as_file
  end
end
