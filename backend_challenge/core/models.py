import string
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django.db import models
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from datetime import date
from django.contrib.auth.models import Group
from django.utils.crypto import get_random_string





# from django.db import models


# STATE_CREATED = "created"
# STATE_ = ""
# STATE_TO_AIRPORT = "to_airport"
# STATE_TO_HOTEL = "to_hotel"
# STATE_DROPPED_OFF = "dropped_off"


#     0 - created
#     1 - assigned
#     2 - on_the_way
#     3 - checked_in
#     4 - done
#     5 - this status is not in use
#     6 - accepted
#     7 - canceled
#     8 - rejected
#     9 - unacknowledged


# STATE_CHOICES = (
#     (STATE_REQUEST, STATE_REQUEST),
#     (STATE_WAITING, STATE_WAITING),
#     (STATE_TO_AIRPORT, STATE_TO_AIRPORT),
#     (STATE_TO_HOTEL, STATE_TO_HOTEL),
#     (STATE_DROPPED_OFF, STATE_DROPPED_OFF),
# )

# TRANSITIONS = {
#     STATE_REQUEST: [STATE_WAITING,],
#     STATE_WAITING: [STATE_REQUEST, STATE_TO_AIRPORT],
#     STATE_TO_AIRPORT: [STATE_TO_HOTEL, STATE_REQUEST],
#     STATE_TO_HOTEL: [STATE_DROPPED_OFF],
#     STATE_DROPPED_OFF: [],
# }


# class Pickup(models.Model):
#     __current_state = None

#     state = models.CharField(
#         max_length=20, choices=STATE_CHOICES, default=STATE_REQUEST
#     )

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.__current_state = self.state

#     def save(
#         self,
#         force_insert=False,
#         force_update=False,
#         using=None,
#         update_fields=None,
#     ):
#         allowed_next = TRANSITIONS[self.__current_state]

#         updated = self.state != self.__current_state
#         if self.pk and updated and self.state not in allowed_next:
#             raise Exception("Invalid transition.", self.state, allowed_next)

#         if self.pk and updated:
#             self.__current_state = self.state

#         return super().save(
#             force_insert=force_insert,
#             force_update=force_update,
#             using=using,
#             update_fields=update_fields,
#         )

#     def _transition(self, state):
#         self.state = state
#         self.save()

#     def assign(self, driver):
#         # we omit storing the driver on the model for simplicity of the example
#         self._transition(STATE_WAITING)

#     def accept(self):
#         self._transition(STATE_TO_AIRPORT)

#     def decline(self):
#         self._transition(STATE_REQUEST)

#     def picked_up(self):
#         self._transition(STATE_TO_HOTEL)

#     def dropped_off(self):
#         self._transition(STATE_DROPPED_OFF)
# class User(AbstractUser):
#     photo = models.ImageField(upload_to='photos', null=True, blank=True)

#     @property
#     def group(self):
#         groups = self.groups.all()
#         return groups[0].name if groups else None


# class Trip(models.Model):
#     REQUESTED = 'REQUESTED'
#     STARTED = 'STARTED'
#     IN_PROGRESS = 'IN_PROGRESS'
#     COMPLETED = 'COMPLETED'
#     STATUSES = (
#         (REQUESTED, REQUESTED),
#         (STARTED, STARTED),
#         (IN_PROGRESS, IN_PROGRESS),
#         (COMPLETED, COMPLETED),
#     )

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#     pick_up_address = models.CharField(max_length=255)
#     drop_off_address = models.CharField(max_length=255)
#     status = models.CharField(max_length=20, choices=STATUSES, default=REQUESTED)
#     driver = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         null=True,
#         blank=True,
#         on_delete=models.DO_NOTHING,
#         related_name='trips_as_driver'
#     )
#     rider = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         null=True,
#         blank=True,
#         on_delete=models.DO_NOTHING,
#         related_name='trips_as_rider'
#     )

#     def __str__(self):
#         return f'{self.id}'

#     def get_absolute_url(self):
#         return reverse('trip:trip_detail', kwargs={'trip_id': self.id})

# def get_or_assign_number(self):
#         if self.number is None:
#             epoch = datetime.now().date()
#             epoch = epoch.replace(epoch.year, 1, 1)
#             qs = Order.objects.filter(number__isnull=False, created_at__gt=epoch)
#             qs = qs.aggregate(models.Max('number'))
#             try:
#                 epoc_number = int(str(qs['number__max'])[4:]) + 1
#                 self.number = int('{0}{1:05d}'.format(epoch.year, epoc_number))
#             except (KeyError, ValueError):
#                 # the first order this year
#                 self.number = int('{0}00001'.format(epoch.year))
#         return self.get_number()

