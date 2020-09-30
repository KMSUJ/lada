import logging

import flask_featureflags as feature
import threading

from copy import copy
from flask import current_app

from lada.constants import FEATURE_MULTITHREADING

log = logging.getLogger(__name__)


def run_async(function, deamon=True, **kwargs):
    app = current_app._get_current_object()

    if feature.is_active(FEATURE_MULTITHREADING):
        kwargs = copy(kwargs)
        kwargs["app"] = app

        threading.Thread(target=function, kwargs=kwargs, daemon=deamon).start()
    else:
        function(app=app, **kwargs)
