from django.contrib import admin
from django import forms
from .models import Transaction,UserProfile,Categories,SubCategories,Accountsc

# Register your models here.

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["userid", "gender", "dob", "mobile", "photo"]

admin.site.register(UserProfile, UserProfileAdmin)

class CategoriesAdmin(admin.ModelAdmin):
    list_display = ["name"]

admin.site.register(Categories, CategoriesAdmin)

class SubCategoriesAdmin(admin.ModelAdmin):
    list_display = ["name", "gender", "categories"]

admin.site.register(SubCategories, SubCategoriesAdmin)

class AccountscAdmin(admin.ModelAdmin):
    list_display=[
        "accountid",
        "accountname",
        "accountemailid",
        "accountphone",
        "accountpan",
        "accountgst",
        "accountcreatedate",
        "userid",
        "address",
        "city",
        "country",
        "pincode"

    ]
admin.site.register(Accountsc,AccountscAdmin)

class transactionAdmin(admin.ModelAdmin):
    list_display=[
        "transactionid",
        "userid",
        "transactionamount",
        'accountid',
        "transactioncreatedate",
        "transactionduedate",
        "transactionstatus",
        "razorpay_payment_id"
    ]
admin.site.register(Transaction,transactionAdmin)
