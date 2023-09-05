from rest_framework.pagination import PageNumberPagination

class WorkersListPagination(PageNumberPagination):
    page_size = 100