from django.shortcuts import render, HttpResponseRedirect,get_object_or_404,redirect
from django.urls import reverse
from django.http import HttpResponse
# Authentication
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate


# Import views
from django.views.generic import ListView, DetailView
# Mixin
from django.contrib.auth.mixins import LoginRequiredMixin
# Forms and Models
# from Model.models import Profile
_models = __import__("MVC Structure.Model.models")
_models = _models.Model.models
# from View.forms import ProfileForm, SignUpForm
_form = __import__("MVC Structure.View.forms.forms")
_form = _form.View.forms.forms

# For payment
# For payment
from django.views.decorators.csrf import csrf_exempt

# Messages
from django.contrib import messages

# **************APP LoGIN************

def sign_up(request):
    form = _form.SignUpForm()
    if request.method == 'POST':
        form = _form.SignUpForm(request.POST)
        print(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account Created Successfully!")
            return HttpResponseRedirect(reverse('login'))
    return render(request, 'App_Login/signup.html', context={'form':form})

def login_user(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You Are Logged in Successfully")
                return HttpResponseRedirect(reverse('home'))
    return render(request, 'App_Login/login.html', context={'form':form})

@login_required
def logout_user(request):
    logout(request)
    messages.warning(request, "You Are Logged Out!")
    return HttpResponseRedirect(reverse('home'))

@login_required
def user_profile(request):
    profile = _models.Profile.objects.get(user=request.user)

    form = _form.ProfileForm(instance=profile)
    if request.method == 'POST':
        form = _form.ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile Updated Successfully!')
            form = _form.ProfileForm(instance=profile)
    return render(request, 'App_Login/change_profile.html', context={'form':form})


#******************APP ORDER*******************


@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(_models.Doctor, pk=pk)
    order_item = _models.Appointment.objects.get_or_create(item=item, user=request.user, purchased=False)
    order_qs = _models.Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.orderitems.filter(item=item).exists():
            order_item[0].quantity += 1
            order_item[0].save()
            messages.info(request, "This item quantity was updated.")
            return redirect("home")
        else:
            order.orderitems.add(order_item[0])
            messages.info(request, "This item was added to your appointment list.")
            return redirect("home")
    else:
        order = _models.Order(user=request.user)
        order.save()
        order.orderitems.add(order_item[0])
        messages.info(request, "This item was added to your appointment list.")
        return redirect("home")

@login_required
def appointment_view(request):
    carts = _models.Appointment.objects.filter(user=request.user, purchased=False)
    orders = _models.Order.objects.filter(user=request.user, ordered=False)
    if carts.exists() and orders.exists():
        order = orders[0]
        return render(request, 'App_Order/cart.html', context={'carts':carts, 'order':order})
    else:
        messages.warning(request, "You don't have any item in your cart")
        return redirect("home")

@login_required
def  remove_from_cart(request, pk):
    item = get_object_or_404(_models.Doctor, pk=pk)
    order_qs = _models.Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.orderitems.filter(item=item).exists():
            order_item = _models.Appointment.objects.filter(item=item, user=request.user, purchased=False)[0]
            order.orderitems.remove(order_item)
            order_item.delete()
            messages.warning(request, "This doctor was removed from your appointment list.")
            return redirect('cart')
        else:
            messages.info(request, "This doctor was not in your appointment list")
            return redirect('home')
    else:
        messages.info(request, "You don't have an active appointment")
        return redirect("home")

#*************************APP Doctor*****************

@login_required
def checkout(request):
    saved_address = _models.BillingAddress.objects.get_or_create(user=request.user)
    saved_address = saved_address[0]
    form = _form.BillingForm(instance=saved_address)
    if request.method == 'POST':
        form = _form.BillingForm(request.POST, instance=saved_address)
        if form.is_valid():
            form.save()
            form = _form.BillingForm(instance=saved_address)
            messages.success(request, f"Shipping Address Saved!")
    order_qs = _models.Order.objects.filter(user=request.user, ordered=False)
    order_items = order_qs[0].orderitems.all()
    order_total = order_qs[0].get_total()
    return render(request, 'App_Payment/checkout.html', context={'form':form, 'order_items':order_items, 'order_total':order_total, 'saved_address':saved_address})


@login_required
def payment(request):
    saved_address = _models.BillingAddress.objects.get_or_create(user=request.user)
    saved_address = saved_address[0]
    if not saved_address.is_fully_filled():
        messages.info(request,f"Please complete your address!")
        return redirect("checkout")
    if not request.user.profile.is_fully_filled():
        messages.info(request, f"Please complete profile details.")
        return redirect("profile")
    status_url = request.build_absolute_uri(reverse('complete'))
    req= {'method':'POST','post':{'status':'VALID','tran_id': '435454', 'val_id':'3242432'}}
    complete(request, req)
    return HttpResponseRedirect(reverse('home'))


    

def complete(request, req=''):
    if req['method']== 'POST' or req['method'] =='post':
        payment_data = req['post']
        status = payment_data['status']
        if status == 'VALID':
            tran_id = payment_data['tran_id']
            val_id = payment_data['val_id']
            messages.success(request, f'Your Payment Completed Successfully! Page will be redirect after 5 sec..')
            return HttpResponseRedirect(reverse('purchase', kwargs={'val_id':val_id, 'tran_id':tran_id}))
        elif status == 'FAILED':
            messages.warning(request, f'Your Payment Failed! Pleaes Try Again!  Page will be redirect after 5 sec..')
    return render(request, 'App_Payment/complete.html', context={})
@login_required
def purchase(request, val_id, tran_id):
    order_qs = _models.Order.objects.filter(user=request.user, ordered=False)
    order = order_qs[0]
    order_id = tran_id
    order.ordered = True
    order.orderId = order_id
    order.paymentId = val_id
    order.save()
    cart_items = _models.Appointment.objects.filter(user=request.user, purchased=False)
    for item in cart_items:
        item.purchased = True
        item.save()
    return HttpResponseRedirect(reverse('home'))

@login_required
def order_view(request):
    try:
        orders = _models.Order.objects.filter(user=request.user, ordered=True)
        context = {'orders':orders}
    except:
        messages.warning(request, "You do not have an active order.")
        return redirect("home")
    return render(request,'App_Payment/order.html',context=context)

# *******************APP SHOP*********************
class Home(ListView):
    model = _models.Doctor
    template_name = 'App_Shop/home.html'

class DoctorDetail(LoginRequiredMixin, DetailView):
    model = _models.Doctor
    template_name = 'App_Shop/doctor_detail.html'
