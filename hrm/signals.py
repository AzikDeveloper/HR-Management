from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User, Group
from . import models
import smtplib


def sendEmail(email, message):
    EMAIL_ADDRESS = 'azikdevapps@gmail.com'
    EMAIL_PASSWORD = 'czrdtzwexajkzvot'

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        subject = 'hi'
        body = message
        msg = f'Subject: {subject}\n\n{body}'
        smtp.sendmail(EMAIL_ADDRESS, email, msg)


def when_user_created(sender, instance, created, **kwargs):
    if created:
        employee = models.Employee.objects.create(
            user=instance, email=instance.email,
            username=instance.username
        )
        link = models.GenLink.objects.create(employee=employee)
        print('http://127.0.0.1:8000/register/'+str(link.link))
        message = f'http://127.0.0.1:8000/register/{link.link}'
        sendEmail(instance.email, message)


post_save.connect(when_user_created, sender=User)
