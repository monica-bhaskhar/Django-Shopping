from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


# Create your models here.

class Customer(models.Model):


	user = models.OneToOneField(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)
	email = models.CharField(max_length=200)
	wallet_amount = models.FloatField(default=0)
	age = models.IntegerField(default=0)
	gender = models.CharField(max_length=10,choices=[('',''),('Male','Male'),('Female','Female')])


	def __str__(self):
		return self.name


def post_save_customer(sender, instance, created, *args, **kwargs):
	user_profile, created = Customer.objects.get_or_create(user=instance,name=instance.username,email=instance.email)



post_save.connect(post_save_customer, sender=User)	






class Product(models.Model):
	name = models.CharField(max_length=200)
	price = models.FloatField()
	digital = models.BooleanField(default=False)
	image = models.ImageField()

	def __str__(self):
		return self.name

	@property
	def imageURL(self):
		try:
			url = self.image.url
		except:
			url = ''
		return url

class Order(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
	date_ordered = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100)

	def __str__(self):
		return str(self.customer.name)+ " "+ str(self.complete)
		
	@property
	def shipping(self):
		shipping = False
		orderitems = self.orderitem_set.all()
		for i in orderitems:
			if i.product.digital == False:
				shipping = True
		return shipping

	@property
	def get_cart_total(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.get_total for item in orderitems])
		return total 

	@property
	def get_cart_items(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.quantity for item in orderitems])
		return total 

	@property
	def get_cart_total_discount(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.get_total for item in orderitems])
		disc = total * 0.1
		discount = total - disc
		return discount 

class OrderItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=0)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.product.name)+ " "+ str(self.quantity)	

	@property
	def get_total(self):
		total = self.product.price * self.quantity
		return total


    	

class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	address = models.CharField(max_length=200)
	city = models.CharField(max_length=200)
	state = models.CharField(max_length=200)
	zipcode = models.CharField(max_length=200)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address