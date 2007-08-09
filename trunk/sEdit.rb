#!/usr/bin/env ruby

#
# Utility functions for editing properties (cut/paste/copy)
#
TITLE = 'Text Editor'

def iter_on_screen(iter, mark_str)
  @buffer.place_cursor(iter) 
  @sourceview.scroll_mark_onscreen(@buffer.get_mark(mark_str))
end
def on_clear()
  @buffer.set_text("")
end
def on_cut()
  @sourceview.signal_emit("cut_clipboard")
end
def on_paste()
  @sourceview.signal_emit("paste_clipboard")
end
def on_copy()
  @sourceview.signal_emit("copy_clipboard")
end
def on_selectall()
  @buffer.place_cursor(@buffer.end_iter)
  @buffer.move_mark(@buffer.get_mark("selection_bound"), @buffer.start_iter)
end

# Undo, Redo
def on_undo()
    return if @undopool.size == 0
  action = @undopool.pop 
  case action[0]
  when "insert_text"
    start_iter = @buffer.get_iter_at_offset(action[1])
    end_iter = @buffer.get_iter_at_offset(action[2])
    @buffer.delete(start_iter, end_iter)
  when "delete_range"
    start_iter = @buffer.get_iter_at_offset(action[1])
    @buffer.insert(start_iter, action[3])
  end
  iter_on_screen(start_iter, "insert")
  @redopool << action
end

def on_redo()
  return if @redopool.size == 0
  action = @redopool.pop 
  case action[0]
  when "insert_text"
    start_iter = @buffer.get_iter_at_offset(action[1])
    end_iter = @buffer.get_iter_at_offset(action[2])
    @buffer.insert(start_iter, action[3])
  when "delete_range"
    start_iter = @buffer.get_iter_at_offset(action[1])
    end_iter = @buffer.get_iter_at_offset(action[2])
    @buffer.delete(start_iter, end_iter)
  end
  iter_on_screen(start_iter, "insert")
  @undopool << action
end
