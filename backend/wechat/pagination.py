from rest_framework.pagination import PageNumberPagination


class WechatPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    # max_page_size = 10000


# class MPPagination(PageNumberPagination):
#     page_size_query_param = 'page_size'

