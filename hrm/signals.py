from django.db.models.signals import post_save
from django.contrib.auth.models import User
from . import models
import smtplib
from django.core.mail import send_mail


def sendEmail(email, link):
    email_address = 'azikdevapps@gmail.com'
    email_password = 'czrdtzwexajkzvot'

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
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
    send_mail = True
    if created:
        employee = models.Employee.objects.create(
            user=instance, email=instance.email,
            username=instance.username
        )
        gen_link = models.GenLink.objects.create(employee=employee)
        print('http://127.0.0.1:8000/register/'+str(gen_link.link))
        link = f'http://127.0.0.1:8000/register/{gen_link.link}'
        if send_mail:
            sendEmail(instance.email, link)
            # try:
            #
            # except Exception:
            #     instance.delete()
            #     raise Exception()


post_save.connect(when_user_created, sender=User)
