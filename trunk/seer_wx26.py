#!/usr/bin/env python

## testfile for older version
import wxversion
wxversion.select("2.60-msw-ansi")

if __name__ == '__main__':
    import seer
    app = seer.sApp(0)
    app.MainLoop()
