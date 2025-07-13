from django.urls import path
from . import views
from . views import MyTokenObtainPairView


from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path("", views.Get_Route),
    path('register/', views.user_register_view, name="Create-User"),
    path('GetData/', views.GetData, name="getData"),
    path('user/me/', views.get_logged_in_user_data, name='get_logged_in_user_data'),
    path('CreateAccount/', views.register_user, name='create_account'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('transactionsCreate/',views.transaction, name="transactions_create"),
    path('get_transaction/',views.Get_transaction, name="get_transaction"),
    path("Receive_transaction/",views.Get_Receive_transaction, name="Receive_transaction"),
    path('send/',views.transfer_money, name="send_money"),
    path('current_balance',views.get_current_balance, name="current_balance"),
    path('find_accountNumber', views.find_account_by_number, name="find_account_number"),
    path('transaction_history',views.get_enhanced_transaction_history, name="get_history"),
    path("get_transfer_details", views.get_transfer_details),
    path("get_updated_user_data", views.get_updated_user_data)
]

