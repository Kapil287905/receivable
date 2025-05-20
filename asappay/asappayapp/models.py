from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.timezone import now
from .validators import validate_pan
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django_countries.fields import CountryField

# Create your models here.

class UserProfile(models.Model):
    userid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)
    type = (("Male", "Male"), ("Female", "Female"))
    gender = models.CharField(max_length=30, choices=type)
    dob = models.DateField(null=True, default=None)
    mobile = models.PositiveIntegerField()
    photo = models.ImageField(upload_to="images")

class Categories(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class SubCategories(models.Model):
    name = models.CharField(max_length=100)
    type = (("Male", "Male"), ("Female", "Female"), ("None", "None"))
    gender = models.CharField(max_length=30, choices=type, default=None, null=True)
    categories = models.ForeignKey(
        Categories, on_delete=models.SET_NULL, null=True, default=None
    )

    def __str__(self):
        return self.name

class Accountsc(models.Model):
    accountid = models.AutoField(primary_key=True)
    userid = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,default=None)
    accountname = models.CharField(max_length=100)
    accountemailid = models.EmailField()
    accountphone = PhoneNumberField()
    accountpan = models.CharField(max_length=10)
    accountgst = models.CharField(max_length=15)
    accountcreatedate = models.DateField()
    address = models.CharField(max_length=255, default='N/A')
    country = CountryField(null=True)
    city = models.CharField(max_length=100, null=True)
    pincode = models.CharField(max_length=10, default='000000')


class Transaction(models.Model):
    transactionid = models.AutoField(primary_key=True)
    userid = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,default=None,related_name='transactions_started')
    accountid = models.ForeignKey(Accountsc, on_delete=models.SET_NULL, null=True, default=None, related_name='transactions_received')    
    transactionamount = models.DecimalField(max_digits=10, decimal_places=2)
    transactioncreatedate = models.DateField()
    transactionduedate = models.DateField()
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    transactionstatus = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    razorpay_payment_id  = models.CharField(max_length=100, blank=True, null=True)
