from django.urls import path 

from user.View.user_view import (
    RefreshAccessTokenView,
    UserLoginAPIView,
    UserSignUpAPIView,
    UserLogoutAPIView

)

urlpatterns = [
    path('signup/', UserSignUpAPIView.as_view(), name='user-signup'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    path('logout/', UserLogoutAPIView.as_view(), name='user-logout'),
    path('refresh-token/', RefreshAccessTokenView.as_view(), name='refresh-access-token'),
    
]
