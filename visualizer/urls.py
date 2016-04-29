from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^run/$', views.run_tests),
    url(r'^run/(?P<test_path>.*)$', views.run_tests),
]
