import csv
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest,JsonResponse
from .models import Transaction,Accountsc,UserProfile
from django.template.loader import render_to_string
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout 
from django.core.exceptions import ValidationError
from .validators import validate_pan,validate_phone,validate_email
from django.utils import timezone
import re
import ssl
import smtplib
import certifi
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
import random
from django.contrib import messages
from email.message import EmailMessage
from django_countries import countries
from django.utils.dateparse import parse_date
from django.urls import reverse
from datetime import date, timedelta
from django.core.paginator import Paginator

# Create your views here.
print(certifi.where())

def index(req):
    if req.method == "GET":
        print(req.method) # GET
        return render(req,"index.html")
    else:
        uname=req.POST["uname"]
        uemail=req.POST["uemail"]
        upass=req.POST["upass"]
        print(upass,uname)
        # userdata=User.objects.filter(email=uemail,password=upass)
        userdata = authenticate(username=uname,email=uemail,password=upass)
        print(userdata)
        if userdata is not None:
            login(req,userdata)
            # return render(req, "dashboard.html")
            return redirect("dashboard")
        else:
            context = {}
            context["errmsg"] = "Invalid email or password"
            return render(req,"index.html",context)
        
def validate_password(password):
    if len(password) < 8 or len(password) > 128:
        raise ValidationError("Password must be atleast long and less than 128")
    has_upper=False
    has_lower=False
    has_digit=False
    has_special=False
    specialchars="@$!%?&"

    for char in password:
        if char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char.isdigit():
            has_digit = True
        elif char in specialchars:
            has_special = True

    print(has_upper)
    print(has_lower)
    print(has_digit)
    print(has_special)

    if not has_upper:
        raise ValidationError("Password must contain atleast one uppercase letter")
    elif not has_lower:
            raise ValidationError("Password must contain atleast one lowercase letter")
    if not has_digit:
            raise ValidationError("Password must contain atleast one digit letter")
    if not has_special:
            raise ValidationError("Password must contain atleast one special char (e.g. @$!%?&)")
    
    commonpassword=["password","123456","qwerty","abc123"]
    if password in commonpassword:
        raise ValidationError("This password is too common.please chose another one.")        

def singup(req):    
    if req.method == "GET":
        print(req.method) # GET
        return render(req,"regester.html")
    else:
        print(req.method) # POST
        uname=req.POST["uname"]
        uemail=req.POST["uemail"]
        upass=req.POST["upass"]
        ucpass=req.POST["ucpass"]
        print(uname,upass,ucpass,uemail)

        context = {}
        try:
            validate_password(upass)
        except ValidationError as e:
            context["errmsg"] = e.messages[0]
            return render(req,"regester.html",context) 
        if upass != ucpass:
            errmsg="Password and Confirm password nust be same"
            context = {"errmsg":errmsg}
            return render(req,"regester.html",context)
        elif uname == upass:
            errmsg="Password should not be same as email id"
            context = {"errmsg":errmsg}
            return render(req,"regester.html",context)
        else:
            try:
                userdata=User.objects.create(username=uname,email=uemail,password=upass)
                userdata.set_password(upass)
                userdata.save()
                print(User.objects.all())
                return redirect("index")
            except:
                errmsg="User already exist. Try with different username"
                context = {"errmsg":errmsg}
                return render(req,"regester.html",context)

def dashboard(req):
    alltransaction=Transaction.objects.all().order_by('-invoiceno').select_related('accountid')
    allaccounts = Accountsc.objects.all() 
    now = timezone.now()   
    username = req.user
    paginator = Paginator(alltransaction, 10)  # Show 10 per page
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(page_obj)
    return render(req, "home.html",{"username": username,"alltransaction":page_obj,"allaccounts":allaccounts,"now": now,'page_obj': page_obj })

def editprofile(req,profileid):
    profile=get_object_or_404(UserProfile,id=profileid)
    if req.method=="POST":
        profile.mobile=req.POST["mobile"]
        profile.gender=req.POST["gender"]
        profile.dob=req.POST["dob"]
        if req.FILES.get("photo"):
            profile.photo=req.FILES["photo"]
        profile.save()
        return redirect('profile')
    return render(req,'editprofile.html',{'userprofile':profile})

