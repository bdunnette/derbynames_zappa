"""
URL configuration for derbynames project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers, serializers, viewsets, permissions
from rest_framework.response import Response
from rest_framework.authtoken import views as token_views
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from derbynames.names.models import DerbyName
from derbynames.names.views import index, detail
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.info("Setting up URL configuration for derbynames project.")


# Serializers define the API representation.
class DerbyNameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DerbyName
        fields = ["id", "name"]


# ViewSets define the view behavior.
class DerbyNameViewSet(viewsets.ModelViewSet):
    queryset = DerbyName.objects.all()
    serializer_class = DerbyNameSerializer


# RandomDerbyName returns a random DerbyName.
class RandomDerbyNameView(viewsets.ModelViewSet):
    def get_queryset(self):
        return DerbyName.objects.order_by("?").first()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=False)
        return Response(serializer.data)

    # Override the default permission to allow unauthenticated access
    permission_classes = [permissions.AllowAny]
    # Use the same serializer as DerbyNameViewSet
    serializer_class = DerbyNameSerializer


class NameStartWithView(viewsets.ModelViewSet):
    serializer_class = DerbyNameSerializer

    def get_queryset(self):
        start_letter = self.kwargs.get("start_letter", "").lower()
        if start_letter:
            return DerbyName.objects.filter(name__istartswith=start_letter)
        return DerbyName.objects.none()

    # Override the default permission to allow unauthenticated access
    permission_classes = [permissions.AllowAny]


class NameContainsView(viewsets.ModelViewSet):
    serializer_class = DerbyNameSerializer

    def get_queryset(self):
        substring = self.kwargs.get("substring", "").lower()
        if substring:
            return DerbyName.objects.filter(name__icontains=substring)
        return DerbyName.objects.none()

    # Override the default permission to allow unauthenticated access
    permission_classes = [permissions.AllowAny]


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"names", DerbyNameViewSet)
router.register(r"random-name", RandomDerbyNameView, basename="random-name")
router.register(
    r"starts-with/(?P<start_letter>[a-zA-Z])",
    NameStartWithView,
    basename="name-start-with",
)
router.register(
    r"contains/(?P<substring>.+)", NameContainsView, basename="name-contains"
)


urlpatterns = [
    path("", index, name="index"),
    path("names/<int:name_id>/", detail, name="name-detail"),
    path("api/", include(router.urls)),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api-token-auth/", token_views.obtain_auth_token),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
