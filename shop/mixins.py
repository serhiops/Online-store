from django.views.generic.base import ContextMixin, View
from .models import Category, MailingList

class BaseMixin(ContextMixin, View):

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active = True)
        context['cartSize'] = self.request.user.cartListUser.all().count() if self.request.user.is_authenticated else len(self.request.session.get('cart_pk_list', {}))
        context['unactivenewsletter'] = self.request.session.get('isInMailingList', False) or (
            self.request.user.is_authenticated and MailingList.objects.filter(email = self.request.user.email)
        )
        return context
