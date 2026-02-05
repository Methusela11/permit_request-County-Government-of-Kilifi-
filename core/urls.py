from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginn, name='login'),
    path('home/', views.home, name='home'),
    path('noisepermit/', views.noisepermit, name='noisepermit'),
    path('submitpermit/', views.submitpermit, name='submitpermit'),
    path('thankyou/', views.thankyou, name='thankyou'),
    path('signup/', views.signup, name='signup'),
    path('permits/', views.permitss, name='permits'),
    path('treepermit/', views.treepermit, name='treepermit'),
    path('forestpermit/', views.forestpermit, name='forestpermit'),
    path('submit-payment/', views.submit_permit_payment, name='submit_permit_payment'),
    path('contact/', views.contact, name='contact'),
    path('clients/', views.clientss, name='clients'),
    path('requestednoisepermit/', views.requestednoisepermits, name='requestednoisepermits'),
    path('logout/', views.logout_view, name='logout'),
    path('readmore/', views.readmore, name='readmore'),
    path('check-approval/<str:id_number>/', views.check_approval, name='checkapproval'),
    path('permit/status/', views.check_permit_status, name='permitstatus'),
    path('report/', views.permit_report, name='report'),
]