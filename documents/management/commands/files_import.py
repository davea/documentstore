import logging
from hashlib import sha1

from django.core.management.base import LabelCommand, CommandError
from django.core.files import File
from django.contrib.auth import get_user_model

from documents.models import Document

log = logging.getLogger(__name__)


class Command(LabelCommand):
    user = None

    def add_arguments(self, parser):
        parser.add_argument(
            "username", type=str, help="The username to assign these documents to"
        )

        parser.add_argument(
            "--source",
            type=str,
            default="manual",
            dest="source",
            help="The source of these documents",
        )

        parser.add_argument("--force", action="store_true", default=False)
        super().add_arguments(parser)

    def handle(self, *args, **kwargs):
        self._set_user(**kwargs)
        super().handle(*args, **kwargs)

    def handle_label(self, filepath, **kwargs):
        with open(filepath, "rb") as f:
            file = File(f)
            filehash = sha1(file.read()).hexdigest()
            if (
                not kwargs["force"]
                and Document.objects.filter(owner=self.user, filehash=filehash).exists()
            ):
                msg = (
                    "This file ({}) already seems to have been imported. Please re-run "
                    "this command with the --force flag if you wish to import it again "
                    "as a new Document. Any files given to this run of the command "
                    "up until this point *have* been imported, so re-running with the same "
                    "file list and the --force flag will result in more duplicates than you "
                    "probably expect."
                )
                raise CommandError(msg.format(filepath))
            document = Document.objects.create(
                owner=self.user, file=file, filehash=filehash, source=kwargs["source"]
            )
        log.debug("Created Document id {} from {}".format(document.id, filepath))

    def _set_user(self, **kwargs):
        UserModel = get_user_model()
        try:
            self.user = UserModel.objects.get(username=kwargs["username"])
        except UserModel.DoesNotExist:
            raise CommandError(
                "User with username '{}' doesn't exist.".format(kwargs["username"])
            )
