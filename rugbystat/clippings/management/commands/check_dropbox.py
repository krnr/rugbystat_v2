import os
import logging

from django.conf import settings
from django.core.management import BaseCommand

from clippings.utils import process_user


logger = logging.getLogger("django.request")
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):
    def handle(self, *args, **options):
        os.chdir(settings.BASE_DIR)
        uid = None
        locks = [file for file in os.listdir() if ".lock" in file]
        logger.debug("Got following locks in dir: {}".format(locks))
        if locks:
            filename = locks[0]
            uid = int(filename.split(".")[0])
            logger.debug("Removing lock {}".format(filename))
            os.remove(filename)
        process_user(uid)
