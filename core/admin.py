from django.contrib import admin
from .models import *

admin.site.register(TimePeriod)
admin.site.register(Account)
admin.site.register(GeneralMembershipFee)
admin.site.register(GeneralMembershipFeePhase)
admin.site.register(CustomMembershipFeePhase)
admin.site.register(SpecificSharingsMembershipPhase)
admin.site.register(ItemCategory)
admin.site.register(Item)
admin.site.register(Consumable)
admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(ConsumptionEstimation)
admin.site.register(Batch)
admin.site.register(User)
admin.site.register(Person)
admin.site.register(VirtualUser)
admin.site.register(Supplier)
admin.site.register(Unit)
admin.site.register(TransactionType) # hide
admin.site.register(Transaction)
admin.site.register(BatchTransaction)
admin.site.register(Taking)
admin.site.register(Restitution)
admin.site.register(Inpayment)
admin.site.register(Depositation)
admin.site.register(TranscriptionToBalance)
admin.site.register(Payout)
admin.site.register(Transfer)
admin.site.register(CostSharing)
admin.site.register(ProceedsSharing)
admin.site.register(Donation)
admin.site.register(Recovery)
admin.site.register(Credit)
admin.site.register(Purchase)
admin.site.register(SpecificPurchase)
admin.site.register(PurchaseStatusType) # hide
admin.site.register(PurchaseStatus)
admin.site.register(MoneyBoxType)
admin.site.register(MoneyBox)
admin.site.register(Currency)
# admin.site.register(MoneyBoxStock)
admin.site.register(Charge)
admin.site.register(GeneralOffer)
admin.site.register(Offer)
admin.site.register(VAT)