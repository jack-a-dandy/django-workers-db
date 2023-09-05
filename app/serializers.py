from rest_framework import serializers
from . import models


class TreeSerializer(serializers.ModelSerializer):
    position = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = models.Worker
        fields = ('id', 'first_name', 'last_name',
                  'patronymic', 'position', 'has_subordinates')
        read_only_fields = ('has_subordinates', 'id')


class SlugRelatedGetOrCreateField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(**{self.slug_field: data})[0]
        except (TypeError, ValueError):
            self.fail('invalid')


class ListSerializer(serializers.ModelSerializer):
    position = SlugRelatedGetOrCreateField(
        slug_field='name', queryset=models.Position.objects.all())

    class Meta:
        model = models.Worker
        fields = '__all__'
        read_only_fields = ('id',)
