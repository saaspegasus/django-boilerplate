from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from apps.users.helpers import validate_profile_picture

MAX_FILE_SIZE = 5242880  # 5 MB, mirrors the limit in validate_profile_picture


def _image_file(name, size=10):
    return SimpleUploadedFile(name, b"x" * size)


class ValidateProfilePictureTest(SimpleTestCase):
    def test_valid_extensions(self):
        for name in ["photo.jpg", "photo.jpeg", "photo.png", "photo.tif", "photo.tiff", "photo.webp", "photo.bmp"]:
            with self.subTest(name=name):
                validate_profile_picture(_image_file(name))  # should not raise

    def test_extension_check_is_case_insensitive(self):
        validate_profile_picture(_image_file("photo.JPG"))
        validate_profile_picture(_image_file("photo.PnG"))

    def test_invalid_extensions(self):
        for name in ["photo.gif", "photo.svg", "script.exe", "photo", "photo.jpg.txt"]:
            with self.subTest(name=name), self.assertRaises(ValidationError):
                validate_profile_picture(_image_file(name))

    def test_file_at_size_limit_is_allowed(self):
        validate_profile_picture(_image_file("photo.jpg", size=MAX_FILE_SIZE))

    def test_file_over_size_limit_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_profile_picture(_image_file("photo.jpg", size=MAX_FILE_SIZE + 1))
