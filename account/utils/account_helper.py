from django.contrib.auth import get_user_model
from django.conf import settings
from django.template.loader import render_to_string
import requests


def email_or_mobile(value):
    UserModel = get_user_model()
    if settings.EMAIL_PATTERN.search(value):
        return {UserModel.EMAIL_FIELD: value}
    if settings.MOBILE_PATTERN.search(value):
        return {UserModel.USERNAME_FIELD: value}
    else:
        return {UserModel.USERNAME_FIELD: value}



def user_exists(**kwargs):
    model = get_user_model()
    try:
        user = model.objects.get(**kwargs)
    except model.DoesNotExist:
        return False
    return user


def verification_mail(user, token, time_validity):
    # token_message = _("SMAS OTP Verification {token}")
    # token_message = token_message.format(token=token)
    try:
        html_message = render_to_string(
            'mailer/verification.html',
            {'name': user.get_full_name().title(), 'otp': token, 'time_validity': time_validity})
        user.email_user("SMAS OTP Verification", None, "admin@smas.com", html_message=html_message)
    except Exception as ex:
        raise Exception('mail failed to sent due to {}'.format(ex))  # ex.args
    return True


def sent_sms(user, token, time_validity):
    try:
        data = settings.SMS_GETWAY[settings.SMS_GETWAY["DEFAULT"]]
        message = "{} is your SECRET One Time password for Login only valid for {} min"
        message = message.format(token, time_validity)
        url = data['url']
        data.pop('url')
        data.update({'message': message, 'numbers': user.mobile})
        response = requests.get(url, params=data)
        if response.status_code == 200:
            # msg = response.content
            return True
    except Exception as ex:
        raise Exception("sms failed to sent due to {}".format(ex))
    raise Exception("sms failed to sent")
