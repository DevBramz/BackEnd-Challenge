
class ManagerEmpManager(models.Manager):

    def get_queryset(self):

        return super(ManagerEmpManager, self).get_queryset().filter(

            type='M')

    def create(self, **kwargs):

        kwargs.update({'type': 'M'})

        return super(ManagerEmpManager, self).create(**kwargs)

# Proxy Model

class ManagerEmployee(Employee):

    objects = ManagerEmpManager()

    class Meta:

        proxy = True

class HondaManager(models.Manager):
    def get_queryset(self):
        return super(HondaManager, self).get_queryset().filter(model='Honda')
# https://wellfire.co/learn/using-django-proxy-models/
# https://www.screamingatmyscreen.com/managing-state-in-django-models/
# https://semaphoreci.com/community/tutorials/testing-python-applications-with-pytest