from multiprocessing import context
from random import randint
from re import L
import re
from django.http import HttpResponse
from django.db import IntegrityError
from django.shortcuts import render,redirect 
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.hashers import check_password
from .models import Precinct, User,Voter,Admin,Repre, Faci
from .forms import CreateUserForm
from django.contrib import messages
# Create your views here.
def home_view(request,*args,**kwargs):
    user=request.user
    full_name=''
    if user.is_authenticated:
        full_name=user.first_name+" "+user.last_name
    return render(request,"base.html",{'user':user, 'name':full_name})

def profile_view(request,*args,**kwargs):
    user=request.user
    full_name=''
    if not user.is_authenticated:
        return redirect('Home')
    if user.is_voter:
        name=Voter.objects.get(user=user)
        full_name=name.user.first_name+" "+name.user.last_name
        precinct=Precinct.objects.get(pNum=name.pNum)
        print(precinct)
        return render(request,"profile.html",{'user':user,'name':full_name, 'info':name,'pr':precinct})
    voters=Repre.objects.filter(user=user)
    print(user.username)
    rep=User.objects.values('first_name','last_name').get(username=user.username)
    full_name=rep['first_name']+" "+rep['last_name']
    pr=[]
    for vtr in voters:
        precinct=Precinct.objects.get(pNum=vtr.pNum)
        pr.append(precinct)
    info=zip(voters,pr)
    return render(request,"profile.html",{'user':user,'name':full_name, 'info':info})

def precinct_view(request,*args,**kwargs):
    a=randint(1,20)
    b=randint(0,30)
    user=request.user
    full_name=''
    if not user.is_authenticated:
        return redirect('Home')
    print("rep:",user.is_rep)
    print("faci:",user.is_faci)
    print("voter", user.is_voter)
    print("admin:",user.is_admin)
    full_name=user.first_name+" "+user.last_name
    return render(request,"precinct.html",{'name':full_name,"top5":["8:30 AM - 9:00 AM (30%)","7:30 AM - 8:00 AM(20%)","2:30 PM - 3:00 PM(15%)","8:00 AM - 8:30 AM(10%)","1:00 PM - 1:30 PM(5%)"],'v':a,'nv':b})
def redirectview(request,*args,**kwargs):
    r=redirect('Home')
    return r
def createacc_view(request,*args,**kwargs):

    User = request.user
    form = CreateUserForm()
    if request.method == 'POST':
        try:
            form = CreateUserForm(request.POST)
            if form.is_valid():
                p=request.POST
                print(p)
                address="{}, {}, {}, {}".format(p['street'],p['Barangay'],p['Municipality'],p['province'])
                new_user=form.save()
                v=Voter(user=new_user,mName=p['MiddleName'],pNum='1234abc', vId= '7016-1234abc-125XYZ', Add=address,contact=p['contact'])
                try:
                    v.save()
                except Exception:
                    messages.warning(request,"Invalid Registration.")
                    return redirect("creation")
                messages.success(request,"Account Created! Your username is "+p['first_name'].replace(" ", "").lower()+"."+p['last_name'].replace(" ", "").lower())
                return redirect("creation")
            else:
                messages.warning(request,"Invalid Registration.")
                return redirect("creation")
        except IntegrityError:
            messages.warning(request,"Invalid Registration.")
            return redirect("creation")
    else:
        return render(request,"createaccount.html", {'form':form})

def scheduling_view(request,*args,**kwargs):
    prec=Voter.objects.get(user=request.user).pNum
    reprevoters=Repre.objects.filter(pNum=prec,scheduled=True).values("scheduleddate")
    print(reprevoters)
    vvoters=Voter.objects.filter(pNum=prec,scheduled=True).values("scheduleddate")
    print(vvoters)
    for i in reprevoters:
        print(i["scheduleddate"])
    return render(request,"scheduling.html",{})
def pwrecovery_view(request,*args,**kwargs):
    return render(request,"pwrecovery.html",{})

def clang_view(request,*args,**kwargs):
    return render(request,"changelang.html",{})

