from django.http import HttpRequest, JsonResponse
from .models import Review, Product, MailingList
from django.views.generic import View
from django.core import serializers
import json

class ReviewApi(View):

    def post(self, request : HttpRequest, *args, **kwargs) -> JsonResponse:
        type = request.POST['type'].upper()
        if type == 'CREATE':
            return self.create()
        if type == 'UPDATE':
            return self.update()
        if type == 'DELETE':
            return self.delete()

    def create(self) -> JsonResponse:
        review, create = Review.objects.get_or_create(author = self.request.user, 
                                                    product = Product.objects.get(pk = self.request.POST['productId']))
        if create: 
            review.text = self.request.POST['text']
            review.save(update_fields = ('text',))
        data = {
            'created' : create,
                'message' : 'Дякую за ваш коментар!' if create else 'Можна написати лише один коментар під кожний товар!',
                'time' : review.updated,
                'success' : True
            }
        return JsonResponse(data)

    def get(self, request : HttpRequest, *qrgs, **kwargs) -> JsonResponse:
        review = Review.objects.get(author = request.user, 
                                            product = request.GET['productId'])
        serializerReview = serializers.serialize('json', ( review, ))
        struct = json.loads(serializerReview)
        data = json.dumps(struct[0], ensure_ascii = False)
        return JsonResponse({ 'success' : True, 'review' : data,  })
    
    def update(self) -> JsonResponse:
        try:
            review = Review.objects.get(author = self.request.user, product = self.request.POST['productId'])
            review.text = self.request.POST['text']
            review.save(update_fields = ('text',))
        except Exception as _ex:
            return JsonResponse({ 'sucess' : False, })
        return JsonResponse({ 'sucess' : True })

    def delete(self) -> JsonResponse:
        try:
            Review.objects.get(author = self.request.user, product = self.request.POST['productId']).delete()
        except Exception as _ex:
            return JsonResponse({'success' : False, })
        return JsonResponse({'success' : True})

def addToMailingList(request : HttpRequest) -> JsonResponse:
    mail, create = MailingList.objects.get_or_create(email = request.POST.get('mail', ''))
    request.session['isInMailingList'] = create
    data = {
        'text' : 'Дякую, що підписалися на нашу розсилку!' if create else 'Ця пошта вже підписана на нашу розсилку!',
        'create' : create,
    } 
    return JsonResponse(data)
