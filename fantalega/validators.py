from django.core.exceptions import ValidationError
import re


def validate_season_name(name):
    pattern = '^\d{4}-\d{4}$'
    if not re.compile(pattern).match(name):
        raise ValidationError('name %s is not correct: yyyy-yyyy is mandatory'\
            % name, params={'name': name},)
