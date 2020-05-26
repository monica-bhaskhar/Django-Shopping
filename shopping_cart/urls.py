from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
	#Leave as empty string for base url
	path('', views.HomeAPIView.as_view(), name="home"),
	path('register', views.UserRegistrationAPIView.as_view(), name="register"),
	path('login', views.UserLoginAPIView.as_view(), name="login"),
	path('logout', views.logoutAPIView.as_view(), name="logout"),
	path('product/<int:pk>', views.ProductAPIView.as_view(), name="product"),
	path('cart/<int:product_id>/<str:action>', views.AddCartAPIView.as_view(), name="cart"),
	path('cart', views.AddCartAPIView.as_view(), name="cart-view"),
	path('wallet', views.WalletAPIView.as_view(), name="wallet"),
	path('checkout', views.CheckoutAPIView.as_view(), name="checkout"),
	path('process_order/', views.processOrder, name="process_order"),
	path('process_orderapi/', views.processOrderAPIView.as_view(), name="process_orderapi"),
	path('check', views.check, name="check"),

]
urlpatterns = format_suffix_patterns(urlpatterns)
