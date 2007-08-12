require 'gtk2'
require 'gtksourceview'

@lang = Gtk::SourceLanguagesManager.new.get_language('text/x-ruby')
@sourceview = Gtk::SourceView.new()
@buffer = @sourceview.buffer
@buffer.language = @lang

@sourceview.buffer.highlight = true
@sourceview.show_line_numbers = 1
@sourceview.auto_indent = 1
    
@undopool = Array.new
@redopool = Array.new

#Signal connections
@buffer.signal_connect("insert_text") do |w, iter, text, length|
  if @user_action
    @undopool <<  ["insert_text", iter.offset, iter.offset + text.scan(/./).size, text]
    @redopool.clear
  end
end
@buffer.signal_connect("delete_range") do |w, start_iter, end_iter|
  text = @buffer.get_text(start_iter, end_iter)
  @undopool <<  ["delete_range", start_iter.offset, end_iter.offset, text] if @user_action
end
@buffer.signal_connect("begin_user_action") do
  @user_action = true
end
@buffer.signal_connect("end_user_action") do
  @user_action = false
end
