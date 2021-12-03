from django.db.models.signals import post_save
from django.contrib.auth.models import User
from . import models
import smtplib
import socket


def sendEmail(email, link):
    email_address = 'azikdevapps@gmail.com'
    email_password = 'czrdtzwexajkzvot'

    with smtplib.SMTP(socket.gethostbyname('smtp.gmail.com'), 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(email_address, email_password)
        subject = 'hi dear new employee!'
        body = f"""
        Please fill out this form to register in our website:
        {link}
        Note that this link will be expired in 3 days!
        """
        msg = f'Subject: {subject}\n\n{body}'
        smtp.sendmail(email_address, email, msg)


def when_user_created(sender, instance, created, **kwargs):
    send_mail = False
    if created:
        attrs_needed = ['_section', '_group']
        if all(hasattr(instance, attr) for attr in attrs_needed):
            info = models.Info.objects.create(
                user=instance,
                section=instance._section
            )
            instance.groups.add(instance._group)
            instance.save()
            gen_link = models.GenLink.objects.create(user=instance)
            print('http://127.0.0.1:8000/register/' + str(gen_link.token))
            link = f'http://127.0.0.1:8000/register/{gen_link.token}'
            if send_mail:
                sendEmail(instance.email, link)


post_save.connect(when_user_created, sender=User)
