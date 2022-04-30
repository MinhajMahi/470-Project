from django.test import  TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage


_views = __import__("MVC Structure.Controller.views")
_views = _views.Controller.views

# from Model.models import User, Profile, BillingAddress
_models = __import__("MVC Structure.Model.models")
_models = _models.Model.models


class ViewsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = _models.User.objects._create_user(email="test@gmail.com",password="top_secret")
        self.category = _models.Category()
        self.category.title = "medicine"
        self.category.save()
        self.product = _models.Doctor()
        self.product.name = "Minhaj Mahi"
        self.product.category = self.category
        self.product.preview_text = "Studied from DMC"
        self.product.detail_text = "Renowned doctor with so much rewards."
        self.product.old_price = 120000
        self.product.price = 100000
        self.product.save()

        self.request = self.factory.get('/shop/add/1')
        self.request.user = self.user
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)
        self.response = _views.add_to_cart(self.request,1)


    def test_add_to_cart(self):

        cart = _models.Cart.objects.get(user=self.user)
        self.assertEqual(cart.quantity, 1,)

        self.response = _views.add_to_cart(self.request,1)
        self.response = _views.add_to_cart(self.request,1)
        self.response = _views.add_to_cart(self.request,1)

        cart = _models.Cart.objects.get(user=self.user)


        self.assertEqual(cart.quantity, 4, )
        self.assertFalse(cart.purchased, "Purchased should be false by default.")
        self.assertEqual(cart.item.name, "Minhaj Mahi", "Studied from DMC")



    def test_remove_from_cart(self):
        request = self.factory.get('/shop/remove/1')
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response = _views.remove_from_cart(request,1)
        order_item = _models.Cart.objects.filter(item=self.product, user=request.user, purchased=False)

        self.assertEqual(response.status_code, 302, "Should get a successfull response.")
        self.assertEqual(len(order_item), 0 , "Cart should be remove from order")
