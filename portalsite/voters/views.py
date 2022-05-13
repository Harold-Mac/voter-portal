from multiprocessing import context
from random import randint
from re import L
import re
from sched import scheduler
from django.http import HttpResponse
from django.db import IntegrityError
from django.shortcuts import render,redirect 
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.hashers import check_password
from .models import Precinct, User,Voter,Admin,Repre, Facis
from .forms import CreateUserForm
from django.contrib import messages
# Create your views here.
def home_view(request,*args,**kwargs):
    user=request.user
    full_name=''
    is_scheduled=False
    sched="Not Yet Scheduled"
    voted=False
    pNum = "abc"
    if user.is_authenticated:
        full_name=user.first_name+" "+user.last_name
        if user.is_voter:
            s=Voter.objects.get(user=user)
            is_scheduled=s.scheduled
            sched=s.scheduleddate
            voted=s.has_voted
        elif user.is_rep:
            s=Repre.objects.filter(user=user)
            b=s.filter(has_voted=True).count()
            c=s.filter(scheduled=True).count()
            sched="{} out of {} scheduled".format(c,s.count())
            voted="{} out of {} scheduled".format(b,s.count())
            is_scheduled=True
        elif user.is_faci:
            s=Facis.objects.get(user=user)
            pNum=s.pNum
    return render(request,"base.html",{'user':user, 'name':full_name,"sch":is_scheduled, 'voted':voted, "sched":sched, "pNum":pNum})

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
    user=request.user
    full_name=''
    if not user.is_authenticated:
        return redirect('Home')
    if user.is_voter:
        us=Voter.objects.get(user=user).pNum
        vv=Voter.objects.filter(pNum=us).values("has_voted")
        rp=Repre.objects.filter(pNum=us).values("has_voted")
        print(vv,rp)
    voted=0
    for i in range(len(vv)):
        if vv[i]["has_voted"]:
            voted+=1
    for i in range(len(rp)):
        if rp[i]["has_voted"]:
            voted+=1
    full_name=user.first_name+" "+user.last_name
    return render(request,"precinct.html",{'name':full_name,"top5":["8:30 AM - 9:00 AM (30%)","7:30 AM - 8:00 AM(20%)","2:30 PM - 3:00 PM(15%)","8:00 AM - 8:30 AM(10%)","1:00 PM - 1:30 PM(5%)"],'v':voted,'nv':len(vv)+len(rp)-voted})
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
    if request.method=="POST":
        vote=Voter.objects.get(user=request.user)
        vote.scheduleddate=request.POST["selectedSched"]
        vote.forscheduling=True
        vote.save()
        return redirect("Home")
    schedules=["7:00 AM","7:30 AM", "8:00 AM","8:30 AM", "9:00 AM","9:30 AM", "10:00 AM","10:30 AM", "11:00 AM","11:30 AM", "12:00 PM","12:30 PM", "1:00 PM","1:30 PM", "2:00 PM","2:30 PM", "3:00 PM","3:30 PM", "4:00 PM","4:30 PM", "5:00 PM","5:30 PM", "6:00 PM","6:30 PM","7:00 PM"]
    v=Voter.objects.get(user=request.user)
    prec=v.pNum
    reprevoters=Repre.objects.filter(pNum=prec,scheduled=True).values("scheduleddate")
    vvoters=Voter.objects.filter(pNum=prec,scheduled=True).values("scheduleddate")
    scheds=[]
    print(v.scheduled)
    for i in schedules:
        print(i)
        tots=reprevoters.filter(scheduleddate__startswith=i).count()+vvoters.filter(scheduleddate__startswith=i).count()
        print(tots)
        scheds.append(tots)
    return render(request,"scheduling.html",{"data":scheds,"stat":v.scheduled,"set":v.forscheduling})

