from django.shortcuts import render, redirect
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status
from .serializer import UserRegistrationSerializer,RegistrationSerializer, UserLoginSerializer, HomeProductSerializer, OrderSerializer, WalletSerializer, ShippingAddressSerializer
from rest_framework.response import Response
from rest_framework import renderers
from rest_framework.authtoken.models import Token
from .models import Product, Customer, Order, OrderItem, ShippingAddress
from rest_framework.generics import CreateAPIView, GenericAPIView, ListAPIView
import json
import datetime
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login , logout, get_user_model
from django.core.mail import send_mail
from Shopping.settings import EMAIL_HOST_USER
from django.template import loader
from django.db.models import Q
from rest_framework import permissions, authentication
from .tasks import send_feedback_email_task
from django.contrib import messages







# Create your views here.
 
class UserRegistrationAPIView(APIView):
    renderer_classes = [renderers.JSONRenderer, renderers.TemplateHTMLRenderer]
    template_name = 'register.html'
    serializer_class = UserRegistrationSerializer
    
    def get(self, request, format=None):
        serializer = UserRegistrationSerializer()
        if request.accepted_renderer.format == "html":
            return Response({'serializer': serializer})
        else:
            return Response(serializer.data)    


    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if request.accepted_renderer.format == "html":
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                user = serializer.instance
                customer = Customer.objects.get(user=serializer.instance)
                customer.age = self.request.data.get('details.age')
                customer.gender = self.request.data.get('details.gender')
                customer.save()
                login(request, user)

                return redirect('home')
            else:
                messages.info(request, serializer.errors)

                return Response(
                    data=serializer.errors,
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )  
        else:
            details=request.data.pop("details")
            serializer = RegistrationSerializer(data=request.data)


            if serializer.is_valid(raise_exception=True):
                serializer.save()
                user = serializer.instance
                customer = Customer.objects.get(user=serializer.instance)
                customer.age = details.get('age')
                customer.gender = details.get('gender')
                customer.save()
                token, created = Token.objects.get_or_create(user=user)
                data = serializer.data
                data["token"] = token.key
                data['success'] = True
                login(request, user)

                return Response(data, status=status.HTTP_201_CREATED) 
            else:
                return Response(
                    data=serializer.errors,
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )          

class UserLoginAPIView(APIView):
    renderer_classes = [renderers.JSONRenderer, renderers.TemplateHTMLRenderer]
    template_name = 'login.html'
    serializer_class = UserLoginSerializer

    def get(self, request, format=None):
        if request.user.is_authenticated:
            return redirect('home')

        
        serializer = UserLoginSerializer()
        if request.accepted_renderer.format == "html":
            return Response({'serializer': serializer})
        else:
            return Response(serializer.data)
    

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if request.accepted_renderer.format == "html":
            if serializer.is_valid(raise_exception=True):
                user = serializer.user
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, serializer.errors)

                return Response(
                    data=serializer.errors,
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )  
        else:    
            if serializer.is_valid(raise_exception=True):
                user = serializer.user
                login(request, user)
                token, _ = Token.objects.get_or_create(user=user)
                data = serializer.data
                data["token"] = token.key
                return Response(data,status=status.HTTP_200_OK)
            else:
                return Response(
                    data=serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )

class logoutAPIView(APIView):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.JSONRenderer, renderers.TemplateHTMLRenderer]

    def get(self, request, format=None): 
        logout(request)
        if request.accepted_renderer.format == "html":
            return redirect('login')
        else:    
            data = {'success': 'Sucessfully logged out'}
            return Response(data=data, status=status.HTTP_200_OK) 