# def get_number(self):
#         return '{0}-{1}'.format(str(self.number)[:4], str(self.number)[4:])

def generate_secret():
   
    initial="API"
    code=get_random_string(length=8, allowed_chars=string.ascii_lowercase + string.digits)
    
    full_code=initial+code
    return full_code.upper()


driver_group, created = Group.objects.get_or_create(name='Doctor')

class TimeStampedModel(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        



class Customer(TimeStampedModel):
    phone = models.CharField(
        max_length=13,
        validators=[
            RegexValidator(
                regex=r"^\+254|07\d{9}$",
                message="Phone number must be entered in the format '+254234567892'. Up to 12 digits allowed with no",
            ),
        ],
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE,)
    code = models.CharField("code", max_length=15)

  
class Driver(TimeStampedModel):
    phone = models.CharField(
        max_length=13,
        validators=[
            RegexValidator(
                regex=r"^\+254\d{9}$",
                message="Phone number must be entered in the format '+254234567892'. Up to 12 digits allowed with no",
            ),
        ],
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE,)
    code = models.CharField("code", max_length=15)

  

    def __str__(self):
        return self.user.email
    def __str__(self):
        return self.user.email


class Order(TimeStampedModel):
    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_EXPIRED = "expired"
    STATUS_CANCELED = "cancelled"
    STATUS_CHOICE = (
        (STATUS_DRAFT, _("draft")),
        (STATUS_PENDING, _("pending")),
        (STATUS_PAID, _("paid")),
        (STATUS_EXPIRED, _("expired")),
        (STATUS_CANCELED, _("cancelled")),
    )
    Funiture = 'furniture'
    Electronics = 'electronics'
    Fashion = 'fashion'
    CATEGORY = [
       (Funiture, _('Furniture')),
       (Electronics, _('electronics')),
       (Fashion, _('fashion')),
   ]
    item = models.CharField("item", max_length=200)
    category= models.CharField(
        max_length=16,
        choices=CATEGORY,
        verbose_name=_("Category"),
        default="fashion"
    )
    amount = models.PositiveIntegerField()
    customer = models.ForeignKey(
        "Customer", related_name="orders", on_delete=models.CASCADE
    )
    

    code = models.CharField(
        max_length=16,
        verbose_name=_("Order code"),
        db_index=True,null=True
    )
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICE,
        verbose_name=_("Status"),
        db_index=True,
        default="draft"
    )
    # scheduled_at= models.DateTimeField()
    
    @staticmethod
    def normalize_code(code):
        tr = str.maketrans({
            '2': 'Z',
            '4': 'A',
            '5': 'S',
            '6': 'G',
        })
        return code.upper().translate(tr)
    
    def assign_code(self):
        # This omits some character pairs completely because they are hard to read even on screens (1/I and O/0)
        # and includes only one of two characters for some pairs because they are sometimes hard to distinguish in
        # handwriting (2/Z, 4/A, 5/S, 6/G). This allows for better detection e.g. in incoming wire transfers that
        # might include OCR'd handwritten text
        charset = list('ABCDEFGHJKLMNPQRSTUVWXYZ3789')
        iteration = 0
        # length = settings.ENTROPY['order_code']
        while True:
            code = get_random_string(length=16, allowed_chars=charset)
            iteration += 1
        return code 
        
        
    def save(self, **kwargs):
        if 'update_fields' in kwargs and 'last_modified' not in kwargs['update_fields']:
            kwargs['update_fields'] = list(kwargs['update_fields']) + ['last_modified']
        if not self.code:
            self.code=generate_secret()
            
    
        super().save(**kwargs)
           

       


    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ["-added"]
        
# CLONING
# blog = Blog(name='My blog', tagline='Blogging is easy')
# blog.save() # blog.pk == 1

# blog.pk = None
# blog._state.adding = True
# blog.save() # blog.p
# https://stackoverflow.com/questions/4733609/how-do-i-clone-a-django-model-instance-object-and-save-it-to-the-database

# from copy import deepcopy

# new_instance = deepcopy(object_you_want_copied)
# new_instance.id = None
# new_instance.save()

