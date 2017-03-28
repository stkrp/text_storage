from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class NumericPageNumberPagination(PageNumberPagination):
    """ 
    Заменяет ссылки на предыдущую/следующую страницы номерами
    
    Ссылки на страницы перенесены в поле `links`.
    """
    def get_next(self):
        if not self.page.has_next():
            return None
        return self.page.next_page_number()

    def get_previous(self):
        if not self.page.has_previous():
            return None
        return self.page.previous_page_number()

    def get_paginated_response(self, data):
        return Response({
            'links': {
               'next': self.get_next_link(),
               'previous': self.get_previous_link(),
            },
            'next': self.get_next(),
            'previous': self.get_previous(),
            'count': self.page.paginator.count,
            'results': data,
        })
