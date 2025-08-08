from logging import getLogger
from django.shortcuts import render
from .models import DerbyName

logger = getLogger(__name__)


def index(request):
    names = DerbyName.objects.order_by("?").all()[:10]  # Get 10 random DerbyNames
    logger.info(f"Rendering index with {len(names)} names.")
    logger.debug(f"Names: {[name.name for name in names]}")
    return render(request, "names/index.html", {"names": names})
