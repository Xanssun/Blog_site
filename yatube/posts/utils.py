from django.core.paginator import Paginator

from .constants import POSTS_NUMBER


def paginate_page(request, post_list):
    paginator = Paginator(post_list, POSTS_NUMBER)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
