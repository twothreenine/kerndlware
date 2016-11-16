from django.contrib import admin
from .models import Account, Item, Consumable, Product, Batch, Person, VirtualUser, Supplier, Unit, Transaction, Taking, Restitution, Inpayment, Depositation, MoneyBox, Currency

admin.site.register(Account)
admin.site.register(Item)
admin.site.register(Consumable)
admin.site.register(Product)
admin.site.register(Batch)
admin.site.register(Person)
admin.site.register(VirtualUser)
admin.site.register(Supplier)
admin.site.register(Unit)
admin.site.register(Transaction)
admin.site.register(Taking)
admin.site.register(Restitution)
admin.site.register(Inpayment)
admin.site.register(Depositation)
admin.site.register(MoneyBox)
admin.site.register(Currency)