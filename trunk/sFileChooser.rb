require 'gtk2'

class FileChooser
  def open
    dialog =  Gtk::FileChooserDialog.new("Open File", @window, 
    				     Gtk::FileChooser::ACTION_OPEN, "nil",
    				     [Gtk::Stock::OPEN, Gtk::Dialog::RESPONSE_ACCEPT],
    				     [Gtk::Stock::CANCEL, Gtk::Dialog::RESPONSE_CANCEL])
				     
    filter_rb = Gtk::FileFilter.new
    filter_rb.name = "Ruby Scripts"
    filter_rb.add_pattern("*.rb")
    filter_rb.add_pattern("*.rbw")
    dialog.add_filter(filter_rb)

    filter_c = Gtk::FileFilter.new
    filter_c.name = "C sources"
    filter_c.add_pattern("*.[c|h]")
    dialog.add_filter(filter_c)

    if dialog.run == Gtk::Dialog::RESPONSE_ACCEPT
      puts "filename = #{dialog.filename}"
      puts "uri = #{dialog.uri}"
      @filename = dialog.filename
      dialog.destroy
      dialog.hide
    else
      dialog.hide
    end
  end
end
