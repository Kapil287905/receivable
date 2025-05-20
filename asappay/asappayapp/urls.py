from django.urls import path
from . import views

urlpatterns = [
    path("",views.index,name="index"),
    path("singup/",views.singup,name="singup"),
    path("dashboard/",views.dashboard,name="dashboard"),
    path("profile/",views.profile,name="profile"),
    path("editprofile/<int:profileid>/", views.editprofile, name="editprofile"),
    path("account/",views.account,name="account"),
    path("transaction/",views.transaction,name="transaction"),
    path("userlogout/",views.userlogout,name="userlogout"),
    path("req_password/", views.req_password, name="req_password"),
    path("reset_password/<uemail>/", views.reset_password, name="reset_password"),
    path("accountview/", views.accountview, name="accountview"),
    path("accountdetail/<int:accountid>/", views.accountdetail, name="accountdetail"),
    path("editaccount/<int:accountid>/", views.editaccount, name="editaccount"),
    path("deleteaccount/<int:accountid>/", views.deleteaccount, name="deleteaccount"),
    path('accountview/', views.search_accounts, name='search_accounts'),
    path('invoice/<int:transactionid>/', views.invoice_view, name='invoice'),
    path('resend-email/<int:transactionid>/', views.resend_transaction_email, name='resend_email'),
    path("payment/", views.payment, name="payment"),
    path('payment_success/<int:transactionid>/', views.payment_success, name='payment_success'),
    path('payment_cancel/<int:transactionid>/', views.payment_cancel, name='payment_cancel'),
    
]