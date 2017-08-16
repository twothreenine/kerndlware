"""kerndlware URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from core import views
from rest_framework import routers
from core.views import BatchViewSet

#router = routers.DefaultRouter()
#router.register(r'batches', BatchViewSet)

urlpatterns = [
    url(r'^$', views.index),
    url(r'^base$', views.base),
    url(r'^user_settings$', views.user_settings),
    url(r'^account_transactions$', views.account_transactions),
    url(r'^register_account$', views.register_account),
    url(r'^register_user$', views.register_user),
    url(r'^account_settings$', views.account_settings),
    url(r'^account_consumption$', views.account_consumption),
    url(r'^suppliers$', views.suppliers),
    url(r'^transactionlist$', views.transactionlist),
    url(r'^batchtransactiontable$', views.batchtransactiontable),
    url(r'^consumabletransactiontable$', views.consumabletransactiontable),
    url(r'^accountlist$', views.accountlist),
    url(r'^batchlist$', views.batchlist),
    url(r'^itemlist$', views.itemlist),
    url(r'^consumablelist$', views.consumablelist),
    url(r'^consumablelist_modify$', views.consumablelist_modify),
    url(r'^batches', views.batches),
    url(r'^currencies', views.currencies),
    url(r'^purchases', views.purchases),
    url(r'^admin/', admin.site.urls),
    #url(r'^', include(router.urls)),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
