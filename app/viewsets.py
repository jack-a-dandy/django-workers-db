from rest_framework.viewsets import ModelViewSet
from .models import Worker, Position
from .serializers import ListSerializer
from .pagination import WorkersListPagination
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend, BooleanFilter
from django_filters import FilterSet, ModelChoiceFilter
from django.db.models import F
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework import status


class NullsFirstOrderingCustomFilter(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            f_ordering = []
            custom_fields = getattr(view, 'custom_ordering_fields', {})
            for o in ordering:
                symbol = o[0]
                o = o.lstrip('-')
                o = custom_fields.get(o, o)
                if symbol == '-':
                    f_ordering.append(F(o).desc(nulls_last=True))
                else:
                    f_ordering.append(F(o).asc(nulls_first=True))

            return queryset.order_by(*f_ordering)

        return queryset


class ListViewSetFilter(FilterSet):
    no_head = BooleanFilter(field_name='head', lookup_expr='isnull')
    position = ModelChoiceFilter(
        field_name="position__name", to_field_name='name', queryset=Position.objects.all())

    class Meta:
        model = Worker
        fields = ('position', 'first_name', 'last_name',
                  'patronymic', 'recruitment_date', 'salary', 'head')


class ListViewSet(ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = ListSerializer
    pagination_class = WorkersListPagination
    filter_backends = (DjangoFilterBackend,
                       NullsFirstOrderingCustomFilter, SearchFilter)
    filter_class = ListViewSetFilter
    ordering_fields = ('position', 'first_name', 'last_name',
                       'patronymic', 'id', 'recruitment_date', 'salary', 'head')
    search_fields = ('position__name', 'first_name',
                     'last_name', 'patronymic', 'recruitment_date')
    custom_ordering_fields = {'position': 'position__name'}
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError:
            content = {'head': 'Must be another worker or NULL.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