class HomeAPIView(ListAPIView):
    renderer_classes = [renderers.JSONRenderer, renderers.TemplateHTMLRenderer]
    template_name = 'home.html'
    serializer_class = HomeProductSerializer

    def get_queryset(self):
        return Product.objects.all()

    def list(self, request):
        # messages.info(request, 'You already own this ebook')

        cartItems = 0
        product_obj = False
        obj_product = False
        queryset = self.get_queryset()
        if request.user.is_authenticated:
            customer = request.user.customer
            pro_lst = []

            if Order.objects.filter(customer=customer, complete=False).exists():
                order = Order.objects.get(customer=customer, complete=False)
                items = order.orderitem_set.all()
                cartItems = order.get_cart_items
            
                if not items:
                    if Order.objects.filter(customer=customer, complete=True).order_by("-id").exists():
                        pre_order = Order.objects.filter(customer=customer, complete=True).order_by("-id")[0]
                        itmes = pre_order.orderitem_set.all()
                        for i in itmes:
                            if i.product.id not in pro_lst:
                                pro_lst.append(i.product.id)
            
            product_obj = Product.objects.filter(id__in=pro_lst)  

            other_lst = []
            pre_shop = Order.objects.filter(customer=customer) 
            if not pre_shop:
                above = int(customer.age) + 5
                below = int(customer.age) - 5
                cust = Customer.objects.filter(Q(age__gte=below)|Q(age__lte=above)).filter(gender=customer.gender)
                for c in cust:
                    if Order.objects.filter(customer=c, complete=True).order_by("-id").exists():
                        pr_order = Order.objects.filter(customer=c, complete=True).order_by("-id")[0]
                        pro = pr_order.orderitem_set.all()
                        for i in pro:
                            if i.product.id not in other_lst:
                                other_lst.append(i.product.id)
            
            obj_product = Product.objects.filter(id__in=other_lst) 
                


        if request.accepted_renderer.format == "html":
            return Response({'products':queryset, 'cartItems': cartItems, 'product_obj': product_obj, 'obj_product': obj_product})
        else:
            serializer = HomeProductSerializer(queryset, many=True)
            data = serializer.data
            val = {"cartItems": cartItems}
            data.append(val)
            return Response(data) 
                  
class ProductAPIView(APIView):
    renderer_classes = [renderers.JSONRenderer, renderers.TemplateHTMLRenderer]
    template_name = 'product_view.html'
    serializer_class = HomeProductSerializer

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        if request.accepted_renderer.format == "html":
            return Response({'products': product})
        else:
            serializer = HomeProductSerializer(product)
            return Response(serializer.data)



class AddCartAPIView(ListAPIView):
    # authentication_classes = [authentication.TokenAuthentication]
    renderer_classes = [renderers.JSONRenderer, renderers.TemplateHTMLRenderer]
    template_name = 'cart.html'
    serializer_class = OrderSerializer

    # def get_permission(self):
    #     print(self,"get_permission")
    #     if not request.accepted_renderer.format == "html":
    #         permission_classes = [permissions.IsAuthenticated]
    #         print(permission_classes,"permission_classes")
    #         return permission_classes


    def list(self, request, product_id=None, action=None):
        print(request.user.is_authenticated,"request.user.is_authenticated")
        print(request.user,"request.user")
        if not request.user.is_authenticated:
            return redirect('login')

        customer = request.user.customer

        if product_id == None:
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
        else:
            product = Product.objects.get(id=product_id)
            order, created = Order.objects.get_or_create(customer=customer, complete=False)

            orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

            if action == 'add':
                orderItem.quantity = (orderItem.quantity + 1)
            elif action == 'remove':
                orderItem.quantity = (orderItem.quantity - 1)

            orderItem.save()

            if orderItem.quantity <= 0:
                orderItem.delete()

        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

        product_lst = []
        for i in items:
            products = Product.objects.filter(name__contains=i.product.name).exclude(id=i.product.id)
            for p in products:
                if p.id not in product_lst:
                    product_lst.append(p.id)

        product_obj = Product.objects.filter(id__in=product_lst)            


        if request.accepted_renderer.format == "html":
            return Response({'cartItems':cartItems ,'order':order, 'items':items, 'product_obj':product_obj})
        else:
            serializer = OrderSerializer(order)
            data = serializer.data
            data['cartItems'] = cartItems
            return Response(data)
        

    
