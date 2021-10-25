from django.db import models
from seller.models import Products
from django.contrib.auth.models import User


class Userdetails(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,default=None)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    mobile_number = models.CharField(max_length=15, blank=False)
    dob = models.DateField(blank=True, null=True)
    image = models.ImageField(default="default-avatar.png" ,upload_to="images",null=True, blank=True)

    def __str__(self):
        return self.first_name


class Cart(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    user = models.CharField(max_length=120)
    quantity=models.IntegerField(default=1)
    options = (("ordernotplaced", "ordernotplaced"),
               ("orderplaced", "orderplaced")
               )
    status = models.CharField(max_length=120, choices=options, default="ordernotplaced")


class Orders(models.Model):
    product=models.ForeignKey(Products,on_delete=models.CASCADE)
    user=models.CharField(max_length=120)
    address=models.CharField(max_length=250)
    options=(
        ("ordered","ordered"),
        ("packed","packed"),
        ("shipped","shipped"),
        ("delivered","delivered"),
        ("cancelled","cancelled")
    )
    status=models.CharField(max_length=120,choices=options,default="ordered")
    date=models.DateField(auto_now=True)

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    review = models.CharField(max_length=500)
    date = models.DateField(auto_now=True)