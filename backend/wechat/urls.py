from django.urls import path, re_path
from wechat import views

app_name = 'wechat'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('friends/', views.UserList.as_view(), name='friend_list'),
    path('friend/<puid>', views.UserUpdate.as_view(), name='friend_update'),
    path('mps/', views.MPList.as_view(), name='mp_list'),
    path('groups/', views.GroupList.as_view(), name='group_list'),
    path('messages/', views.MessageList.as_view(), name='messages'),
    re_path(r'^stream/(?P<channel>\w+)/$', views.SSE.as_view(), name="stream")
]