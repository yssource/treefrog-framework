win32 {
  INCLUDEPATH += $$quote($$(TFDIR)\\include)
  LIBS += -L$$quote($$(TFDIR)\\bin)
  CONFIG(debug, debug|release) {
    LIBS += -ltreefrogd1
  } else {
    LIBS += -ltreefrog1
  }
} else {
  unix:!macx {
    unix:LIBS += -Wl,-rpath,. -Wl,-rpath,/usr/lib -L/usr/lib -ltreefrog
    unix:INCLUDEPATH += /usr/include/treefrog
  }
  macx: {
    unix:LIBS += -Wl,-rpath,. -Wl,-rpath,/usr/local/lib -L/usr/local/lib -ltreefrog
    unix:INCLUDEPATH += /usr/local/include/treefrog
  }
  linux-*:LIBS += -lrt
}
