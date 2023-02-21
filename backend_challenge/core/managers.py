

class HondaManager(models.Manager):
    def get_queryset(self):
        return super(HondaManager, self).get_queryset().filter(model='Honda')