# -*- coding: utf-8 -*-

# Author : JoyZheng
#
# Date : 2022/1/7

import os
import sys
import qdarkstyle
from PyQt5 import uic,QtWidgets,QtCore
from PyQt5.QtWidgets import QApplication, QDockWidget,QMainWindow,QTableWidgetItem
from editor import TextArea
from simbase import *
from qdarkstyle.light.palette import LightPalette

# Make the file runnable without the need to  include ui
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/../ui'))
here = os.path.abspath(os.path.dirname(__file__))

class Sim_MainWindow(QMainWindow):
    def __init__(self,parent=None):
        super(Sim_MainWindow,self).__init__(parent)
        # Load ui files
        uic.loadUi(os.path.join(here, 'ui\sim_menu.ui'), self)
        self.memory_dock=QDockWidget()
        uic.loadUi(os.path.join(here, 'ui\sim_memory.ui'),self.memory_dock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,self.memory_dock)#add dockwidget to mainwindow
        # Connect signal function
        self.action_openfile.triggered.connect(self.openfile_click_success)
        self.action_savefile.triggered.connect(self.savefile_click_success)
        self.action_newfile.triggered.connect(self.newfile_click_success)
        self.action_debug.triggered.connect(self.debug_click_success)
        self.action_debugnext.triggered.connect(self.debugnext_click_success)
        self.action_clearmemory.triggered.connect(self.clearmemory_click_success)
        self.action_run.triggered.connect(self.run_click_success)
        # Creat a Textarea
        self.__editor=TextArea()
        self.codearea_Layout.addWidget(self.__editor)
        
    # Open file
    def openfile_click_success(self):
        file_path= QtWidgets.QFileDialog.getOpenFileName(self,"选择文件",os.getcwd(),"All Files(*);;asm(*.asm)")
        if file_path[0]:
            with open(file_path[0],'r') as f:
                open_text=f.read()
                self.__editor.setText(open_text)
                self.__editor.markerDeleteAll()
    
    # Save file
    def savefile_click_success(self):
        file_path=QtWidgets.QFileDialog.getSaveFileName(self,"选择保存路径",os.getcwd(),"asm(*.asm)")
        if file_path[0]:
            with open(file_path[0],'w') as f:
                save_text=self.__editor.text().replace("\r", '')
                f.write(save_text)
    # New file
    def newfile_click_success(self):
        pass
    def run_click_success(self):
        # get codelist
        sim51.code_list=self.__editor.text().splitlines()
        sim51.code_len=len(sim51.code_list)
        sim51.decode_first(sim51.code_list,sim51.code_len)
        sim51.init()
        while sim51.PC <sim51.code_len:
            com=sim51.split_comment(sim51.code_list[sim51.PC])
            sim51.compile(com)
            sim51.pc_increment()
            self.refresh_memory()

    debug_status='off'
    def debug_click_success(self):
        if self.debug_status=='off':
            # on
            self.debug_status='on'
            # get codelist
            sim51.code_list=self.__editor.text().splitlines()
            sim51.code_len=len(sim51.code_list)
            sim51.decode_first(sim51.code_list,sim51.code_len)
            sim51.PC=self.__editor.breakpoint
            # disable other actions
            self.action_run.setEnabled(False)
            self.action_clearmemory.setEnabled(False)
            # enable debug action
            self.action_debugnext.setEnabled(True)
            # When debug_status is 'on',margin mouse clicks is ont allowed
            self.__editor.setMarginSensitivity(1,False)
        elif self.debug_status=='on':
            # off
            self.debug_status='off'
            # enable other actions
            self.action_run.setEnabled(True)
            self.action_clearmemory.setEnabled(True)
            # disable debug action
            self.action_debugnext.setEnabled(False)
            # When debug_status is 'off',margin mouse clicks is allowed
            self.__editor.setMarginSensitivity(1,True)

    def debugnext_click_success(self):
        if sim51.PC<sim51.code_len:
            com=sim51.split_comment(sim51.code_list[sim51.PC])
            sim51.compile(com)
            sim51.pc_increment()
            self.refresh_memory()
            self.__editor.breakpoint=sim51.PC
            self.__editor.reset_marker(0,self.__editor.breakpoint)
    
    def clearmemory_click_success(self):
        sim51.init()
        self.refresh_memory()

    #Refresh memory
    def refresh_memory(self):
        #SFR
        self.memory_dock.Sfr_tableWidget.setItem(0,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['ACC']]))
        self.memory_dock.Sfr_tableWidget.setItem(1,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['B']]))
        self.memory_dock.Sfr_tableWidget.setItem(2,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['PSW']]))
        self.memory_dock.Sfr_tableWidget.setItem(3,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['SP']]))
        self.memory_dock.Sfr_tableWidget.setItem(4,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['DPH']]))
        self.memory_dock.Sfr_tableWidget.setItem(5,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['DPL']]))
        self.memory_dock.Sfr_tableWidget.setItem(6,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['P0']]))
        self.memory_dock.Sfr_tableWidget.setItem(7,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['P1']]))
        self.memory_dock.Sfr_tableWidget.setItem(8,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['P2']]))
        self.memory_dock.Sfr_tableWidget.setItem(9,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['P3']]))
        self.memory_dock.Sfr_tableWidget.setItem(10,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['IP']]))
        self.memory_dock.Sfr_tableWidget.setItem(11,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['IE']]))
        self.memory_dock.Sfr_tableWidget.setItem(12,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['TMOD']]))
        self.memory_dock.Sfr_tableWidget.setItem(13,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['TCON']]))
        self.memory_dock.Sfr_tableWidget.setItem(14,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['TH0']]))
        self.memory_dock.Sfr_tableWidget.setItem(15,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['TL0']]))
        self.memory_dock.Sfr_tableWidget.setItem(16,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['TH1']]))
        self.memory_dock.Sfr_tableWidget.setItem(17,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['TL1']]))
        self.memory_dock.Sfr_tableWidget.setItem(18,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['SCON']]))
        self.memory_dock.Sfr_tableWidget.setItem(19,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['SBUF']]))
        self.memory_dock.Sfr_tableWidget.setItem(20,1,QTableWidgetItem(sim51.RAM[sim51.sfrAddress['PCON']]))
        #RAM
        for i in range(0,32):
            for j in  range(0,8):
                self.memory_dock.Ram_tableWidget.setItem(i,j+1,QTableWidgetItem(sim51.RAM[8*(i)+j]))

if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5',palette=LightPalette()))
    simwin =Sim_MainWindow()
    simwin.refresh_memory()
    simwin.show()
    sys.exit(app.exec())