def req_password(request):
    if request.method == 'POST':
        uemail = request.POST.get("uemail")
        try:
            user = User.objects.get(email=uemail)
        except User.DoesNotExist:
            messages.error(request, "❌ No user found with that email.")
            return render(request, 'req_password.html')

        userotp = random.randint(1111, 999999)
        request.session["otp"] = userotp
        request.session["email"] = user.email  # optional, to access in next view

        sender = settings.EMAIL_HOST_USER
        password = settings.EMAIL_HOST_PASSWORD
        receiver = user.email

        msg = EmailMessage()
        msg.set_content(
            f"Hello, {user.username}\nYour OTP to reset password is: {userotp}\nThank you for using our services."
        )
        msg["Subject"] = "Forgot Password OTP for Reset Password"
        msg["From"] = sender
        msg["To"] = receiver

        context = ssl._create_unverified_context()

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls(context=context)
                server.login(sender, password)
                server.send_message(msg)
            return redirect("reset_password", uemail=user.email)
        except Exception as e:
            messages.error(request, f"❌ Failed to send email: {e}")
            return render(request, 'req_password.html')

    return render(request, 'req_password.html')


def reset_password(req, uemail):
    user = User.objects.get(email=uemail)
    print(user)
    if req.method == "POST":
        otp_entered = req.POST["otp"]
        upass = req.POST["upass"]
        ucpass = req.POST["ucpass"]
        userotp = req.session.get("otp")
        print(userotp, type(userotp))
        print(otp_entered, type(otp_entered), upass, ucpass)

        if int(otp_entered) != int(userotp):
            messages.error(req, "OTP does not match! Try Again.")
            return render(req, "reset_password.html", {"uemail": uemail})

        elif upass != ucpass:
            messages.error(req, "Confirm password and password do not match.")
            return render(req, "reset_password.html", {"uemail": uemail})

        else:
            try:
                validate_password(upass)
                user.set_password(upass)
                user.save()
                return redirect("/")
            except ValidationError as e:
                messages.error(req, str(e))
                return render(req, "reset_password.html", {"uemail": uemail})
    else:
        return render(req, "reset_password.html", {"uemail": uemail})

def profile(req):
    print(req.user)
    username = req.user
    user=req.user
    userprofile=UserProfile.objects.filter(userid=req.user).first()
    return render(req, "profile.html",{"username": username,"userid":user, "userprofile":userprofile})

def account(request):
    username = request.user
    context = {
        "username": username,
        "countries": list(countries)
    }

    if request.method == "GET":
        return render(request, "Account.html", context)

    # === Manual Form Submission ===
    if 'submit_manual' in request.POST:
        email = request.POST.get('aemail', '').strip()
        phone = request.POST.get('aphone', '').strip()

        # Validate the **required** fields
        try:
            validate_email(email)
            validate_phone(phone)
        except ValidationError as e:
            messages.error(request, e.messages[0])
            return redirect('account')

        # Build defaults dict only with non‑empty optional fields
        defaults = {
            'userid': request.user if request.user.is_authenticated else None,
            'accountcreatedate': timezone.now().date(),
        }
        # Optional fields
        for field_name, post_key in [
            ('accountname', 'aname'),
            ('accountpan', 'apannu'),
            ('accountgst', 'agstnu'),
            ('address', 'address'),
            ('country', 'country'),
            ('city', 'city'),
            ('pincode', 'pincode'),
        ]:
            val = request.POST.get(post_key, '').strip()
            if val:
                # validate PAN if that’s the field
                if field_name == 'accountpan':
                    try:
                        validate_pan(val)
                    except ValidationError as e:
                        messages.error(request, e.messages[0])
                        return redirect('account')
                defaults[field_name] = val

        # phone and email always go in defaults
        defaults['accountemailid'] = email
        defaults['accountphone'] = phone

        # Attempt to get or create
        account_obj, created = Accountsc.objects.get_or_create(
            accountemailid=email, 
            defaults=defaults
        )

        if created:      
            messages.success(request, "Account created with Email & Phone!")
        else:
            messages.info(request, "An account with this email already exists.")

        return redirect('account')


    # === CSV Upload ===
    if 'submit_csv' in request.POST and request.FILES.get('csvfile'):
        csv_file = request.FILES['csvfile']
        try:
            reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
        except Exception as e:
            messages.error(request, f"Error reading CSV: {e}")
            return redirect('account')

        created, skipped, errors = 0, 0, []
        for idx, row in enumerate(reader, start=1):
            email = row.get('email', '').strip().lower()  # normalize email
            phone = row.get('phone', '').strip()
            if not email or not phone:
                skipped += 1
                continue

            # Validate email and phone
            try:
                validate_email(email)
                validate_phone(phone)
            except ValidationError as e:
                errors.append(f"Row {idx}: {e.messages[0]}")
                continue

            # Check if account with this email already exists (case-insensitive)
            if Accountsc.objects.filter(accountemailid__iexact=email).exists():
                skipped += 1
                messages.info(request, f"An account with this {email} already exists.")
                continue

            defaults = {
                'userid': request.user if request.user.is_authenticated else None,
                'accountcreatedate': timezone.now().date(),
                'accountemailid': email,
                'accountphone': phone,
            }

            # Optional CSV fields
            if row.get('name', '').strip():
                defaults['accountname'] = row['name'].strip()
            if row.get('pan_number', '').strip():
                try:
                    validate_pan(row['pan_number'].strip())
                    defaults['accountpan'] = row['pan_number'].strip()
                except ValidationError as e:
                    errors.append(f"Row {idx}: {e.messages[0]}")
            # add more optional fields here as needed

            Accountsc.objects.create(**defaults)
            created += 1

        msg = f"Imported {created} new, skipped {skipped} rows."
        if errors:
            msg += " Errors: " + "; ".join(errors)
        messages.info(request, msg)
        return redirect('account')
    # Fallback
    return render(request, "Account.html", context)
       
