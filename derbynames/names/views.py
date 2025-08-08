from logging import getLogger
from django.shortcuts import render
from django.db.models import Q

from .models import DerbyName, DerbyJersey

logger = getLogger(__name__)


def index(request):
    names = DerbyName.objects.order_by("?").all()[:10]  # Get 10 random DerbyNames
    logger.info(f"Rendering index with {len(names)} names.")
    logger.debug(f"Names: {[name.name for name in names]}")
    return render(request, "names/index.html", {"names": names})


def detail(request, name_id):
    name = DerbyName.objects.get(id=name_id)
    jersey = DerbyJersey.objects.filter(name=name).first()
    logger.info(f"Rendering detail for name: {name.name}")
    return render(request, "names/detail.html", {"name": name, "jersey": jersey})


def jersey_grid(request):
    # Select jerseys with images
    jerseys = (
        DerbyJersey.objects.filter(Q(image__isnull=False) & ~Q(image__exact=""))
        .order_by("?")
        .all()[:9]
    )  # Get 9 random DerbyJerseys
    logger.info(f"Rendering jersey grid with {len(jerseys)} jerseys.")
    logger.debug(f"Jerseys: {[jersey.name for jersey in jerseys]}")
    return render(request, "names/jersey_grid.html", {"jerseys": jerseys})
