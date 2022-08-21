from datetime import date
from typing import Dict

from django.http.request import HttpRequest


def year(request: HttpRequest) -> Dict[str, int]:
    """Add current year in template."""
    return {'year': date.today().year}
