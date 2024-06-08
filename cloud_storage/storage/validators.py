import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 6:
            raise ValidationError(
                _("Пароль должен содержать не менее 6 символов."),
                code='password_too_short',
            )
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Пароль должен содержать хотя бы одну заглавную букву."),
                code='password_no_upper',
            )
        if not re.search(r'\d', password):
            raise ValidationError(
                _("Пароль должен содержать хотя бы одну цифру."),
                code='password_no_number',
            )
        if not re.search(r'[\W_]', password):
            # \W соответствует любому символу, который не является буквой, цифрой или подчеркиванием
            raise ValidationError(
                _("Пароль должен содержать хотя бы один специальный символ."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Пароль должен содержать не менее 6 символов, включать хотя бы одну заглавную букву, одну цифру и один специальный символ."
        )
