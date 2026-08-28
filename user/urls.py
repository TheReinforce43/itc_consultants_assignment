from django.urls import path 

from user.View.user_view import (
    RefreshAccessTokenView,
    UserLoginAPIView,
    UserLogoutAPIView,
    CreateAPIView

)

urlpatterns = [
    path('signup/', CreateAPIView.as_view(), name='user-signup'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    path('logout/', UserLogoutAPIView.as_view(), name='user-logout'),
    path('refresh-token/', RefreshAccessTokenView.as_view(), name='refresh-access-token'),
    
]
