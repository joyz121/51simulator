# -*- coding: utf-8 -*-
# Author : JoyZheng
#
# Date : 2022/4/7
from django.shortcuts import render
import sys
import numpy as np
sys.path.append('../')
import simbase
# 接收POST请求数据

def run(request):
    #Django -request.POST一个表单，多个按钮
    if request.POST:
        if 'sim' in request.POST:
            simbase.sim51.web_code = request.POST['web_code']
            simbase.sim51.code_list=simbase.sim51.web_code.splitlines()
            simbase.sim51.code_len=len(simbase.sim51.code_list)
            simbase.sim51.decode_first(simbase.sim51.code_list,simbase.sim51.code_len)
            simbase.sim51.init()
            while simbase.sim51.PC <simbase.sim51.code_len:
                com=simbase.sim51.split_comment(simbase.sim51.code_list[simbase.sim51.PC])
                simbase.sim51.compile(com)
                if simbase.sim51.error_flag==1:
                    simbase.sim51.error_msg="message:无法识别  "+simbase.sim51.code_list[simbase.sim51.PC]
                    break
                simbase.sim51.pc_increment()
            if simbase.sim51.error_flag==0:
                simbase.sim51.error_msg="message:程序运行成功"
        elif 'clear' in request.POST:
            simbase.sim51.web_code =''
            simbase.sim51.init()
            simbase.sim51.error_msg="message:已清空代码区和所有寄存器"
        elif 'debug' in request.POST:
            simbase.sim51.web_code = request.POST['web_code']
            simbase.sim51.code_list=simbase.sim51.web_code.splitlines()
            simbase.sim51.code_len=len(simbase.sim51.code_list)
            simbase.sim51.decode_first(simbase.sim51.code_list,simbase.sim51.code_len)
            if simbase.sim51.PC<simbase.sim51.code_len:
                com=simbase.sim51.split_comment(simbase.sim51.code_list[simbase.sim51.PC])
                simbase.sim51.compile(com)
                if simbase.sim51.error_flag==0:
                    simbase.sim51.error_msg="message：成功运行  "+simbase.sim51.code_list[simbase.sim51.PC]
                elif simbase.sim51.error_flag==1:
                    simbase.sim51.error_msg="message：运行失败，请检查代码  "+simbase.sim51.code_list[simbase.sim51.PC]
                simbase.sim51.pc_increment()
    context={}
    adrs=[]
    sfr_value=[]
    a=[]
    last_ram=[hex(0)]*(32*9)
    last_ram=np.array(np.array_split(last_ram,32))
    colr_flag=[0]*(32*8)
    colr_flag=np.array(np.array_split(colr_flag,32))
    #sfr
    sfr=simbase.sim51.sfrAddress
    sfr_keys=sfr.keys()#getkey
    sfr_adrs=sfr.values()#getvalue
    for i in sfr_adrs:
        sfr_value.append(simbase.sim51.RAM[i])
    #ram
    ram=simbase.sim51.RAM
    arr=np.array(ram)
    newarr=np.array_split(arr,32)
    for i in range(32):
        adrs.append(hex(i*8))
    np.array(adrs)
    ram=np.insert(newarr,0,adrs,axis=1)
    temp_ram=np.array(ram)
    
    if not (temp_ram==last_ram).all():#ram内容发生变化
        dif=np.where(temp_ram!=last_ram)#找出变化位置
        dif_cor=np.where(dif[1]!=0)
        x=(dif[0][dif_cor]).tolist()
        y=(dif[1][dif_cor]).tolist()
        for i in range(len(x)):
            colr_flag[x[i]][y[i]-1]=1
    last_ram=ram
    #前8个数代表ram值，后8个数代表是否发生变化
    context['ram']=np.hstack((ram,colr_flag))
    context['sfr_keys']=list(sfr_keys)
    context['sfr_values']=sfr_value
    context['code']=simbase.sim51.web_code
    context['error_massage']=simbase.sim51.error_msg
    #context['colr_flag']=colr_flag
    return render(request, "post.html", context)
