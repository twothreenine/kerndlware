from django.contrib import admin
from .models import Account, Batch, Transaction, Person, VirtualUser, Supplier, Unit

admin.site.register(Account)
admin.site.register(Batch)
admin.site.register(Transaction)
admin.site.register(Person)
admin.site.register(VirtualUser)
admin.site.register(Supplier)
admin.site.register(Unit)