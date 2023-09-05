import factory
from . import models
import random
import os
from django.conf import settings

LOCALE = settings.LANGUAGE_CODE.split('-')[0]+'_'+settings.LANGUAGE_CODE.split('-')[1].upper()

factory.Faker._DEFAULT_LOCALE = LOCALE


class PositionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Position
        django_get_or_create = ('name',)

    name = factory.Faker('job')


class WorkerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Worker

    first_name = factory.Faker('first_name_male')
    last_name = factory.Faker('last_name_male')
    patronymic = factory.Faker('middle_name_male')
    position = factory.SubFactory('app.factories.PositionFactory')
    salary = factory.LazyFunction(lambda: round(random.randint(20000, 1000000)/1000)*1000)
    recruitment_date = factory.Faker('date', pattern="%Y-%m-%d", end_datetime=None)
    head = factory.SubFactory('app.factories.WorkerFactory')
    photo = factory.django.ImageField(height=100, width=100,
                                      color=factory.LazyFunction(
                                          lambda: "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]))
                                      )
