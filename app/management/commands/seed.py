from django.core.management.base import BaseCommand
from django.core.management import CommandError
from app import factories
from app import models
import random


class Command(BaseCommand):
    help = 'Seeds the database.'

    def add_arguments(self, parser):
        parser.add_argument('--workers',
                            default=10,
                            type=int,
                            help='The number of fake workers to create.')

        parser.add_argument('--levels',
                            default=5,
                            type=int,
                            help='The number of hierarchy levels.'
                            )

    def handle(self, *args, **options):
        if options['workers'] < 1 or options['levels'] < 1:
            raise CommandError("Values of arguments can't be less than 1.")
        if options['workers'] < options['levels']:
            raise CommandError("Levels can't be more than workers.")

        heads = []
        current = None
        for _ in range(options['levels']-1):
            current = factories.WorkerFactory.create(head=current)
            heads.append([current.id])
        factories.WorkerFactory.create(head=current)

        for _ in range(options['workers']-options['levels']):
            level = random.randint(0, options['levels']-1)
            if level == 0:
                heads[level].append(
                    factories.WorkerFactory.create(head=None).pk)
            elif level == options['levels']-1:
                factories.WorkerFactory.create(
                    head=models.Worker.objects.get(pk=random.choice(heads[level-1])))
            else:
                heads[level].append(factories.WorkerFactory.create(
                    head=models.Worker.objects.get(pk=random.choice(heads[level-1]))).pk)