class WalletAPIView(APIView):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.JSONRenderer, renderers.TemplateHTMLRenderer]
    template_name = 'wallet.html'
    serializer_class = WalletSerializer

    def get(self, request, format=None):
        cartItems = 0
        customer = request.user.customer
        if  Order.objects.filter(customer=customer, complete=False).exists():
            order = Order.objects.get(customer=customer, complete=False)
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items

        serializer = WalletSerializer()
        if request.accepted_renderer.format == "html":
            return Response({'serializer': serializer, 'wallet': customer, 'cartItems': cartItems})
        else:
            data = serializer.data
            data['cartItems'] = cartItems
            return Response(data)


    def post(self, request, format=None):
        customer = Customer.objects.get(user=request.user)
        print(customer,"customer")
        serializer = WalletSerializer(customer, data=request.data)
        if request.accepted_renderer.format == "html":
            if serializer.is_valid(raise_exception=True):
                serializer.save(wallet_amount=self.request.data.get("wallet_amt"))

                return Response({'serializer' : serializer,  'wallet': customer})
            else:
                messages.info(request, serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:     
            if serializer.is_valid(raise_exception=True):
                serializer.save(wallet_amount=self.request.data.get("wallet_amt"))
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckoutAPIView(APIView):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.JSONRenderer, renderers.TemplateHTMLRenderer]
    template_name = 'checkout.html'
    serializer_class = OrderSerializer

    def get(self, request, format=None):
        if request.user.is_authenticated:
            customer = request.user.customer
            order = Order.objects.get(customer=customer, complete=False)
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items
            if request.accepted_renderer.format == "html":
                return Response({'cartItems':cartItems ,'order':order, 'items':items})
            else:
                serializer = OrderSerializer(order)
                data = serializer.data
                data['cartItems'] = cartItems
                return Response(data)
               
        else:
            return redirect('login')


def send_email(request, order):
    customer = request.user.customer
    items = order.orderitem_set.all()
    name = customer.name
    total = order.get_cart_total
    total_dsc = order.get_cart_total_discount
    
    html_message = loader.render_to_string(
            'payment_email.html',
            {
                'user_name': name,
                'total' : total,
                'total_dsc' : total_dsc,
                'items':  items,
                
            }
        )
    subject = 'Your Order Has Shipped'
    message = 'text version of HTML message'
    to_email = customer.email    
    send_mail(subject,message,EMAIL_HOST_USER,[to_email],fail_silently=True,html_message=html_message)

    
    return True
         


class processOrderAPIView(APIView):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.JSONRenderer]
    serializer_class = ShippingAddressSerializer

    def get(self, request, format=None):
        serializer = ShippingAddressSerializer()
        data = serializer.data
        data['option'] = "wallet/debit"         
        return Response(data)  

    def post(self, request, format=None):
        transaction_id = datetime.datetime.now().timestamp()
       
        if request.user.is_authenticated:
            customer = request.user.customer
            order = Order.objects.get(customer=customer, complete=False)
            total = order.get_cart_total_discount

            if self.request.data.get('option') == "wallet":
                wallet_val = int(customer.wallet_amount) - int(total)
                customer.wallet_amount = wallet_val
                customer.save()
       

        order.transaction_id = transaction_id

        if total == order.get_cart_total_discount:
            order.complete = True

        order.save()
        s=send_email(request, order)

        if order.shipping == True:
            serializer = ShippingAddressSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(customer=customer,order=order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)

    # data = json.loads(request)
    total = float(data['form']['total']) 

    if request.user.is_authenticated:
        customer = request.user.customer
        order = Order.objects.get(customer=customer, complete=False)
        if 'option' in data['form']:
            wallet_val = int(customer.wallet_amount) - int(total)
            customer.wallet_amount = wallet_val
            customer.save()

    else:
        return redirect("login")

    order.transaction_id = transaction_id

    if total == order.get_cart_total_discount:
        order.complete = True

    order.save()
    s=send_email(request, order)

    if order.shipping == True:
        ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)
    return JsonResponse('Payment submitted..', safe=False)    


def check(self):
    s=send_feedback_email_task.delay()
    return HttpResponse("Email send")
