from django.db import models
from accounts.models import Account

# Create your models here.

from django.db import models
from store.models import  Product, Variation

# Create your models here.
class Wishlist(models.Model):
    wishlist_id=models.CharField(max_length=50,blank=True)
    date_added= models.DateField(auto_now_add=True)

    def __str__(self):
        return self.wishlist_id

class WishlistItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.product
    