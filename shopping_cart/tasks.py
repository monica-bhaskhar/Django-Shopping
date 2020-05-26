from celery.decorators import task
from celery.utils.log import get_task_logger

from django.utils import timezone
logger = get_task_logger(__name__)
from shopping_cart.models import *
import datetime
from django.core.mail import send_mail
from Shopping.settings import EMAIL_HOST_USER
from django.template import loader


@task(name="send_feedback_email_task")
def send_feedback_email_task():
    # subject = "test"
    # messages = "trest"
    # to_email = "monicabhaskhar1995@gmail.com"
    # send_mail(subject,messages,EMAIL_HOST_USER,[to_email],fail_silently=False)

    logger.info("Saved image from Flickr")
    """sends an email when feedback form is filled successfully"""
    #logger.info("Sent feedback email")
    customer = Customer.objects.all()
    for c in customer:
        if Order.objects.filter(customer=c, complete=False).exists():
            order = Order.objects.get(customer=c, complete=False)
            # items = order.orderitem_set.all()
            date =  timezone.now() + datetime.timedelta(days=3)

            items = OrderItem.objects.filter(order=order,date_added__gt=date)
            if items:
                items = order.orderitem_set.all()
                name = c.name
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
                subject = 'Your Order is Pending'
                message = 'text version of HTML message'
                to_email = c.email    
                s=send_mail(subject,message,EMAIL_HOST_USER,[to_email],fail_silently=True,html_message=html_message)
                print(s,"SSSS")
            
    return None