from django.core.exceptions import ValidationError
import os


def allow_only_images_validator(value):

    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']

    if ext not in valid_extensions:
        raise ValidationError(
            f'Unsupported file extension: {ext}. Allowed types: {", ".join(valid_extensions)}')
