from rest_framework import serializers
# from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.utils.translation import ugettext_lazy as _
from .models import Product, Customer, Order, OrderItem, ShippingAddress, User

class UserFieldSerializers(serializers.Serializer):
    age = serializers.IntegerField(write_only=False)
    gender = serializers.ChoiceField(choices=[('',''),('Male','Male'),('Female','Female')],write_only=False)

class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(max_length=8,required=True,write_only=True,style={'input_type': 'password'})
   

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    # def validate_password(self, value):
    #     print(value,"value")
    #     r=password_validation.validate_password(value)
    #     print(r,"RR")
    #     return value     

    def validate(self, attrs):
        if attrs.get('username'):
            user_query = User.objects.filter(username=attrs.get('username')).exists()
            if user_query:
                raise serializers.ValidationError("Username Already Exist!")

        if attrs.get('email'):
            queryset = User.objects.filter(email=attrs.get('email')).exists()
            if queryset:
                raise serializers.ValidationError("Email Already Exist!")

        attrs['password'] = make_password(attrs['password'])
        return attrs 

    




class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(max_length=8,required=True,write_only=True,style={'input_type': 'password'})
    details = UserFieldSerializers()
   

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "details")

    # def validate_password(self, value):
    #     print(value,"value")
    #     r=password_validation.validate_password(value)
    #     print(r,"RR")
    #     return value     

    def validate(self, attrs):
        if attrs.get('username'):
            user_query = User.objects.filter(username=attrs.get('username')).exists()
            if user_query:
                raise serializers.ValidationError("Username Already Exist!")

        if attrs.get('email'):
            queryset = User.objects.filter(email=attrs.get('email')).exists()
            if queryset:
                raise serializers.ValidationError("Email Already Exist!")

        attrs['password'] = make_password(attrs['password'])
        return attrs 

    def create(self, validated_data):
        details_data = validated_data.pop("details")
        user = User.objects.create(**validated_data)

        return user

   

class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True,style={'input_type': 'password'})

    default_error_messages = {
        'inactive_account': _('User account is disabled.'),
        'invalid_credentials': _('Unable to login with provided credentials.'),
        'invalid_user' : _('Invalid User Email.')
    }

    def __init__(self, *args, **kwargs):
        super(UserLoginSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        query = User.objects.filter(email=attrs.get("email")).exists()
        if query:
            username = User.objects.get(email=attrs.get("email"))
            user_val = authenticate(username=username, password=attrs.get('password'))

            self.user = authenticate(username=username, password=attrs.get('password'))
            if self.user:
                if not self.user.is_active:
                    raise serializers.ValidationError(self.error_messages['inactive_account'])
                return attrs
            else:
                raise serializers.ValidationError(self.error_messages['invalid_credentials'])
        else:
            raise serializers.ValidationError(self.error_messages['invalid_user'])      

       
class HomeProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "image")


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("id", "quantity", "date_added", "product")
        depth = 1

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    order_item = OrderItemSerializer(many=True, source='orderitem_set')


    class Meta:
        model = Order
        fields = ("id", "date_ordered", "complete", "customer","order_item")


class WalletSerializer(serializers.ModelSerializer):

    wallet_amt = serializers.FloatField(min_value=0,default=0,label="Wallet Amount")

    class Meta:
        model = Customer
        fields = ("wallet_amt",)

    def validate(self, attrs):
        if attrs.get("wallet_amt") < 0:
            raise serializers.ValidationError("Negative Amout Should not be allowed")   
        return attrs  


class ShippingAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShippingAddress
        fields = ("id", "address", "city", "state", "zipcode")
