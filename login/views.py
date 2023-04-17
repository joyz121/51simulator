from django.contrib import auth
from django.shortcuts import render,redirect
from notifications.signals import notify
from django.contrib.auth.models import User
from .userform import userform,registerform
#登录
def login(request):
    if request.session.get('is_login',None):
        return redirect("/sim/")
    if request.method =="POST":
        login_form=userform(request.POST)
        message="用户名密码都需填写！"
        #用户名密码都不为空
        if login_form.is_valid():
            username= login_form.cleaned_data['username']
            password= login_form.cleaned_data['password']
            try:
                user=auth.authenticate(username=username,password=password)
                if user :
                    request.session['is_login']=True
                    request.session['user_name']=username
                    auth.login(request,user)
                    return redirect('/sim/')
                else:
                    message="密码错误！"
            except:
                message="用户名不存在！"
            return render(request,'login.html',locals())
    login_form=userform()
    return render(request,'login.html',locals())
#注册
def register(request):
    if request.method == "POST":
        register_form = registerform(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'register.html', locals())
            else:
                same_name_user = User.objects.filter(username=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'register.html', locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'register.html', locals())
 
                # 创建新用户
                new_user = User.objects.create_user(username=username,password=password1)

                return redirect('/login/')  # 自动跳转到登录页面
    register_form = registerform()
    return render(request, 'register.html', locals())
#登出
def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    request.session.flush()
    auth.logout(request)
    return redirect('/login/')

def my_notifications(request):
    context={}
    return render(request,'my_notification.html',context)
