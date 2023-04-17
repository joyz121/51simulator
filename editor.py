# -*- coding: utf-8 -*-

# Author : JoyZheng
#
# Date : 2022/1/10

from PyQt5.QtGui import QColor,QFont, QImage
from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import QSize
import os

class TextArea(QsciScintilla):
    def __init__(self,
        name: str = "Untilted",
        data: str = "",
        path: str = None):
        super(TextArea,self).__init__(parent=None)
        self.setText(data)
        self.__setup_editor()
        self.breakpoint=0
    def __setup_editor(self):
        # QScintilla editor setup
        self.setLexer(None)
        self.setUtf8(True)  # Set encoding to UTF-8
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#1fff0000"))
        self.__myFont =QFont()
        self.__myFont.setPointSize(20)
        self.setFont(self.__myFont)
        # Margin setup
        self.setMarginType(0,QsciScintilla.NumberMargin)
        self.setMarginType(1,QsciScintilla.SymbolMargin)
        self.setMarginWidth(0,"00")
        self.setMarginWidth(1,"000")
        sym = QImage(os.path.join(os.path.abspath(os.path.dirname(__file__))+"/ui/icon/breakpoint.png")).scaled(QSize(40, 40))
        self.markerDefine(sym,0)
        self.setMarginSensitivity(1,True)
        # Connect signal function
        self.marginClicked.connect(self.__margin_left_clicked)
        
    def reset_marker(self,margin_nr,line_nr):
        self.markerDeleteAll()
        self.markerAdd(line_nr,margin_nr)

    def __margin_left_clicked(self, margin_nr, line_nr):
        self.reset_marker(0,line_nr)
        self.breakpoint=line_nr