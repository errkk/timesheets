from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'grindstone.views.home', name='home'),
    url(r'^login/$', 'grindstone.views.loginpage', name='login'),
    url(r'^logout/$', 'grindstone.views.logoutpage', name='logout'),
    url(r'^gs/', include('grindstone.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
