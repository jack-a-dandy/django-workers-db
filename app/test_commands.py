from django.test import TestCase
from django.core.management import call_command, CommandError
from .models import Worker


class SeedCommandTest(TestCase):
    def _checkLevel(self, head, level):
        if head.has_subordinates():
            level += 1
            maxl = level
            objects = head.subordinates.all()
            for i in objects:
                l = self._checkLevel(i, level)
                if l > maxl:
                    maxl = l
            level = maxl
        return level

    def test_generation(self):
        Workers = 1000
        Levels = 50
        call_command('seed', workers=Workers, levels=Levels)
        self.assertEqual(Workers, Worker.objects.count(),
                         msg="Count of workers is invalid.")
        maxl = 1
        for i in Worker.objects.filter(head=None):
            l = self._checkLevel(i, 1)
            if l > maxl:
                maxl = l
        self.assertEqual(Levels, maxl, msg="Count of levels is invalid.")

    def test_levels_below_one(self):
        self.assertRaises(CommandError, call_command,
                          'seed', workers=100, levels=0)

    def test_workers_below_levels(self):
        self.assertRaises(CommandError, call_command,
                          'seed', workers=5, levels=8)