def login_view(request,*args,**kwargs):
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        print(username,password)
        try:
            #user=User.objects.get(username=username)
            #if user is not None and (check_password(password, user.password) or password==user.password):
                #print("ok")
                #login(request,user)
                #return redirect("Home")
            #else:
                #messages.success(request,"Invalid Credentials")
                #return redirect("login")
            user=authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("Home")
            else:
                messages.success(request,"Invalid Credentials")
                return redirect("login")
        except User.DoesNotExist:
                messages.success(request,"Invalid Credentials")
                return redirect("login")
    else:
        return render(request,"login.html",{})
def logout_acc(request):
    logout(request)
    return redirect("Home")

def testview(request): #for testing of incorporated css and js files
    return render(request,"charts.html",{})

def markvotedview(request):
    user=request.user
    info=Voter.objects.get(user=user)
    
    context = {'user': user, 'info': info}
    return render(request, "markVoted.html", context)
def createFaciview(request,*args,**kwargs):
    User = request.user
    form = CreateUserForm()
    if request.method == 'POST':
        try:
            form = CreateUserForm(request.POST)
            if form.is_valid():
                s=request.POST
                print(s)
                address="{}, {}, {}, {}".format(s['street'],s['Barangay'],s['Municipality'],s['province'])
                new_user=form.savefaci()
                f=Faci(user=new_user, mName=s['MiddleName'], Add=address, pNum=s['pNum'])
                try:
                    f.save()
                except Exception:
                    messages.warning(request,"Invalid Registration.")
                    return redirect("createFaci")
                messages.success(request,"Account Created!  Your username is "+s['first_name'].replace(" ", "").lower()+"."+s['last_name'].replace(" ", "").lower())
                return redirect("createFaci")
            else:
                messages.warning(request,"Invalid Registration.")
                return redirect("createFaci")
        except IntegrityError:
            messages.warning(request,"Invalid Registration.")
            return redirect("createFaci")
    else:
        return render(request,"createFaci.html", {'form':form})
def createRepview(request,*args,**kwargs):
    User = request.user
    form = CreateUserForm()
    if request.method == 'POST':
        try:
            form = CreateUserForm(request.POST)
            if form.is_valid():
                q=request.POST
                print(q)
                address="{}, {}, {}, {}".format(q['street'],q['Barangay'],q['Municipality'],q['province'])
                new_user=form.saverep()
                r=Repre(user=new_user, mName=q['MiddleName'], vFname=q['first_name'], vLname=q['last_name'], Add=address, pNum='1234abc', vId= '7016-1234abc-125XYZ', contact=q['contact'])
                try:
                    r.save()
                except Exception:
                    messages.warning(request,"Invalid Registration.")
                    return redirect("createRep")
                messages.success(request,"Account Created! Your username is "+q['first_name'].replace(" ", "").lower()+"."+q['last_name'].replace(" ", "").lower())
                return redirect("createRep")
            else:
                messages.warning(request,"Invalid Registration.")
                return redirect("createRep")
        except IntegrityError:
            messages.warning(request,"Invalid Registration.")
            return redirect("createRep")
    else:
        return render(request,"createRep.html", {'form':form})

def createAdminview(request,*args,**kwargs):
    full_name=''
    user=request.user
    if not user.is_authenticated:
        return redirect('Home')
    full_name=user.first_name+" "+user.last_name
    return render(request,"createAdmin.html",{'name':full_name})

def faciVerifyview(request,*args,**kwargs):
    full_name=''
    user=request.user
    if not user.is_authenticated:
        return redirect('Home')
    full_name=user.first_name+" "+user.last_name
    return render(request,"faciVerify.html",{'name':full_name})

def notRegisteredview(request,*args,**kwargs):
    full_name=''
    return render(request,"notRegistered.html",{'name':full_name})

def repSchedview(request,*args,**kwargs):
    full_name=''
    user=request.user
    if not user.is_authenticated:
        return redirect('Home')
    full_name=user.first_name+" "+user.last_name
    return render(request,"repSched.html",{'name':full_name})