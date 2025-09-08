from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Количество сущностей, которое будет выведено на одной странице."""

    page_size = 4
    page_size_query_param = "page_size"
