from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from . import views
from . import viewsets

router = DefaultRouter()
router.register(r'^api/list', viewsets.ListViewSet, basename='api-list')

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='tree.html'), name="tree"),
    url(r'^tree$', TemplateView.as_view(template_name='tree.html'), name="tree"),
    path('api/tree/<int:id>/subordinates/', views.subordinates, name="api-tree"),
    url(r'^list$', login_required(TemplateView.as_view(
        template_name='list.html'), login_url="/auth"), name='list'),
    url(r'^auth$', views.auth, name="login"),
    url(r'^logout$', views.log_out, name="logout")
] + router.urls
