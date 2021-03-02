from django.db import models
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Customer(models.Model):
    phone= models.CharField(max_length=13,blank=True,null=True,
    validators=[
      RegexValidator(
        regex=r'^\+254\d{9}$',
        message="Phone number must be entered in the format '+254234567892'. Up to 12 digits allowed with no"
      ),
    ],
  )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code= models.CharField('code', max_length=15)
    # https://stackoverflow.com/questions/19130942/whats-the-best-way-to-store-phone-number-in-django-models
    
    def __str__(self):
        return self.user.email
    



class TimeStampedModel(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Order(TimeStampedModel):
    item = models.CharField('item',max_length=200 )
    amount = models.PositiveIntegerField()
    customer = models.ForeignKey('Customer',related_name='orders',on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ["-added"]