def repOwnSched_view(request,*args,**kwargs):
    if request.method=="POST":
        vote=Repre.objects.get(user=request.user)
        vote.scheduleddate=request.POST["selectedSched"]
        vote.forscheduling=True
        vote.save()
        return redirect("Home")
    schedules=["7:00 AM","7:30 AM", "8:00 AM","8:30 AM", "9:00 AM","9:30 AM", "10:00 AM","10:30 AM", "11:00 AM","11:30 AM", "12:00 PM","12:30 PM", "1:00 PM","1:30 PM", "2:00 PM","2:30 PM", "3:00 PM","3:30 PM", "4:00 PM","4:30 PM", "5:00 PM","5:30 PM", "6:00 PM","6:30 PM","7:00 PM"]
    v=Repre.objects.get(user=request.user)
    prec=v.pNum
    reprevoters=Repre.objects.filter(pNum=prec,scheduled=True).values("scheduleddate")
    vvoters=Voter.objects.filter(pNum=prec,scheduled=True).values("scheduleddate")
    scheds=[]
    print(v.scheduled)
    for i in schedules:
        print(i)
        tots=reprevoters.filter(scheduleddate__startswith=i).count()+vvoters.filter(scheduleddate__startswith=i).count()
        print(tots)
        scheds.append(tots)
    return render(request,"repOwnSched.html",{"data":scheds,"stat":v.scheduled,"set":v.forscheduling})

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
                f=Facis(user=new_user, mName=s['MiddleName'], Add=address, pNum=s['pNum'])
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
    pnum=Facis.objects.get(user=user).pNum
    print(pnum)
    if request.method=="POST":
        req=request.POST["verify"]
        pnum=Facis.objects.get(user=user).pNum
        ck=User.objects.filter(username=req,is_voter=True)
        if ck.count()>0: #from voter table
            temp=ck[0]
            obj=Voter.objects.get(user=temp)
            obj.forscheduling=False
            obj.scheduled=True
            obj.save(update_fields=['forscheduling','scheduled'])
            return redirect("faciVerify")
        else:   #from repre
            ck=Repre.objects.filter(id=int(req))
            print(ck)
            obj=ck[0]
            obj.forscheduling=False
            obj.scheduled=True
            obj.save(update_fields=['forscheduling','scheduled'])
    Reprevoters=Repre.objects.filter(pNum=pnum,forscheduling=True)
    vvoters=Voter.objects.filter(pNum=pnum,forscheduling=True)
    print
    return render(request,"faciVerify.html",{'name':full_name,"rVoters":Reprevoters,"vVoters":vvoters})

def markvotedview(request):
    full_name=''
    user=request.user
    if not user.is_authenticated:
        return redirect('Home')
    full_name=user.first_name+" "+user.last_name
    pnum=Facis.objects.get(user=user).pNum
    if request.method=="POST":
        req=request.POST["voted"]
        pnum=Facis.objects.get(user=user).pNum
        ck=User.objects.filter(username=req,is_voter=True)
        if ck.count()>0: #from voter table
            temp=ck[0]
            obj=Voter.objects.get(user=temp)
            obj.has_voted=True
            obj.save(update_fields=['has_voted'])
            return redirect("markVoted")
        else:   #from repre
            ck=Repre.objects.filter(id=int(req))
            print(ck)
            obj=ck[0]
            obj.has_voted=True
            obj.save(update_fields=['has_voted'])
    Reprevoters=Repre.objects.filter(pNum=pnum,has_voted=False,scheduled=True)
    voter=Voter.objects.filter(pNum=pnum,has_voted=False,scheduled=True)

    return render(request, "markVoted.html", {'user': user, "rVoters":Reprevoters, 'vVoters': voter})

def notRegisteredview(request,*args,**kwargs):
    full_name=''
    return render(request,"notRegistered.html",{'name':full_name})

def repSchedview(request,*args,**kwargs):
    full_name=''
    user=request.user
    if not user.is_authenticated:
        return redirect('Home')
    if request.method=="POST":
        id=int(request.POST["voter"])
        if id>0:
            obj=Repre.objects.get(id=id)
            obj.forscheduling=True
            obj.scheduleddate=request.POST["selectedSched"]
            obj.save(update_fields=["forscheduling", "scheduleddate"])
    schedules=["7:00 AM","7:30 AM", "8:00 AM","8:30 AM", "9:00 AM","9:30 AM", "10:00 AM","10:30 AM", "11:00 AM","11:30 AM", "12:00 PM","12:30 PM", "1:00 PM","1:30 PM", "2:00 PM","2:30 PM", "3:00 PM","3:30 PM", "4:00 PM","4:30 PM", "5:00 PM","5:30 PM", "6:00 PM","6:30 PM","7:00 PM"]
    scheds=[0 for i in range(len(schedules))]
    names=[]
    repobj=Repre.objects.filter(user=user)
    unscheduled=repobj.filter(scheduled=False,forscheduling=False).values("vFname","mName","vLname","id")
    prec=repobj[0].pNum
    reprevoters=Repre.objects.filter(pNum=prec,scheduled=True).values("scheduleddate")
    vvoters=Voter.objects.filter(pNum=prec,scheduled=True).values("scheduleddate")
    if repobj.count()>0:
        for i in unscheduled:
            names.append([i["id"],"{} {}. {}".format(i["vFname"], i["mName"][0], i["vLname"])])
    for k in range(len(schedules)):
        i=schedules[k]
        tots=reprevoters.filter(scheduleddate__startswith=i).count()+vvoters.filter(scheduleddate__startswith=i).count()
        scheds[k]=tots
    full_name=user.first_name+" "+user.last_name
    return render(request,"repSched.html",{'name':full_name, "data":scheds,"voters":names})
def voterschedule(request):
    print(request.POST["sched"])
    return redirect("Home")