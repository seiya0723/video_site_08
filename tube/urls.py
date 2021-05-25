from django.urls import path
from . import views


app_name = "tube"
urlpatterns =[
    path('', views.index, name="index"),

    #検索ページ
    path('search/', views.search, name="search"),

    # TIPS:<型:変数名>とすることでビューに変数を与えることができる
    #idをuuidにするので、intをuuidに変える。

    path('delete/<uuid:video_pk>/', views.delete, name="delete"),
    path('update/<uuid:video_pk>/', views.update, name="update"),


    path('single/<uuid:video_pk>/', views.single, name="single"),
    path('single_mod/<uuid:video_pk>/', views.single_mod, name="single_mod"),

    ##ランキングページ。DBからデータ抜き取って表示するだけ。GET文だけ
    path('rank/', views.rank, name="rank"),

    # 以下認証済みユーザー専用
    path('mypage/', views.mypage, name="mypage"),
    path('history/', views.history, name="history"),
    path('recommend/', views.recommend, name="recommend"),
    path('notify/', views.notify, name="notify"),
    path('mylist/', views.mylist, name="mylist"),
    path('upload', views.upload, name="upload"),
    path('config/', views.config, name="config"),

]
