from django.contrib import admin
from .models import Account, Batch, Taking, Person, VirtualUser, Supplier, Unit

admin.site.register(Account)
admin.site.register(Batch)
admin.site.register(Taking)
admin.site.register(Person)
admin.site.register(VirtualUser)
admin.site.register(Supplier)
admin.site.register(Unit)
