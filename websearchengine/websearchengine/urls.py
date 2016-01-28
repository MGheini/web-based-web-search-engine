
from django.conf.urls import include, url

urlpatterns = [
    # Examples:
    # url(r'^$', 'websearchengine.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'search.views.home'),
    url(r'^search/', 'search.views.retrieve'),
]
