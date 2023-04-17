# -*- coding: utf-8 -*-

# Author : JoyZheng
#
# Date : 2022/1/7

class sim8051base:
    sfrAddress={'ACC':0xE0,'B':0xF0,'PSW':0xD0,'SP':0x81,'DPH':0x83,'DPL':0x82,'P0':0x80,'P1':0x90,'P2':0xA0
    ,'P3':0xB0,'IP':0xB8,'IE':0xA8,'TMOD':0x89,'TCON':0x88,'TH0':0x8C,'TL0':0x8A,'TH1':0x8D,'TL1':0x8B,'SCON':0x98
    ,'SBUF':0x99,'PCON':0x87}
    RAM=[hex(0)]*256    #256B
    ERAM=[hex(0)]*65536 #64KB
    PC=0
    PC_inc=0
    pc_inc_flag=0
    web_code=""
    code_list=""
    code_len=0
    label={}
    SP=0x07
    error_msg="none"
    error_flag=0

    def clear_memory(self):
        for i in range(0,256):
            self.RAM[i]=hex(0)
    
    def init(self):
        self.clear_memory()
        self.PC=0
        self.SP=0x07
        self.error_flag=0
    
    def split_comment(self,line):
        temp = line.split(',')
        if len(temp) == 1:
            return line.strip().split(' ')
        elif len(temp) == 2:
            return temp[0].strip().split(' ') + [temp[1].strip()]
        elif len(temp) == 3:
            return temp[0].strip().split(' ') + [temp[1].strip()] + [temp[2].strip()]

    def pc_increment(self):
        if self.pc_inc_flag==0:
            self.PC=self.PC+1
        else:
            self.PC=self.PC_inc
            self.pc_inc_flag=0

    def getDiraddress(self,operand):
        if operand in self.sfrAddress.keys():
            return self.sfrAddress[operand]
        else:
            return int(operand.strip('H'),16)

    def getRnaddress(self,operand):
        return int(operand.strip('R'))+((0x18&int(self.RAM[0xD0],16))>>3)*8# Rn address
    
    def getRiaddress(self,operand):
        return int(operand.strip('@R'))+((0x18&int(self.RAM[0xD0],16))>>3)*8
    
    def set_PSW_P(self):
        count=bin(int(self.RAM[self.sfrAddress['ACC']],16)).count('1')#the number of '1'
        if (count%2)==0:#is even number
            self.RAM[self.sfrAddress['PSW']]=hex(int(self.RAM[self.sfrAddress['PSW']],16)&0xfe)#set PSW.P=0
        else:#is odd number
            self.RAM[self.sfrAddress['PSW']]=hex(int(self.RAM[self.sfrAddress['PSW']],16)|0x01)#set PSW.P=1
    
    def setC(self,bit):
        psw=int(self.RAM[self.sfrAddress['PSW']],16)
        psw=psw&0x7f
        self.RAM[self.sfrAddress['PSW']]=hex(psw|bit<<7)

    def getC(self):
        psw=int(self.RAM[self.sfrAddress['PSW']],16)
        return psw>>7
    
    def getBitValue(self,location):
        if location[-1]=='H':
            location=int(location.strip('H'),16)
            if location<=0x7f:
                base=0x20
                iloc=base+location//8
                offset=location%8
                data=int(self.RAM[iloc],16)
                data=data&1<<offset
        elif location[0]=='P':
            tmp=location.split('.')
            location=self.sfrAddress[tmp[0]]
            offset=int(tmp[1])
            data=int(self.RAM[location],16)
            data=data&1<<offset
        if data==0:
            return 0
        else:
            return 1
    
    def clrBitValue(self,location):
        if location[-1]=='H':
            location=int(location.strip('H'),16)
            if location<=0x7f:
                base=0x20
                iloc=base+location//8
                offset=location%8
                data=int(self.RAM[iloc],16)
                self.RAM[iloc]=hex(data& ~(1<<offset))
        elif location[0]=='P':
            tmp=location.split('.')
            location=self.sfrAddress[tmp[0]]
            offset=int(tmp[1])
            data=int(self.RAM[location],16)
            self.RAM[location]=hex(data&~(1<<offset))
    
    def setBitValue(self,location):
        #---SETB bit---#
        if location[-1]=='H':
            location=int(location.strip('H'),16)
            if location<=0x7f:
                base=0x20
                iloc=base+location//8
                offset=location%8
                data=int(self.RAM[iloc],16)
                self.RAM[iloc]=hex(data|1<<offset)
        elif location[0]=='P':
            tmp=location.split('.')
            location=self.sfrAddress[tmp[0]]
            offset=int(tmp[1])
            data=int(self.RAM[location],16)
            self.RAM[location]=hex(data|1<<offset)
    
    def push_data(self,data):
        self.SP+=1
        self.RAM[self.SP]=hex(data)
    
    def pop_data(self):
        data=int(self.RAM[self.SP],16)
        self.SP=self.SP-1
        return data
    
    def decode_first(self,code,code_len):
        i=0
        while i<code_len:
            #get all lable ,then remove it
            line=code[i].split(':')
            if len(line)>1:
                self.label[line[0]]=i
                code[i]=line[1]
            i+=1
        self.code_list=code

    def MOV(self,operand):
        if operand[1][0]=='A':
            #---MOV A,#data---#
            if operand[2][0]=='#':
                self.RAM[self.sfrAddress['ACC']]='0x'+(operand[2].strip('#H'))
            #---MOV A,@Ri---#
            elif operand[2][0]=='@':
                self.RAM[self.sfrAddress['ACC']]=self.RAM[int(self.RAM[self.getRiaddress(operand[2])],16)]
            #---MOV A,Rn---#
            elif operand[2][0]=='R':
                self.RAM[self.sfrAddress['ACC']]=self.RAM[self.getRnaddress(operand[2])]
            #---MOV A,direct---#
            else:
                self.RAM[self.sfrAddress['ACC']]=self.RAM[self.getDiraddress(operand[2])]
        elif operand[1][0]=='R':
            #---MOV Rn,A---#
            if operand[2][0]=='A':
                self.RAM[self.getRnaddress(operand[1])]=self.RAM[self.sfrAddress['ACC']]
            #---MOV Rn,#data---#
            elif operand[2][0]=='#':
                self.RAM[self.getRnaddress(operand[1])]='0x'+(operand[2].strip('#H'))
            #---MOV Rn,direct---#
            else:
                self.RAM[self.getRnaddress(operand[1])]=self.RAM[self.getDiraddress(operand[2])]
        elif operand[1][0]=='@':
            #---MOV @Ri,A---#
            if operand[2][0]=='A':
                self.RAM[int(self.RAM[self.getRiaddress(operand[1])],16)]=self.RAM[self.sfrAddress['ACC']]
            #---MOV @Ri,#data---#
            elif operand[2][0]=='#':
                self.RAM[int(self.RAM[self.getRiaddress(operand[1])],16)]='0x'+(operand[2].strip('#H'))
            #---MOV @Ri,direct---#
            else:
                self.RAM[int(self.RAM[self.getRiaddress(operand[1])],16)]=self.RAM[self.getDiraddress(operand[2])]
        elif operand[1]=='DPTR':
            #---MOV DPTR,#data16---#
            data16=operand[2].strip('#H')
            self.RAM[self.sfrAddress['DPH']]='0x'+data16[:2]
            self.RAM[self.sfrAddress['DPL']]='0x'+data16[-2:]
        
        elif operand[1][0]=='C':
            #---MOV C,bit---#
            self.setC(self.getBitValue(operand[2]))
        else:
            #---MOV bit,C---#
            if operand[2][0]=='C':
                C=self.getC()
                if C==1:
                    self.setBitValue(operand[1])
                else:
                    self.clrBitValue(operand[1])
            #---MOV direct,A---#
            if operand[2][0]=='A':
                self.RAM[self.getDiraddress(operand[1])]=self.RAM[self.sfrAddress['ACC']]
            #---MOV direct,Rn---#
            elif operand[2][0]=='R':
                self.RAM[self.getDiraddress(operand[1])]=self.RAM[self.getRnaddress(operand[2])]
            #---MOV direct,@Ri---#
            elif operand[2][0]=='@':
                self.RAM[self.getDiraddress(operand[1])]=self.RAM[int(self.RAM[self.getRiaddress(operand[2])],16)]
            #---MOV direct,#data---#
            elif operand[2][0]=='#':
                self.RAM[self.getDiraddress(operand[1])]='0x'+(operand[2].strip('#H'))
            #---MOV direct,direct2---#
            else:
                self.RAM[self.getDiraddress((operand[1]))]=self.RAM[self.getDiraddress(operand[2])]

    def MOVX(self,operand):
        if operand[1]=='A':
            #---MOVX A,@DPTR---#
            if operand[2]=='@DPTR':
                adrs=(int(self.sfrAddress['DPH'],16)<<8)+int(self.sfrAddress['DPL'],16)
            elif operand[2][0:-1]=='@R':
            #---MOVX A,@Ri---#
                adrs=int(self.RAM[self.getRiaddress(operand[2])],16)
            self.sfrAddress['ACC']=self.ERAM[adrs]
        elif operand[1]=='@DPTR':
            #---MOVX @DPTR,A---#
            adrs=(int(self.sfrAddress['DPH'],16)<<8)+int(self.sfrAddress['DPL'],16)
            self.ERAM[adrs]=self.sfrAddress['ACC']
        elif operand[1][0:-1]=='@R':
            #---MOVX @Ri,A---#
            adrs=int(self.RAM[self.getRiaddress(operand[1])],16)
            self.ERAM[adrs]=self.sfrAddress['ACC']
        
    def MOVC(self,operand):
        if operand[1]=='A':
            if operand[2]=='@A+DPTR':
                adrs=(int(self.sfrAddress['DPH'],16)<<8)+int(self.sfrAddress['DPL'],16)
                a=int(self.sfrAddress['ACC'],16)
                self.sfrAddress['ACC']=self.ERAM[adrs+a]
            elif operand[2]=='@A+PC':
                pass

    def ADD(self,operand):
        if operand[1]=='A':
            data1=int(self.RAM[self.sfrAddress['ACC']],16)
            #---ADD A,Rn---#
            if operand[2][0]=='R':
                data2=int(self.RAM[self.getRnaddress(operand[2])],16)
            #---ADD A,@Ri---#
            elif operand[2][0]=='@':
                data2=int(self.RAM[int(self.RAM[self.getRiaddress(operand[2])],16)],16)
            #---ADD A,#data---#
            elif operand[2][0]=='#':
                data2=int(operand[2].strip('#H'),16)
            #---ADD A,direct---#
            else:
                data2=int(self.RAM[self.getDiraddress(operand[2])],16)
            #set psw
            psw=int(self.RAM[self.sfrAddress['PSW']],16)
            sum=(data1&0xff)+(data2&0xff)
            CY=sum&0x100
            ps_temp=(psw|0x80)                  #ps_temp.D7=1
            psw=((CY>>1)|0x7f)&ps_temp          #set psw.D7
            ps_temp=(psw|0x40)                  #ps_temp.D6=1
            AC=(data1&0x0f)+(data2&0x0f)        #add the low 4 bits
            psw=(((AC&0x10)<<2)|0xbf)&ps_temp   #set psw.D6
            OV=((data1&0x7f)+(data2&0x7f))&0x80 #whether D6 is carry
            if CY^OV:
                psw=psw|0x04 #set OV=1
            else:
                psw=psw&0xFB #set 0V=0
            self.RAM[self.sfrAddress['PSW']]=hex(psw)
            #set ACC
            self.RAM[self.sfrAddress['ACC']]=hex((data1+data2)&0xff)

    def ADDC(self,operand):
        if operand[1]=='A':
            data1=int(self.RAM[self.sfrAddress['ACC']],16)
            #---ADDC A,Rn---#
            if operand[2][0]=='R':
                data2=int(self.RAM[self.getRnaddress(operand[2])],16)
            #---ADDC A,@Ri---#
            elif operand[2][0]=='@':
                data2=int(self.RAM[int(self.RAM[self.getRiaddress(operand[2])],16)],16)
            #---ADDC A,#data---#
            elif operand[2][0]=='#':
                data2=int(operand[2].strip('#H'),16)
            #---ADDC A,direct---#
            else:
                data2=int(self.RAM[self.getDiraddress(operand[2])],16)
            #set psw
            psw=int(self.RAM[self.sfrAddress['PSW']],16)
            C=psw>>7
            sum=(data1&0xff)+(data2&0xff)+(C&0xff)
            CY=sum&0x100
            ps_temp=(psw|0x80)                      #ps_temp.D7=1
            psw=((CY>>1)|0x7f)&ps_temp              #set psw.D7
            ps_temp=(psw|0x40)                      #ps_temp.D6=1
            AC=(data1&0x0f)+(data2&0x0f)+C          #add the low 4 bits
            psw=(((AC&0x10)<<2)|0xbf)&ps_temp       #set psw.D6
            OV=((data1&0x7f)+(data2&0x7f)+C)&0x80   #whether D6 is carry
            if CY^OV:
                psw=psw|0x04 #set OV=1
            else:
                psw=psw&0xFB #set 0V=0
            self.RAM[self.sfrAddress['PSW']]=hex(psw)
            #set ACC
            self.RAM[self.sfrAddress['ACC']]=hex((data1+data2+C)&0xff)

    def SUBB(self,operand):
        if operand[1]=='A':
            data1=int(self.RAM[self.sfrAddress['ACC']],16)
            #---SUBB A,Rn---#
            if operand[2][0]=='R':
                data2=int(self.RAM[self.getRnaddress(operand[2])],16)
            #---SUBB A,@Ri---#
            elif operand[2][0]=='@':
                data2=int(self.RAM[int(self.RAM[self.getRiaddress(operand[2])],16)],16)
            #---SUBB A,#data---#
            elif operand[2][0]=='#':
                data2=int(operand[2].strip('#H'),16)
            #---SUBB A,direct---#
            else:
                data2=int(self.RAM[self.getDiraddress(operand[2])],16)
            #set psw
            psw=int(self.RAM[self.sfrAddress['PSW']],16)
            C=psw>>7
            diff=(data1&0xff)-(data2&0xff)-(C&0xff)
            CY=diff&0x100
            ps_temp=(psw|0x80)                      #ps_temp.D7=1
            psw=((CY>>1)|0x7f)&ps_temp              #set psw.D7
            ps_temp=(psw|0x40)                      #ps_temp.D6=1
            AC=(data1&0x0f)-(data2&0x0f)-C          #add the low 4 bits
            psw=(((AC&0x10)<<2)|0xbf)&ps_temp       #set psw.D6
            OV=((data1&0x7f)-(data2&0x7f)-C)&0x80   #whether D6 is carry
            if CY^OV:
                psw=psw|0x04 #set OV=1
            else:
                psw=psw&0xFB #set 0V=0
            self.RAM[self.sfrAddress['PSW']]=hex(psw)
            #set ACC
            self.RAM[self.sfrAddress['ACC']]=hex((data1-data2-C)&0xff)

    def INC(self,operand):
        #---INC A---#
        if operand[1]=='A':
            self.RAM[self.sfrAddress['ACC']]=hex((int(self.RAM[self.sfrAddress['ACC']],16)+1)&0xff)
        #---INC Rn---#
        elif operand[1][0]=='R':
            self.RAM[self.getRnaddress(operand[1])]=hex((int(self.RAM[self.getRnaddress(operand[1])],16)+1)&0xff)
        #---INC @Ri---#
        elif operand[1][0]=='@':
            self.RAM[int(self.RAM[self.getRiaddress(operand[1])],16)]=hex((int(self.RAM[int(self.RAM[self.getRiaddress(operand[1])],16)],16)+1)&0xff)
        #---INC DPTR---#
        elif operand[1]=='DPTR':
            dpl=int(self.RAM[self.sfrAddress['DPL']],16)
            dph=int(self.RAM[self.sfrAddress['DPH']],16)
            val=(dpl|dph<<8)+1
            self.RAM[self.sfrAddress['DPL']]=hex(val&0xff)
            self.RAM[self.sfrAddress['DPH']]=hex((val&0xff00)>>8)
        #---INC direct---#
        else:
            self.RAM[self.getDiraddress(operand[1])]=hex((int(self.RAM[self.getDiraddress(operand[1])],16)+1)&0xff)
    
    def DEC(self,operand):
        #---DEC A---#
        if operand[1]=='A':
            self.RAM[self.sfrAddress['ACC']]=hex((int(self.RAM[self.sfrAddress['ACC']],16)-1)&0xff)
        #---DEC Rn---#
        elif operand[1][0]=='R':
            self.RAM[self.getRnaddress(operand[1])]=hex((int(self.RAM[self.getRnaddress(operand[1])],16)-1)&0xff)
        #---DEC @Ri---#
        elif operand[1][0]=='@':
            self.RAM[int(self.RAM[self.getRiaddress(operand[1])],16)]=hex((int(self.RAM[int(self.RAM[self.getRiaddress(operand[1])],16)],16)-1)&0xff)
        #---DEC direct---#
        else:
            self.RAM[self.getDiraddress(operand[1])]=hex((int(self.RAM[self.getDiraddress(operand[1])],16)-1)&0xff)
    
    def MUL(self,operand):
        #---MUL AB---#
        if operand[1]=='AB':
            val=int(self.RAM[self.sfrAddress['ACC']],16)*int(self.RAM[self.sfrAddress['B']],16)
            self.RAM[self.sfrAddress['ACC']]=hex((val&0xff))
            self.RAM[self.sfrAddress['B']]=hex((val&0xff00)>>8)
            if int(self.RAM[self.sfrAddress['B']],16)==0:
                self.RAM[self.sfrAddress['PSW']]=hex(int(self.RAM[self.sfrAddress['PSW']],16)&0xfb) #set 0V=0
            else:
                self.RAM[self.sfrAddress['PSW']]=hex(int(self.RAM[self.sfrAddress['PSW']],16)|0x04) #set 0V=1
            #CY=0 always
            self.RAM[self.sfrAddress['PSW']]=hex(int(self.RAM[self.sfrAddress['PSW']],16)&0x7f)
            
    def DIV(self,operand):
        #---DIV AB---#
        if operand[1]=='AB':
            a=int(self.RAM[self.sfrAddress['ACC']],16)
            b=int(self.RAM[self.sfrAddress['B']],16)
            if b!=0:
                self.RAM[self.sfrAddress['ACC']]=hex(a//b)
                self.RAM[self.sfrAddress['B']]=hex(a%b)
                self.RAM[self.sfrAddress['PSW']]=hex(int(self.RAM[self.sfrAddress['PSW']],16)&0xfb) #set 0V=0
            else:
                self.RAM[self.sfrAddress['PSW']]=hex(int(self.RAM[self.sfrAddress['PSW']],16)|0x04) #set 0V=1
            #CY=0 always
            self.RAM[self.sfrAddress['PSW']]=hex(int(self.RAM[self.sfrAddress['PSW']],16)&0x7f)
    
    def DA(self,operand):
        pass
    
    def ANL(self,operand):
        if operand[1][0]=='A':
            data1=int(self.RAM[self.sfrAddress['ACC']],16)
            #---ANL A,Rn---#
            if operand[2][0]=='R':
                data2=int(self.RAM[self.getRnaddress(operand[2])],16)
            #---ANL A,@Ri---#
            elif operand[2][0]=='@':
                data2=int(self.RAM[int(self.RAM[self.getRiaddress(operand[2])],16)],16)
            #---ANL A,#data---#
            elif operand[2][0]=='#':
                data2=int(operand[2].strip('#H'),16)
            #---ANL A,direct---#
            else:
                data2=int(self.RAM[self.getDiraddress(operand[2])],16)
            self.RAM[self.sfrAddress['ACC']]=hex(data1&data2)
        elif operand[1][0]=='C':
            C=self.getC()
            #---ANL C,/bit---#
            if operand[2][0]=='/':
                bit=~self.getBitValue(operand[2].strip('/'))
             #---ANL C,bit---#
            else:
                bit=self.getBitValue(operand[2])
            self.setC(C&bit)
        else:
            data1=int(self.RAM[self.getDiraddress(operand[1])],16)
            #---ANL direct,A---#
            if operand[2][0]=='A':
                data2=int(self.RAM[self.sfrAddress['ACC']],16)
            #---ANL direct,#data---#
            elif operand[2][0]=='#':
                data2=int(operand[2].strip('#H'),16)
            self.RAM[self.getDiraddress(operand[1])]=hex(data1&data2)
    
    def ORL(self,operand):
        if operand[1][0]=='A':
            data1=int(self.RAM[self.sfrAddress['ACC']],16)
            #---ORL A,Rn---#
            if operand[2][0]=='R':
                data2=int(self.RAM[self.getRnaddress(operand[2])],16)
            #---ORL A,@Ri---#
            elif operand[2][0]=='@':
                data2=int(self.RAM[int(self.RAM[self.getRiaddress(operand[2])],16)],16)
            #---ORL A,#data---#
            elif operand[2][0]=='#':
                data2=int(operand[2].strip('#H'),16)
            #---ORL A,direct---#
            else:
                data2=int(self.RAM[self.getDiraddress(operand[2])],16)
            self.RAM[self.sfrAddress['ACC']]=hex(data1|data2)
        elif operand[1][0]=='C':
            C=self.getC()
            #---ANL C,/bit---#
            if operand[2][0]=='/':
                bit=~self.getBitValue(operand[2].strip('/'))
             #---ANL C,bit---#
            else:
                bit=self.getBitValue(operand[2])
            self.setC(C|bit)
        else:
            data1=int(self.RAM[self.getDiraddress(operand[1])],16)
            #---ORL direct,A---#
            if operand[2][0]=='A':
                data2=int(self.RAM[self.sfrAddress['ACC']],16)
            #---ORL direct,#data---#
            elif operand[2][0]=='#':
                data2=int(operand[2].strip('#H'),16)
            self.RAM[self.getDiraddress(operand[1])]=hex(data1|data2)
    
    def XRL(self,operand):
        if operand[1][0]=='A':
            data1=int(self.RAM[self.sfrAddress['ACC']],16)
            #---XRL A,Rn---#
            if operand[2][0]=='R':
                data2=int(self.RAM[self.getRnaddress(operand[2])],16)
            #---XRL A,@Ri---#
            elif operand[2][0]=='@':
                data2=int(self.RAM[int(self.RAM[self.getRiaddress(operand[2])],16)],16)
            #---XRL A,#data---#
            elif operand[2][0]=='#':
                data2=int(operand[2].strip('#H'),16)
            #---XRL A,direct---#
            else:
                data2=int(self.RAM[self.getDiraddress(operand[2])],16)
            self.RAM[self.sfrAddress['ACC']]=hex(data1^data2)
        else:
            data1=int(self.RAM[self.getDiraddress(operand[1])],16)
            #---XRL direct,A---#
            if operand[2][0]=='A':
                data2=int(self.RAM[self.sfrAddress['ACC']],16)
            #---XRL direct,#data---#
            elif operand[2][0]=='#':
                data2=int(operand[2].strip('#H'),16)
            self.RAM[self.getDiraddress(operand[1])]=hex(data1^data2)
    
    def CLR(self,operand):
        #---CLR A---#
        if operand[1]=='A':
            self.RAM[self.sfrAddress['ACC']]=hex(0)
        #---CLR C---#
        elif operand[1]=='C':
            self.setC(0)
        else:
            #CLR bit
            self.clrBitValue(operand[1])

    def CPL(self,operand):
        #---CPL A---#
        if operand[1]=='A':
            self.RAM[self.sfrAddress['ACC']]=hex(int(self.RAM[self.sfrAddress['ACC']],16)^0xff)
        elif operand[1]=='C':
        #---CPL C---#
            self.setC(~self.getC())
        else:
        #---CPL bit---#
            abit=self.getBitValue(operand[1])
            if abit==1:
                self.clrBitValue(operand[1])
            else:
                self.setBitValue(operand[1])
        
    def RL(self,operand):
        #---RL A---#
        if operand[1]=='A':
            val=int(self.RAM[self.sfrAddress['ACC']],16)
            A7=val>>7
            val=((val<<1)&0xff)|A7
            self.RAM[self.sfrAddress['ACC']]=hex(val)

    def RLC(self,operand):
        #---RLC A---#
        if operand[1]=='A':
            val=int(self.RAM[self.sfrAddress['ACC']],16)
            CY=int(self.RAM[self.sfrAddress['PSW']],16)>>7
            A7=val&0x80
            self.RAM[self.sfrAddress['PSW']]=hex((int(self.RAM[self.sfrAddress['PSW']],16)&0x7f)|A7)#CY<-A7
            val=((val<<1)&0xff)|CY
            self.RAM[self.sfrAddress['ACC']]=hex(val)
    
    def RR(self,operand):
        #---RR A---#
        if operand[1]=='A':
            val=int(self.RAM[self.sfrAddress['ACC']],16)
            A0=(val&0x01)<<7
            val=(val>>1)|A0
            self.RAM[self.sfrAddress['ACC']]=hex(val)
    
    def RRC(self,operand):
        #---RRC A---#
        if operand[1]=='A':
            val=int(self.RAM[self.sfrAddress['ACC']],16)
            CY=int(self.RAM[self.sfrAddress['PSW']],16)&0x80
            A0=val&0x01
            self.RAM[self.sfrAddress['PSW']]=hex((int(self.RAM[self.sfrAddress['PSW']],16)&0x7f)|(A0<<7))#CY<-A0
            val=(val>>1)|CY
            self.RAM[self.sfrAddress['ACC']]=hex(val)

    def SWAP(self,operand):
        #---SWAP A---#
        if operand[1]=='A':
            val=int(self.RAM[self.sfrAddress['ACC']],16)
            h=(val<<4)&0xff
            l=(val>>4)&0xff
            val=h+l
            self.RAM[self.sfrAddress['ACC']]=hex(val)
    
    def ACALL(self,operand):
        pass
    
    def LCALL(self,operand):
        pass
    
    def RET(self,):
        pass
    
    def RET1(self,):
        pass
    
    def AJMP(self,operand):
        #---AJMP add---#
        self.pc_inc_flag=1
        self.PC_inc=self.label[operand[1]]
    
    def LJMP(self,operand):
        #---LJMP add ---#
        self.pc_inc_flag=1
        self.PC_inc=self.label[operand[1]]
    
    def SJMP(self,operand):
        #---LJMP rel ---#
        self.pc_inc_flag=1
        self.PC_inc=self.label[operand[1]]
    
    def JMP(self,operand):
        pass

    def JZ(self,operand):
        #---JZ rel---#
        if int(self.RAM[self.sfrAddress['ACC']],16)==0:
            self.pc_inc_flag=1
            self.PC_inc=self.label[operand[1]]
        else:
            pass
    
    def JNZ(self,operand):
        #---JNZ rel---#
        if not(int(self.RAM[self.sfrAddress['ACC']],16)==0):
            self.pc_inc_flag=1
            self.PC_inc=self.label[operand[1]]
        else:
            pass
    
    def CJNE(self,operand):
        if operand[1][0]=='A':
            data1=int(self.RAM[self.sfrAddress['ACC']],16)
            #---CJNE A,#data,rel---#
            if operand[2][0]=='#':
                data2=int(operand[2].strip('#H'),16)
            #---CJNE A,direct,rel---#
            else:
                data2=int(self.RAM[self.getDiraddress(operand[2])],16)
        elif operand[1][0]=='R':
            #---CJNE Rn,#data,rel---#
            data1=int(self.RAM[self.getRnaddress(operand[1])],16)
            data2=int(operand[2].strip('#H'),16)
        elif operand[1][0]=='@':
            #---CJNE @Ri,#data,rel---#
            data1=int(self.RAM[int(self.RAM[self.getRiaddress(operand[1])],16)],16)
            data2=int(operand[2].strip('#H'),16)
        if not(data1==data2):
            self.pc_inc_flag=1
            self.PC_inc=self.label[operand[3]]
        if data1<data2:
            self.setC(1)
        else:
            self.setC(0)
    
    def DJNZ(self,operand):
        if operand[1][0]=='R':
        #---DJNZ Rn,rel---#
            data=int(self.RAM[self.getRnaddress(operand[1])],16)-1
            if(data<0):
                data=0xff
            self.RAM[self.getRnaddress(operand[1])]=hex(data)
        else:
        #---DJNZ direct,rel---#
            data=int(self.RAM[self.getDiraddress(operand[1])],16)-1
            if(data<0):
                data=0xff
            self.RAM[self.getDiraddress(operand[1])]=hex(data)
        if not(data==0):
            self.pc_inc_flag=1
            self.PC_inc=self.label[operand[2]]
        else:
            pass
    
    def NOP(self,operand):
        pass
    
    def JC(self,operand):
        #---JC rel---#
        if self.getC()==1:
            self.pc_inc_flag=1
            self.PC_inc=self.label[operand[1]]
        else:
            pass
    
    def SETB(self,operand):
        #---SETB C---#
        if operand[1]=='C':
            self.setC(1)
        else:
        #---SETB bit---#
            self.setBitValue(operand[1])

    def JNC(self,operand):
        #---JNC rel---#
        if self.getC()==0:
            self.pc_inc_flag=1
            self.PC_inc=self.label[operand[1]]
        else:
            pass
    
    def JB(self,operand):
        #---JB bit,rel---#
        if self.getBitValue(operand[1])==1:
            self.pc_inc_flag=1
            self.PC_inc=self.label[operand[2]]

    def JNB(self,operand):
        #---JNB bit,rel---#
        if not (self.getBitValue(operand[1])==1):
            self.pc_inc_flag=1
            self.PC_inc=self.label[operand[2]]

    def JBC(self,operand):
        #---JBC bit,rel---#
        if self.getBitValue(operand[1])==1:
            self.pc_inc_flag=1
            self.PC_inc=self.label[operand[2]]
            self.clrBitValue(operand[1])

    def PUSH(self,operand):
        #---PUSH direct---#
        data=int(self.RAM[self.getDiraddress(operand[1])],16)
        self.push_data(data)
    
    def POP (self,operand):
        #---POP direct---#
        data=self.pop_data()
        self.RAM[self.getDiraddress(operand[1])]=hex(data)
    
    def compile(self,line_code):
        opcode=line_code[0]
        if opcode=='MOV':
            self.MOV(line_code)
        elif opcode=='MOVX':
            self.MOVX(line_code)
        elif opcode=='ADD':
            self.ADD(line_code)
        elif opcode=='ADDC':
            self.ADDC(line_code)
        elif opcode=='SUBB':
            self.SUBB(line_code)
        elif opcode=='INC':
            self.INC(line_code)
        elif opcode=='DEC':
            self.DEC(line_code)
        elif opcode=='MUL':
            self.MUL(line_code)
        elif opcode=='DIV':
            self.DIV(line_code)
        elif opcode=='DA':
            self.DA(line_code)
        elif opcode=='ANL':
            self.ANL(line_code)
        elif opcode=='ORL':
            self.ORL(line_code)
        elif opcode=='XRL':
            self.XRL(line_code)
        elif opcode=='CLR':
            self.CLR(line_code)
        elif opcode=='CPL':
            self.CPL(line_code)
        elif opcode=='RL':
            self.RL(line_code)
        elif opcode=='RLC':
            self.RLC(line_code)
        elif opcode=='RR':
            self.RR(line_code)
        elif opcode=='RRC':
            self.RRC(line_code)
        elif opcode=='SWAP':
            self.SWAP(line_code)
        elif opcode=='ACALL':
            self.ACALL(line_code)
        elif opcode=='LCALL':
            self.LCALL(line_code)
        elif opcode=='RET':
            self.RET()
        elif opcode=='RET1':
            self.RET1()
        elif opcode=='AJMP':
            self.AJMP(line_code)
        elif opcode=='LJMP':
            self.LJMP(line_code)
        elif opcode=='SJMP':
            self.SJMP(line_code)
        elif opcode=='JMP':
            self.JMP(line_code)
        elif opcode=='JZ':
            self.JZ(line_code)
        elif opcode=='JNZ':
            self.JNZ(line_code)
        elif opcode=='CJNE':
            self.CJNE(line_code)
        elif opcode=='DJNZ':
            self.DJNZ(line_code)
        elif opcode=='NOP':
            self.NOP()
        elif opcode=='SETB':
            self.SETB(line_code)
        elif opcode=='JC':
            self.JC(line_code)
        elif opcode=='JNC':
            self.JNC(line_code)
        elif opcode=='JB':
            self.JB(line_code)
        elif opcode=='JNB':
            self.JNB(line_code)
        elif opcode=='JBC':
            self.JBC(line_code)
        elif opcode=='PUSH':
            self.PUSH(line_code)
        elif opcode=='POP':
            self.POP(line_code)
        else:
            self.error_flag=1
        self.set_PSW_P()
sim51=sim8051base()