def userlogout(req):
    logout(req)
    return redirect('/')

def accountview(req):
    allaccounts = Accountsc.objects.all()
    print(allaccounts)
    return render(
        req, "Accountview.html", {"allaccounts": allaccounts}
    )

def search_account(request):
    name = request.GET.get('accountname')
    createdate = request.GET.get('accountcreatedate')
    allaccounts = Accountsc.objects.all()
    if name:
        allaccounts = allaccounts.filter(accountname=name) if name else allaccounts
   
    if createdate:
         allaccounts = allaccounts.filter(accountcreatedate=createdate) if createdate else allaccounts

    context = {
        'allaccounts': allaccounts,            # For displaying
        'ajax': request.headers.get('x-requested-with') == 'XMLHttpRequest',
    }

    if context['ajax']:
        # Return partial HTML (only results section)
        html = render_to_string('Accountview.html', context, request=request)
        return HttpResponse(html)

    # Full page load
    return render(request, 'Accountview.html', context)

def search_transaction(request):
    name = request.GET.get('accountname')
    duedate = request.GET.get('transactionduedate')
    status = request.GET.get('transactionstatus')

    alltransaction = Transaction.objects.select_related('accountid').all()

    if name:
        alltransaction = alltransaction.filter(accountid__accountname__iexact=name)
    if duedate:
        alltransaction = alltransaction.filter(transactionduedate=duedate)
    if status:
        alltransaction = alltransaction.filter(transactionstatus=status)

    # Add pagination here
    paginator = Paginator(alltransaction.order_by('-invoiceno'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Build query string for pagination links
    filter_params = {
        "accountname": name,
        "transactionduedate": duedate,
        "transactionstatus": status,
    }
    query_string = "&" + "&".join(
        f"{key}={val}"
        for key, val in filter_params.items()
        if val
    )

    context = {
        'alltransaction': page_obj,
        'page_obj': page_obj,
        'query_string': query_string,
        'ajax': request.headers.get('x-requested-with') == 'XMLHttpRequest',
    }

    if context['ajax']:
        html = render_to_string('home.html', context, request=request)
        return HttpResponse(html)

    return render(request, 'home.html', context)

def accountdetail(req,accountid):
    accounts=Accountsc.objects.get(accountid=accountid)
    context={"accounts":accounts}
    return render(req, "Accountdetail.html",context)

def editaccount(request, accountid):
    accounts = get_object_or_404(Accountsc, accountid=accountid)

    if request.method == "POST":
        # update the *instance*, `accounts`
        accounts.accountname    = request.POST.get('aname',    accounts.accountname)
        accounts.accountemailid = request.POST.get('aemail',   accounts.accountemailid)
        accounts.accountphone   = request.POST.get('aphone',   accounts.accountphone)
        accounts.accountpan     = request.POST.get('apannu',   accounts.accountpan)
        accounts.accountgst     = request.POST.get('agstnu',   accounts.accountgst)
        accounts.address        = request.POST.get('address',  accounts.address)
        accounts.country        = request.POST.get('country',  accounts.country)
        accounts.city           = request.POST.get('city',     accounts.city)
        accounts.pincode        = request.POST.get('pincode',  accounts.pincode)

        accounts.save()

        # use the *instance* value here:
        return redirect('accountdetail', accountid=accounts.accountid)

    return render(request, 'Accountedit.html', {
        "accounts": accounts,
        "countries": list(countries)
    })

def deleteaccount(req,accountid):
    accounts = get_object_or_404(Accountsc, accountid=accountid)
    accounts.delete()
    return redirect('accountview')
   

def transaction(request):
    username   = request.user
    allaccount = Accountsc.objects.all()

    # GET: just render form(s)
    if request.method == "GET":
        return render(request, "receive.html", {
            "username": username,
            "allaccount": allaccount,
        })

    # POST: distinguish by which button was clicked
    # — single create uses name="submit_manual"
    if 'submit_manual' in request.POST:
        email   = request.POST.get('email', '').strip()
        amount  = request.POST.get('amount', '').strip()
        duedate = request.POST.get('duedate', '').strip()

        # Validate email
        try:
            validate_email(email)
        except ValidationError as e:
            messages.error(request, e.messages[0])
            return redirect('transaction')

        # Lookup account
        account = Accountsc.objects.filter(accountemailid__iexact=email).first()
        if not account:
            messages.error(request, "Account does not exist for this email.")
            return redirect('transaction')

        # Create transaction
        try:
            txn = Transaction.objects.create(
                userid=request.user,
                accountid=account,
                transactionamount=Decimal(amount),
                transactioncreatedate=timezone.now().date(),
                transactionduedate=duedate,
            )
        except Exception as e:
            messages.error(request, f"Error creating transaction: {e}")
            return redirect('transaction')

        # 4) Send email
        invoice_url = request.build_absolute_uri(
            reverse('invoice', kwargs={'transactionid': txn.transactionid})
        )
        sender = settings.EMAIL_HOST_USER
        password = settings.EMAIL_HOST_PASSWORD
        receiver = email

        msg = EmailMessage()
        msg.set_content(
            f"Thank you! A transaction of ₹{amount} was created.\n"
            f"Pay now: {invoice_url}"
        )
        msg["Subject"] = "Invoice for Your Transaction"
        msg["From"] = sender
        msg["To"] = receiver

        context = ssl._create_unverified_context()

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls(context=context)
                server.login(sender, password)
                server.send_message(msg)
            messages.success(request, f"✅ Transaction #{txn.invoiceno} created and email sent to {email}!")
            return redirect("transaction")
        except Exception as e:
            messages.error(request, f"❌ Failed to send email: {e}")
            return render(request, 'receive.html')

    # — bulk create uses name="submit_bulk"
    elif 'submit_bulk' in request.POST:
        ids      = request.POST.getlist('account_id[]')
        emails   = request.POST.getlist('email[]')
        amounts  = request.POST.getlist('amount[]')
        duedates = request.POST.getlist('duedate[]')

        created = 0
        for i, accountid in enumerate(ids):
            email   = emails[i].strip()
            amount  = amounts[i].strip()
            duedate = duedates[i].strip()

            # 1) Validate email
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, f"Invalid email: {email}")
                continue

            # 2) Lookup account
            account = Accountsc.objects.filter(accountemailid__iexact=email).first()
            if not account:
                messages.error(request, f"No account for ID {accountid}")
                continue

            # 3) Create transaction
            try:
                txn = Transaction.objects.create(
                    userid=request.user,
                    accountid=account,
                    transactionamount=Decimal(amount),
                    transactioncreatedate=timezone.now().date(),
                    transactionduedate=duedate,
                )
            except Exception as e:
                messages.error(request, f"Error creating txn for {email}: {e}")
                continue

            # 4) Send email
            invoice_url = request.build_absolute_uri(
                reverse('invoice', kwargs={'transactionid': txn.transactionid})
            )
            msg = EmailMessage()
            msg.set_content(
                f"Thank you! A transaction of ₹{amount} was created.\n"
                f"Pay now: {invoice_url}"
            )
            msg["Subject"] = "Invoice for Your Transaction"
            msg["From"]    = settings.EMAIL_HOST_USER
            msg["To"]      = email

            context = ssl._create_unverified_context()
            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls(context=context)
                    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                    server.send_message(msg)
            except Exception as e:
                messages.error(request, f"❌ Failed to send email to {email}: {e}")
                # but don't break—move on to next
            else:
                created += 1

        # Only after processing all rows:
        if created:
            messages.success(request, f"✅ {created} transactions created and emails sent.")
        return redirect('transaction')


    # Fallback
    return render(request, "receive.html", {
        "username": request.user,
        "allaccount": Accountsc.objects.all(),
    })


def resend_transaction_email(request, transactionid):
    txn = get_object_or_404(Transaction, transactionid=transactionid)
    email = txn.accountid.accountemailid
    amount = txn.transactionamount

    # Construct invoice URL
    invoice_url = request.build_absolute_uri(
        reverse('invoice', kwargs={'transactionid': txn.transactionid})
    )

    # Prepare Email
    sender = settings.EMAIL_HOST_USER
    password = settings.EMAIL_HOST_PASSWORD
    receiver = email

    msg = EmailMessage()
    msg.set_content(
        f"Thank you! A transaction of ₹{amount} was created.\n"
        f"Pay now: {invoice_url}"
    )
    msg["Subject"] = "Invoice for Your Transaction"
    msg["From"] = sender
    msg["To"] = receiver

    context = ssl._create_unverified_context()

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(sender, password)
            server.send_message(msg)
        messages.success(request, f"📧 Email re-sent to {email}")
    except Exception as e:
        messages.error(request, f"❌ Failed to resend email: {e}")

    return redirect('dashboard')  

from decimal import Decimal

def calculate_all_adjusted_amounts(amount):
    discount_2_percent = (amount * Decimal('0.98')).quantize(Decimal('0.01'))
    discount_1_percent = (amount * Decimal('0.99')).quantize(Decimal('0.01'))
    penalty_2_percent = (amount * Decimal('1.02')).quantize(Decimal('0.01'))

    return {
        'discount_2_percent': discount_2_percent,
        'discount_1_percent': discount_1_percent,
        'penalty_2_percent': penalty_2_percent,
    }    
        
def invoice_view(request, transactionid):
    transaction = get_object_or_404(Transaction, transactionid=transactionid)
    account = transaction.accountid 

    days_to_due = (transaction.transactionduedate - date.today()).days

    adjusted_amounts = calculate_all_adjusted_amounts(transaction.transactionamount)

    if days_to_due > 15:
        final_amount = adjusted_amounts['discount_2_percent']  # 2% discount
    elif 0 <= days_to_due <= 15:
        final_amount = adjusted_amounts['discount_1_percent']  # 1% discount
    else:
        final_amount = adjusted_amounts['penalty_2_percent']   # 2% penalty

    print(final_amount)

    amount_in_paise = int(final_amount * 100)  # convert to paise for Razorpay

    context = {
        "transaction": transaction,
        'discount_2_percent': adjusted_amounts['discount_2_percent'],
        'discount_1_percent': adjusted_amounts['discount_1_percent'],
        'penalty_2_percent': adjusted_amounts['penalty_2_percent'],
        "final_amount": final_amount,
        "account": account,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": amount_in_paise,
    }

    return render(request, 'invoice.html', context)

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import razorpay

@csrf_exempt
def payment(request):
    if request.method != "POST":
        return JsonResponse({"status": "invalid_method"}, status=405)

    try:
        data = json.loads(request.body)
        payment_id     = data.get("razorpay_payment_id")
        transaction_id = data.get("transaction_id")

        if not payment_id or not transaction_id:
            return JsonResponse({"status": "missing_data"}, status=400)

        client  = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment = client.payment.fetch(payment_id)

        # ————————————————
        # If Razorpay says the payment is good…
        if payment["status"] in ["authorized", "captured"]:
            # 1) Lookup your transaction row by your own transactionid
            txn = get_object_or_404(Transaction, transactionid=transaction_id)

            # 2) Update its fields
            txn.transactionstatus = "paid"              # ← here is where you change the status
            txn.razorpay_payment_id  = payment_id           # optional: store the Razorpay ID
            # you could also store:
            # txn.transactionamount   = payment["amount"] / 100
            # txn.transactiondate      = datetime.fromtimestamp(payment["created_at"])
            txn.save()  # ← persist the change to your transaction table

            # 3) Return the updated info back to the frontend
            return JsonResponse({
                "status":          "success",
                "transaction_id":  txn.transactionid,
                "amount":          payment["amount"],
                "payment_status":  payment["status"],
                "created_at":      payment["created_at"],
            })

        else:
            # Razorpay payment wasn’t in an OK state
            return JsonResponse({
                "status":         "fail",
                "payment_status": payment["status"]
            }, status=400)

    except Exception as e:
        # Something went wrong talking to Razorpay or your DB
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    

def payment_success(request, transactionid):
    txn = get_object_or_404(Transaction, transactionid=transactionid)
    messages.success(request, "Payment successful!")
    return render(request, 'success.html', {'transaction': txn})

def payment_cancel(request, transactionid):
    txn = get_object_or_404(Transaction, transactionid=transactionid)
    messages.success(request, "Payment Failed!")
    return render(request, 'cancel.html', {'transaction': txn})
