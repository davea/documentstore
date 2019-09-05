import os
from io import BytesIO
from tempfile import TemporaryDirectory
import logging
from hashlib import sha1

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from dropbox import Dropbox

from documents.models import Document

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for config in settings.DROPBOX["users"]:
            user = self.get_user(config["username"])
            dropbox = Dropbox(config["auth_token"])
            for folder in config["folders"]:
                log.debug(folder)
                for entry in dropbox.files_list_folder(folder["path"]).entries:
                    if Document.objects.filter(
                        owner=user,
                        source="Dropbox import",
                        source_metadata__dropbox_id=entry.id,
                    ).exists():
                        log.debug("File already imported.")
                        continue

                    log.debug("File didn't exist, creating")
                    with TemporaryDirectory() as tmppath:
                        filepath = os.path.join(tmppath, entry.name)
                        dropbox.files_download_to_file(filepath, entry.path_display)
                        with open(filepath, "rb") as f:
                            file = File(f)
                            filehash = sha1(file.read()).hexdigest()
                            if Document.objects.filter(
                                owner=user, filehash=filehash
                            ).exists():
                                raise CommandError(
                                    f"File already exists for {user.username} {entry.path_display}"
                                )
                            document = Document.objects.create(
                                owner=user,
                                file=file,
                                filehash=filehash,
                                tags=folder["tags"],
                                source="Dropbox import",
                                imported_ok=True,
                                source_metadata={"dropbox_id": entry.id},
                            )
                            document.file_thumbnail.generate()
                            log.debug(
                                f"Created Document id {document.id} from {entry.id} ({entry.path_display})"
                            )

    def get_user(self, username):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            raise CommandError(f"User {username} doesn't exist.")
