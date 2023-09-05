from django.test import TestCase
from .factories import WorkerFactory, PositionFactory
from .models import Worker, Position
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction


class WorkerModelTest(TestCase):

    def test_changing_head_of_subordinates(self):
        a = WorkerFactory.create(head=None)
        b = WorkerFactory.create(head=a)
        for i in range(3):
            WorkerFactory.create(head=b)
        objects = b.subordinates.all()
        b.delete()
        for i in objects:
            self.assertEquel(a, i.head)

    def test_useless_position_deletion(self):
        a = WorkerFactory.create(
            head=None, position=PositionFactory(name='aaaa'))
        b = WorkerFactory.create(head=None, position=a.position)
        c = WorkerFactory.create(
            head=None, position=PositionFactory(name='bbbb'))
        i = a.position.id
        b.delete()
        self.assertEqual(2, Position.objects.all().count(
        ), msg="Position was deleted after deletion of one object.")
        a.delete()
        self.assertRaises(ObjectDoesNotExist, Position.objects.get, id=i,
                          name="Position wasn't deleted after deletion of all related objects.")
        a = WorkerFactory.create(head=None, position=c.position)
        b = WorkerFactory.create(
            head=None, position=PositionFactory(name='dddd'))
        a.position = b.position
        a.save()
        self.assertEqual(2, Position.objects.all().count(),
                         msg="Position was deleted after update of one object.")
        i = c.position.id
        c.position = b.position
        c.save()
        self.assertRaises(ObjectDoesNotExist, Position.objects.get, id=i,
                          name="Position wasn't deleted after update of all related objects.")

    def test_head_self_reference(self):
        a = WorkerFactory.create(head=None)
        b = WorkerFactory.create(head=a)
        b.head = b
        with transaction.atomic():
            self.assertRaises(IntegrityError, b.save)
