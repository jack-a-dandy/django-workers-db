from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import os
import uuid

class Position(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(verbose_name='Position', max_length = 100, unique=True)

    class Meta:
        db_table = 'positions'
        ordering = ('name',)

    def __str__(self):
        return self.name


def upload_path_handler(instance, filename):
    return os.path.join(settings.PHOTOS_DIR, str(uuid.uuid4())+'.'+filename.split('.')[1])

class Worker(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    first_name = models.CharField(verbose_name='First name', max_length = 50)
    last_name = models.CharField(verbose_name='Last name', max_length = 50)
    patronymic = models.CharField(verbose_name='Patronymic', max_length = 55)
    position = models.ForeignKey(Position, verbose_name='Position', null=False, on_delete=models.CASCADE, related_name='workers')
    recruitment_date = models.DateField(verbose_name='Recruitment date')
    salary = models.IntegerField(verbose_name='Salary')
    head = models.ForeignKey('self', verbose_name='Head', null=True, on_delete=models.DO_NOTHING, related_name='subordinates')
    photo = models.ImageField(verbose_name="Photo", null=True, blank=True, upload_to=upload_path_handler)

    class Meta:
        db_table = 'workers'
        constraints = (models.CheckConstraint(check=~models.Q(head=models.F('id')), name='worker_head_not_self'),)

    def save(self, *args, **kwargs):
        if self.pk:
            old_position = Worker.objects.get(id=self.id).position
            super().save(*args, **kwargs)
            if self.position != old_position and Worker.objects.filter(position=old_position).count() == 0:
                old_position.delete()
        else:
            super().save(*args, **kwargs)

    def has_subordinates(self):
        return self.subordinates.all().exists()

    def __str__(self):
        return "{} {} {} - {} (id:{})".format(self.last_name, self.first_name, self.patronymic, self.position.name, self.pk)


@receiver(models.signals.pre_delete, sender=Worker)
def change_head_of_subordinates(sender, instance, using, **kwargs):
    for i in sender.objects.filter(head=instance.id).iterator():
        i.head=instance.head
        i.save()

@receiver(models.signals.post_delete, sender=Worker)
def delete_useless_position(sender, instance, using, **kwargs):
    if sender.objects.filter(position=instance.position).count() == 0:
        instance.position.delete()