from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('request/', views.document_request, name='document_request'),
    path('list/', views.certificate_requests, name='certificate_requests'),
    path('detail/<str:request_id>/', views.request_detail, name='request_detail'),
    path('barangay-clearance/', views.barangay_clearance_request, name='barangay_clearance_request'),
    path('residency/', views.brgy_residency_cert, name='brgy_residency_cert'),
    path('indigency/', views.brgy_indigency_cert, name='brgy_indigency_cert'),
    path('good-moral/', views.brgy_goodmoral_character, name='brgy_goodmoral_character'),
    path('business/', views.brgy_business_cert, name='brgy_business_cert'),
    path('payment/mode/<str:request_id>/', views.payment_mode_selection, name='payment_mode_selection'),
    path('payment/gcash/<str:request_id>/', views.gcash_payment, name='gcash_payment'),
    path('payment/counter/<str:request_id>/', views.counter_payment, name='counter_payment'),
    path('cancel/<str:request_id>/', views.cancel_request, name='cancel_request'),
]