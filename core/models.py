from django.db import models
#from djmoney.models.fields import MoneyField
#from moneyed import Money, EUR
from .fields import PercentField
import datetime

class Currency(models.Model):
    name = models.CharField(max_length=10)
    conversion_rate = models.FloatField(default=1) # into anchor currency
    full_name = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    comment = models.TextField(blank=True)

class Role(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    comment = models.TextField(blank=True)

class User(models.Model):
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    comment = models.TextField(blank=True)
    accounts = models.ManyToManyField('Account', blank=True)

    def __str__(self):
        return "{} - {}".format(str(self.id), self.name)

class Person(User):
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    streetname = models.CharField(max_length=100, blank=True)
    streetnumber = models.SmallIntegerField(blank=True, null=True)
    zipcode = models.IntegerField(blank=True, null=True)
    town = models.CharField(max_length=100, blank=True)
    address_notice = models.TextField(blank=True)
    email = models.EmailField(max_length=254, blank=True)
    website = models.TextField(blank=True)
    telephone = models.BigIntegerField(blank=True, null=True)
    
class VirtualUser(User):
    description = models.TextField(blank=True)

class Account(models.Model):
    name = models.CharField(max_length=50, default="")
    users = models.ManyToManyField('User', blank=True)
    deposit = models.FloatField(default=0) #MoneyField; 
    balance = models.FloatField(default=0) #MoneyField; 
    taken = models.FloatField(default=0)

    def __str__(self):
        return "{} - {}".format(str(self.id), self.name)

    def add_balance(self, amount):
        self.balance += amount

    def subtract_balance(self, amount):
        self.balance -= amount

    def add_deposit(self, amount):
        self.deposit += amount

    def subtract_deposit(self, amount):
        self.deposit -= amount

    def add_taken(self, amount):
        self.taken += amount

    def subtract_taken(self, amount):
        self.taken -= amount

    def recalc_balance(self):
        self.balance = 0
        positive = Inpayment.objects.filter(charged_account=self).aggregate(sum('value')) + Restitution.objects.filter(charged_account=self).aggregate(sum('value')) + CostSharing.objects.filter(charged_account=self).aggregate(sum('value')) + Recovery.objects.filter(charged_account=self).aggregate(sum('value')) + Transfer.objects.filter(recipient_account=self).aggregate(sum('value'))
        negative = Taking.objects.filter(charged_account=self).aggregate(sum('value')) + ProceedsSharing.objects.filter(charged_account=self).aggregate(sum('value')) + Donation.objects.filter(charged_account=self).aggregate(sum('value')) + Transfer.objects.filter(charged_account=self).aggregate(sum('value')) + PayOutBalance.objects.filter(charged_account=self).aggregate(sum('value'))
        # missing: Shared costs, proceeds, donations, and recoveries where self is involved as a recipient
        self.add_balance(positive)
        self.subtract_balance(negative)
        self.save()

class AccPayPhases(models.Model):
    account = models.ForeignKey('Account')
    start_date = models.DateField()
    end_date = models.DateField()
    rate = models.FloatField(default=1)
    comment = models.TextField(blank=True)

class Engagement(models.Model):
    person = models.ForeignKey('Person')
    role = models.ForeignKey('Role')
    comment = models.TextField(blank=True)

class MoneyBox(models.Model):
    name = models.CharField(max_length=50)
    stock_value = models.FloatField(default=0)
    #inpayment_fee = models.FloatField(default=0)
    #inpayment_percentage_fee = models.FloatField(default=0)
    #payout_fee = models.FloatField(default=0)
    #payout_percentage_fee = models.FloatField(default=0)

    # TODO: Methode zum Berechnen des stock_value

class MoneyBoxStock(models.Model):
    moneybox = models.ForeignKey('MoneyBox')
    currency = models.ForeignKey('Currency')
    stock = models.FloatField()

    def inpayment(self, amount):
        self.stock_value += amount

    def payout(self, amount):
        self.stock_value -= amount

    def transfer(self, amount, recipient):
        self.payout(amount)
        recipient.inpayment(amount)

class StorageCondition(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(blank=True)

class StorageLocation(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    streetname = models.CharField(max_length=100, blank=True)
    streetnumber = models.SmallIntegerField(blank=True, null=True)
    zipcode = models.IntegerField(blank=True, null=True)
    town = models.CharField(max_length=100, blank=True)
    address_notice = models.TextField(blank=True)

class StorageSpace(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.ForeignKey('StorageLocation')
    active_winter = models.BooleanField(default=True)
    active_summer = models.BooleanField(default=True)
    temperature_winter_min = models.FloatField(blank=True, null=True)
    temperature_winter_max = models.FloatField(blank=True, null=True)
    temperature_summer_min = models.FloatField(blank=True, null=True)
    temperature_summer_max = models.FloatField(blank=True, null=True)
    humidity_winter_min = PercentField(blank=True, null=True)
    humidity_winter_max = PercentField(blank=True, null=True)
    humidity_summer_min = PercentField(blank=True, null=True)
    humidity_summer_max = PercentField(blank=True, null=True)
    brightness_winter = PercentField(blank=True, null=True)
    brightness_summer = PercentField(blank=True, null=True)
    reachability_winter = PercentField(blank=True, null=True)
    reachability_summer = PercentField(blank=True, null=True)
    smelliness_winter = PercentField(blank=True, null=True)
    smelliness_summer = PercentField(blank=True, null=True)
    ventilation_winter = PercentField(blank=True, null=True)
    ventilation_summer = PercentField(blank=True, null=True)
    rodentfree = models.NullBooleanField(blank=True) # safe from mice without further packaging
    mothfree = models.NullBooleanField(blank=True) # safe from moths without further packaging
    conditions = models.ManyToManyField('StorageCondition', blank=True, null=True) # list of storage conditions this position complies
    height_level = models.FloatField(blank=True, null=True) # height above room floor
    width = models.FloatField(blank=True, null=True) # width of the pace in cm
    depth = models.FloatField(blank=True, null=True) # width of the pace in cm
    height = models.FloatField(blank=True, null=True) # height of the space from height_level on in cm
    loadability = models.FloatField(blank=True, null=True) # in kg

class Material(models.Model):
# predefines materials for storage containers and packaging materials
# paper, foodsave plastic, non-foodsave plastic, unknown plastic, wood, stainless steel, aluminium, zellophane, white glass, green glass, brown glass, other glass
# übersetzen: Stoff, Pappe, Weißblech
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    foodsave = PercentField(blank=True, null=True)
    cleanness = PercentField(blank=True, null=True)
    smelliness = PercentField(blank=True, null=True)
    reachability = PercentField(blank=True, null=True) # how easy it is to open and to close
    resistance_smell = PercentField(blank=True, null=True)
    resistance_light = PercentField(blank=True, null=True)
    resistance_humidity = PercentField(blank=True, null=True)
    capability_oil = PercentField(blank=True, null=True) # how well it is suitable for oily goods like oily seeds (min 60%) or oil itself
    ventilation = PercentField(blank=True, null=True)
    rodentfree = models.NullBooleanField(blank=True) # whether it keeps the product safe from mice without further packaging
    mothfree = models.NullBooleanField(blank=True) # whether it keeps the product safe from moths without further packaging

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    full_names = models.TextField(blank=True)
    is_wholesale = models.BooleanField(default=False)
    is_retailer = models.BooleanField(default=False)
    is_processor = models.BooleanField(default=False)
    is_grower = models.BooleanField(default=False)
    is_device_provider = models.BooleanField(default=False)
    is_container_provider = models.BooleanField(default=False)
    is_packaging_provider = models.BooleanField(default=False)
    contact_person = models.ForeignKey('Person', blank=True, null=True)
    min_order_value = models.FloatField(null=True, blank=True) #MoneyField; 
    min_order_weight = models.FloatField(blank=True, null=True)
    max_order_weight = models.FloatField(blank=True, null=True) # maximum order weight per order in kg
    basic_cost = models.FloatField(null=True, blank=True) #MoneyField; 
    delivery_cost_gen = models.FloatField(null=True, blank=True) #MoneyField; 
    delivery_cost_per_unit = models.FloatField(null=True, blank=True) #MoneyField; 
    unit_for_delivery_cost = models.FloatField(null=True, blank=True) # in kg
    min_interval = models.FloatField(null=True, blank=True) # minimum interval between orders from this supplier in months
    description = models.TextField(blank=True)
    streetname = models.CharField(max_length=100, blank=True)
    streetnumber = models.SmallIntegerField(null=True, blank=True)
    zipcode = models.IntegerField(null=True, blank=True)
    town = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    address_notice = models.TextField(blank=True)
    broad_location = models.TextField(blank=True) # describes the location roughly, e.g. 
    distance = models.FloatField(null=True, blank=True) # the length of the delivery route (one-way) to the food coop storage place
    email = models.EmailField(max_length=254, blank=True)
    website = models.TextField(blank=True)
    telephone = models.BigIntegerField(null=True, blank=True)
    structure = models.TextField(blank=True) # the corporate structure, e.g. family-run
    focus = models.TextField(blank=True) # the business focus, e.g. a specific group of products
    processing = models.TextField(blank=True) # what the supplier can process with own machines
    distribution = models.TextField(blank=True) # how the supplier usually distributes his products
    animals = models.TextField(blank=True) # information about animal farming by the supplier or products sold by him
    official = models.PositiveSmallIntegerField(null=True, blank=True) # whether the supplier shall be uploaded in the online portal. 0 = not at all; 1 = without cost information; 2 = completely

    def __str__(self):
        return "{} in {} (area)".format(self.name, self.broad_location)

class ProductCat(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

class VAT(models.Model):
    percentage = models.DecimalField(max_digits=4, decimal_places=2)
    name = models.CharField(max_length=50, blank=True)

class ProductAvail(models.Model):
# Levels of availability, from none to surplus, in the storage and in general. Shows to all users vaguely in which amounts they can take the products from the storage.
# If a product has an almost empty stock but is easy to re-order, don't change ffthe availability to "scarce". Only do this if, for example, the suppliers don't have it until the next harvest, 
# or it is so hard to deliver that you want to reduce the amount in that it is taken, e.g. make it exclusive for core participants.
    name = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=6, blank=True)

class QualityFunction(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    feature = models.CharField(max_length=100) # enter the name(s) of the feature(s) for which this function is meant to be used
    a = models.FloatField(default=0)
    b = models.FloatField(default=0)
    c = models.FloatField(default=0)

class QualityFeature(models.Model): # TODO: options for automatically calculating conditions to be implemented
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    conditions_0 = models.TextField(blank=True)
    conditions_100 = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    importance = PercentField(default=100)
    function= models.ForeignKey('QualityFunction', null=True, blank=True)

class SupplierRating(models.Model): # General rating of the supplier. Every offer can still be rated specifically.
    supplier = models.ForeignKey('Supplier')
    feature = models.ForeignKey('QualityFeature')
    rating = PercentField()
    importance = PercentField(default=100)
    reason = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    official = models.PositiveSmallIntegerField(null=True, blank=True) # whether the rating shall be uploaded in the online portal. 0 = not at all; 1 = without importance; 2 = completely

class Unit(models.Model):
    name = models.CharField(max_length=100)
    weight = models.FloatField(null=True, blank=True) # in grams
    continuous = models.BooleanField()

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Consumable(Item):
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    orderpos = models.IntegerField(blank=True, null=True)
    unit = models.ForeignKey('Unit', blank=True, null=True)
    presumed_price = models.FloatField(null=True, blank=True) #MoneyField; 
    presumed_vat = models.ForeignKey('VAT', blank=True, null=True)
    estimated_consumption = models.FloatField(default=0) # presumed amount taken per month altogether (sum of all the participant's consumption guesses for this product)
    monthly_consumption = models.FloatField(default=0) # the actual average amount taken per month altogether
    taken = models.FloatField(default=0) # the whole amount ever taken from this product by the participants
    stock = models.FloatField(default=0) # amount of this product in stock
    on_order = models.FloatField(default=0) # amount of this product on order
    planning = models.FloatField(default=0) # amount of this product in orders in planning stage
    #availability = models.ForeignKey('ProductAvail') # TODO: Make enum

    def add_stock(self, amount):
        self.stock += amount

    def add_taken(self, amount):
        self.taken += amount

    def add_on_order(self, amount):
        self.on_order += amount

    def add_planning(self, amount):
        self.planning += amount

    def __str__(self):
        return self.name

    def calc_stock(self):
        # funktioniert nicht
        batches = Batch.objects.filter(consumable = self)
        for batch in batches:
        	self.stock += batch.stock
        self.save()

class Product(Consumable):
    category = models.ForeignKey('ProductCat', blank=True, null=True)
    density = models.FloatField(blank=True, null=True) # kg/l
    storability = models.DurationField(blank=True, null=True)
    usual_taking_min = models.FloatField(blank=True, null=True) # in which amounts the product is usually taken at once
    usual_taking_max = models.FloatField(blank=True, null=True) # in which amounts the product is usually taken at once
    storage_temperature_min = models.FloatField(blank=True, null=True)
    storage_temperature_optimal = models.FloatField(blank=True, null=True)
    storage_temperature_max = models.FloatField(blank=True, null=True)
    storage_humidity_min = PercentField(blank=True, null=True)
    storage_humidity_optimal = PercentField(blank=True, null=True)
    storage_humidity_max = PercentField(blank=True, null=True)
    storage_reachability_min = PercentField(blank=True, null=True)
    storage_smelliness_max = PercentField(blank=True, null=True)
    storage_height_min = models.FloatField(blank=True, null=True)
    storage_height_optimal = models.FloatField(blank=True, null=True)
    storage_height_max = models.FloatField(blank=True, null=True)
    storage_brightness_min = PercentField(blank=True, null=True)
    storage_brightness_max = PercentField(blank=True, null=True)
    storage_ventilation_min = PercentField(blank=True, null=True)
    storage_ventilation_max = PercentField(blank=True, null=True)
    storage_mothfree_needed = models.NullBooleanField(blank=True)
    storage_micefree_needed = models.NullBooleanField(blank=True)
    sc_essential = models.CommaSeparatedIntegerField(max_length=50, blank=True, null=True) # list of essential storage conditions
    sc_favorable = models.CommaSeparatedIntegerField(max_length=50, blank=True, null=True) # list of favorable storage conditions
    sc_unfavorable = models.CommaSeparatedIntegerField(max_length=50, blank=True, null=True) # list of unfavorable storage conditions
    sc_intolerable = models.CommaSeparatedIntegerField(max_length=50, blank=True, null=True) # list of intolerable storage conditions
    lossfactor = PercentField(default=0) # presumed lossfactor per month in % for this product (e.g. 3 => it is presumed to lose 3% of the stock every month of storage)
    official = models.PositiveSmallIntegerField(blank=True, null=True) # whether the product shall be uploaded in the online portal. 0 = not at all; 1 = without strage conditions; 2 = completely

    def __str__(self):
        return self.name

class Durable(Item):
    pass

class ConsumptionEstimation(models.Model):
    account = models.ForeignKey('Account')
    consumable = models.ForeignKey('Consumable')
    amount = models.FloatField()
    comment = models.TextField()
    relevant = models.BooleanField(default=True)
    entry_date = models.DateField(default=datetime.date.today)

class DeviceStatus(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

class DeviceCat(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

class Device(Durable):
    category = models.ForeignKey('DeviceCat')
    status = models.ForeignKey('DeviceStatus')
    active = models.BooleanField(default=True)

class DeviceByInstalments(Device):
    interval_months = models.FloatField(default=1) # months and days will be added
    interval_days = models.FloatField(default=0) # months and days will be added
    number_of_instalments = models.IntegerField(blank=True, null=True)
    deducted = models.FloatField(default=0) # amount that already has been deducted

class Instalment(models.Model):
    account = models.ForeignKey('Account')
    device = models.ForeignKey('DeviceByInstalments')
    instalment_number = models.IntegerField()
    rate = models.FloatField(default=1)
    amount = models.FloatField(default=0) #MoneyField; 

class Batch(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    consumable = models.ForeignKey('Consumable', blank=True, null=True)
    supplier = models.ForeignKey('Supplier', blank=True, null=True)
    owner_account = models.ForeignKey('Account')
    unit = models.ForeignKey('Unit', blank=True, null=True)
    price = models.FloatField() #MoneyField; 
    production_date = models.DateField(blank=True, null=True) # date of production, harvest, or purchase (for devices: start of warranty)
    purchase_date = models.DateField(blank=True, null=True) # date of production, harvest, or purchase (for devices: start of warranty)
    date_of_expiry = models.DateField(blank=True, null=True) # durability date; resp. for devices: end of service life, e.g. end of warranty
    exhaustion_date = models.DateField(blank=True, null=True) # the date when the stock is likely to be used-up
    stock = models.FloatField(default=0) # the exact amount in stock (desired value according to transitions)
    monthly_consumption = models.FloatField(default=0) # per month
    monthly_consumption_calcdate = models.DateField(blank=True, null=True) # date when monthly consumption was last calculated
    consumption_evaluation = models.TextField(blank=True) # enum ?
    taken = models.FloatField(default=0)
    parcel_approx = models.FloatField(default=0)
    special_density = models.FloatField(default=0)

    def add_stock(self, amount):
        self.stock += amount

    def subtract_stock(self, amount):
        self.stock -= amount

    def add_taken(self, amount):
        self.taken += amount

    def subtract_taken(self, amount):
        self.taken -= amount

    @property
    def text(self):
        return "B{} - {} by {} from {}".format(str(self.id), self.name, self.supplier, self.purchase_date)

    def __str__(self):
        return self.text

    def calc_monthly_consumption(self):
        # not tried out yet
        if self.taken > 0:
            start_date = Taking.objects.filter(batch=self).aggregate(Min('date'))
            end_date = Taking.objects.filter(batch=self).aggregate(Max('date'))
            days = (end_date - start_date)
            months = days.days / 30.4375
            self.monthly_consumption = self.taken / months
            self.monthly_consumption_calcdate = datetime.date.today
            self.save()
        else:
            self.monthly_consumption = 0
            self.save()
    
    def calc_exhaustion_date(self):
        # not tried out yet
        if self.stock <= 0 or (self.stock < self.consumable.usual_taking_min and self.consumable.usual_taking_min > 0):
            self.exhaustion_date = 0
            self.save()
        elif self.monthly_consumption > 0:
            self.exhaustion_date = datetime.date.today + self.stock / self.monthly_consumption * 30.4375
            self.save()
        else:
            self.exhaustion_date = null
            self.save()

    def evaluate_consumption(self):
        # not tried out yet
        if self.stock <= 0 or (self.stock < self.consumable.usual_taking_min and self.consumable.usual_taking_min > 0):
            self.consumption_evaluation = "empty or almost empty"
            self.save()
        elif self.exhaustion_date <= self.date_of_expiry:
            self.consumption_evaluation = "fine"
            self.save()
        elif self.date_of_expiry <= datetime.date.today:
            self.consumption_evaluation = "already expired"
            self.save()
        elif self.exhaustion_date > self.date_of_expiry:
            self.consumption_evaluation = "will exceed date of expiry"
            self.save()
        else:
            self.consumption_evaluation = "evaluation failed"
            self.save()

class BatchStorage(models.Model):
    batch = models.ForeignKey('Batch')
    position = models.ForeignKey('StorageSpace')
    is_reserve = models.BooleanField(default=False) # set True if this storage space is not meant to be used for direct taking by participants (resp. for money: direct insertion)
    amount_approx = models.FloatField(blank=True, null=True) # e.g. 25 for a bag with 24.697 kg
    comment = models.TextField(blank=True)

class ContainerCategory(ProductCat):
    pass

class Container(Consumable):
    # A type of storage containers or packaging containers/material
    material = models.ForeignKey('Material')
    category = models.ForeignKey('ContainerCategory')
    loanable = models.BooleanField() # whether it may be borrowed by participants
    buyable = models.BooleanField() # whether it may be bought by participants
    capacity = models.FloatField() # volume in l
    circular = models.BooleanField()
    foodsave = PercentField()
    cleanness = PercentField()
    smelliness = PercentField()
    cleanability = PercentField()
    reachability = PercentField() # how easy it is to open and to close (to handle generally)
    resistance_smell = PercentField()
    resistance_light = PercentField()
    resistance_humidity = PercentField()
    capability_oil = PercentField() # how well it is suitable for oily goods like oily seeds
    capability_liquid = PercentField() # how well it is suitable for liquids
    ventilation = PercentField()
    rodentfree = models.NullBooleanField() # whether it keeps the product safe from mice without further packaging
    mothfree = models.NullBooleanField() # whether it keeps the product safe from moths without further packaging
    width = models.FloatField() # width of the container in cm
    depth = models.FloatField() # depth of the container in cm (if it is circular, enter the width again)
    height = models.FloatField() # height of the container in cm
    amount_occupied = models.PositiveSmallIntegerField()
    amount_ready = models.PositiveSmallIntegerField()
    amount_unclean = models.PositiveSmallIntegerField()
    amount_defective = models.PositiveSmallIntegerField()
    amount_loaned = models.PositiveSmallIntegerField()
    amount_new = models.PositiveSmallIntegerField()
    volume_max = models.FloatField() # in l
    volume_easy = models.FloatField() # in l
    tare = models.FloatField() # in g
    tare_without_lid = models.FloatField() # in g
    tare3 = models.FloatField() # in g
    tare3_name = models.CharField(max_length=50)
    tare4 = models.FloatField() # in g
    tare4_name = models.CharField(max_length=50)
    tare5 = models.FloatField() # in g
    tare5_name = models.CharField(max_length=50)

    def __init__(self, name="Unnamed container", capacity=0, circular=False, amount_occupied=0, amount_ready=0, amount_unclean=0, amount_defective=0, amount_loaned=0, amount_new=0, tare=0, tare_without_lid=0):
        self.name = name
        self.capacity = capacity
        self.circular = circular
        self.amount_occupied = amount_occupied
        self.amount_ready = amount_ready
        self.amount_unclean = amount_unclean
        self.amount_defective = amount_defective
        self.amount_loaned = amount_loaned
        self.amount_new = amount_new
        self.tare = tare
        self.tare_without_lid = tare_without_lid

    def print_amounts(self):
        print("occupied:", self.amount_occupied, "ready:", self.amount_ready, "unclean:", self.amount_unclean, "defective:", self.amount_defective)

    def occupy(self, amount, status):
        if status == 'ready':
            self.amount_occupied += amount
            self.amount_ready -= amount
        elif status == 'unclean':
            self.amount_occupied += amount
            self.amount_unclean -= amount
        elif status == 'defective':
            self.amount_occupied += amount
            self.amount_defective -= amount
        else:
            print('The former status must be entered: ready, unclean or defective.')

    def clean(self, amount):
        self.amount_ready += amount
        self.amount_unclean -= amount

    def defect(self, amount, status):
        if status == 'occupied':
            self.amount_defective += amount
            self.amount_occupied -= amount
        elif status == 'ready':
            self.amount_defective += amount
            self.amount_ready -= amount
        elif status == 'unclean':
            self.amount_defective += amount
            self.amount_unclean -= amount
        else:
            print('The former status must be entered: occupied, ready or unclean.')

    def repaired(self, amount, status):
        if status == 'occupied':
            self.amount_defective -= amount
            self.amount_occupied += amount
        elif status == 'ready':
            self.amount_defective -= amount
            self.amount_ready += amount
        elif status == 'unclean':
            self.amount_defective -= amount
            self.amount_unclean += amount
        else:
            print('The new status must be entered: occupied, ready or unclean.')

    def empty(self, amount, status):
        if status == 'ready':
            self.amount_occupied -= amount
            self.amount_ready += amount
        elif status == 'unclean':
            self.amount_occupied -= amount
            self.amount_unclean += amount
        elif status == 'defective':
            self.amount_occupied -= amount
            self.amount_defective += amount
        else:
            print('The new status must be entered: ready, unclean or defective.')

    def delete(self, amount, status):
        if status == 'ready':
            self.amount_ready -= amount
        elif status == 'unclean':
            self.amount_unclean -= amount
        elif status == 'defective':
            self.amount_defective -= amount
        elif status == 'occupied':
            self.amount_occupied -= amount
        else:
            print('The former status must be entered: defective, occupied, ready or unclean.')

    def add(self, amount, status):
        if status == 'ready':
            self.amount_ready += amount
        elif status == 'unclean':
            self.amount_unclean += amount
        elif status == 'defective':
            self.amount_defective += amount
        elif status == 'occupied':
            self.amount_occupied += amount
        else:
            print('The new status must be entered: occupied, ready, unclean or defective.')

class GeneralOffer(models.Model):
    # Describes a consumable offered by a supplier, but not in a specific package and with a specific price.
    consumable = models.ForeignKey('Consumable', related_name="consumable")
    distributor = models.ForeignKey('Supplier', related_name="distributor") # the supplier from whom the product is bought by the food coop
    processor = models.ForeignKey('Supplier', related_name="processor") # the supplier from whom the product has been processed (optional; in many cases the distributor itself)
    grower = models.ForeignKey('Supplier', related_name="grower") # the supplier from whom the product has been grown (optional; in many cases the distributor itself)
    variety = models.CharField(max_length=50)
    vat = models.ForeignKey('VAT', related_name="VAT")
    distance_total = models.FloatField() # replaces the distance of the supplier
    distance_add = models.FloatField() # will be added to the distance of the supplier
    orderpos = models.IntegerField()
    comment = models.TextField()
    supply_stock = models.FloatField() # in product unit

class Offer(models.Model):
    # Describes a specific offer of an offered consumable.
    general_offer = models.ForeignKey('GeneralOffer')
    parcel = models.FloatField() # how much g a single package or filling unit is (e.g. 25kg bag -> 25000; 1kg packages -> 1000; bulk with any amount in kg -> 1000)
    quantity = models.IntegerField() # how many parcels have to be taken at once
    favorite = models.BooleanField()
    official = models.PositiveSmallIntegerField() # whether the offer shall be uploaded in the online portal. 0 = not at all; 1 = without price information; 2 = completely
    basic_price = models.FloatField(null=True, blank=True) #MoneyField; 
    total_price = models.FloatField(null=True, blank=True) #MoneyField; 
    discount = models.FloatField(null=True, blank=True) #MoneyField; 
    available = models.BooleanField()
    available_from = models.DateField()
    available_until = models.DateField()
    orderpos = models.IntegerField()
    comment = models.TextField()
    supply_stock = models.FloatField() # in product unit (caution, this is the stock of this offer with its specific packaging)

class OfferRating(models.Model):
    offer = models.ForeignKey('Offer')
    feature = models.ForeignKey('QualityFeature')
    replace = models.BooleanField() # If True, the OfferRating replaces the SupplierRatingng for this offer and feature. If False, it will be multiplied with it.
    rating = PercentField()
    importance = PercentField()
    reason = models.TextField()
    comment = models.TextField()
    official = models.PositiveSmallIntegerField() # whether the rating shall be uploaded in the online portal. 0 = not at all; 1 = without importance; 2 = completely

class TransactionStatus(models.Model): # predefined statuses, i. a. planning, on_order, completed, aborted
    name = models.CharField(max_length=50)
    description = models.TextField()

class Insertion(models.Model):
    by_user = models.ForeignKey('User')
    by_user_comment = models.TextField()
    payer_account = models.ForeignKey('Account', related_name="payer_account")
    supplier = models.ForeignKey('Supplier')
    total_cost = models.FloatField(null=True, blank=True) #MoneyField; 
    total_price = models.FloatField(null=True, blank=True) #MoneyField; 
    discount = models.FloatField(null=True, blank=True) #MoneyField; 
    basic_cost = models.FloatField(null=True, blank=True) #MoneyField; 
    delivery_cost = models.FloatField(null=True, blank=True) #MoneyField; 
    deliverer_account = models.ForeignKey('Account', related_name="deliverer_account") # who paid for the delivery or transport. If the delivery cost has to be paid to the supplier, this has to be null.
    sum_of_lot_prices = models.FloatField(null=True, blank=True) #MoneyField; 
    difference = models.FloatField(null=True, blank=True) #MoneyField; 
    compensation_account = models.ForeignKey('Account') # who pays or gets the difference
    status = models.ForeignKey('TransactionStatus')
    date_creation = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

class Transaction(models.Model):
    charged_account = models.ForeignKey('Account')
    by_user = models.ForeignKey('User') # Person who types in the transaction
    date = models.DateField()
    entry_date = models.DateField(auto_now_add=True) # Date when transaction is entered into the system
    amount = models.FloatField()
    value = models.FloatField(default=0)
    status = models.ForeignKey('TransactionStatus', blank=True, null=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return "Tr{} {} on {}: {}: {} {} (submitted by {})".format(str(self.id), self.charged_account.name, self.date, self.batch, self.amount, self.batch.unit, self.by_user.name)

    def perform(self):
        batch = Batch.objects.get(pk=self.batch.id) # type(transaction.batch) == Batch
        batch.subtract_stock(self.amount)
        batch.add_taken(self.amount)
        batch.save()
        self.value = self.amount * batch.price
        account = Account.objects.get(pk=self.charged_account.id)
        account.subtract_balance(self.value)
        account.add_taken(self.amount)
        account.save()
        self.save()

class Taking(Transaction): # taking of goods from balance
    batch = models.ForeignKey('Batch')

    @property
    def type_name(self):
        return "Taking"

class Restitution(Transaction): # return goods to the storage
    batch = models.ForeignKey('Batch')
    original_taking = models.ForeignKey('Taking', blank=True, null=True)
    approved_by = models.ForeignKey('User', blank=True, null=True)
    approval_comment = models.TextField()

    def perform(self):
        batch = Batch.objects.get(pk=self.batch.id) # type(transaction.batch) == Batch
        batch.add_stock(self.amount)
        batch.subtract_taken(self.amount)
        batch.save()
        self.value = self.amount * batch.price
        account = Account.objects.get(pk=self.charged_account.id)
        account.add_balance(self.value)
        account.subtract_taken(self.amount)
        account.save()
        self.save()

    @property
    def type_name(self):
        return "Restitution"

class Inpayment(Transaction): # insertion of money to balance
    currency = models.ForeignKey('Currency')
    moneybox = models.ForeignKey('MoneyBox')
    confirmed_by = models.ForeignKey('User', blank=True, null=True)
    confirmation_comment = models.TextField()

    def perform(self):
        currency = Currency.objects.get(pk=self.currency.id)
        self.value = self.amount * currency.concersion_rate
        moneybox = MoneyBox.objects.get(pk=self.moneybox.id)
        moneyboxstock = MoneyBoxStock.objects.get(moneybox=moneybox, currency=currency) # foreign key?
        moneyboxstock.inpayment(self.amount)
        moneyboxstock.save()
        account = Account.objects.get(pk=self.charged_account.id)
        account.add_balance(self.value)
        account.save()
        self.save()

class Depositation(Transaction): # insertion of money to deposit
    currency = models.ForeignKey('Currency')
    moneybox = models.ForeignKey('MoneyBox')
    confirmed_by = models.ForeignKey('User', blank=True, null=True)
    confirmation_comment = models.TextField()

    # perform

class PayOutbalance(Transaction):
    currency = models.ForeignKey('Currency')
    moneybox = models.ForeignKey('MoneyBox')

    # perform

class PayOutDeposit(Transaction):
    currency = models.ForeignKey('Currency')
    moneybox = models.ForeignKey('MoneyBox')

    # perform

#class Trbalance_in_Good(Transaction): # insertion of goods to balance
#    insertion = models.ForeignKey('Insertion')

#class Trbalance_out_Money(Transaction): # taking of money from balance
#    pass

#class TrDeposit_in(Transaction): # insertion of money or goods to deposit
#    pass

#class TrDeposit_out(Transaction): # taking of money or goods from deposit
#    pass

class Transfer(Transaction): # IDEE: Im Frontend Feld Value, das durch Eingaben in Felder Amount und entweder Currency oder Batch berechnet wird
    recipient_account = models.ForeignKey('Account')

    def perform(self):
        sender_account = Account.objects.get(pk=self.charged_account.id)
        sender_account.subtract_balance(self.value)
        sender_account.save()
        recipient_account = Account.objects.get(pk=self.recipient_account.id)
        recipient_account.add_balance(self.value)
        recipient_account.save()
        self.save()

class CostSharing(Transaction):
    excepted_accounts = models.ManyToManyField('Account')
    approved_by = models.ForeignKey('User', blank=True, null=True)
    approval_comment = models.TextField()

    # TODO: perform

class ProceedsSharing(Transaction):
    excepted_accounts = models.ManyToManyField('Account')
    approved_by = models.ForeignKey('User', blank=True, null=True)
    approval_comment = models.TextField()

    # TODO: perform

class Donation(Transaction):
    excepted_accounts = models.ManyToManyField('Account')
    approved_by = models.ForeignKey('User', blank=True, null=True)
    approval_comment = models.TextField()

    # TODO: perform

class Recovery(Transaction): # donation backwards
    excepted_accounts = models.ManyToManyField('Account')
    approved_by = models.ForeignKey('User', blank=True, null=True)
    approval_comment = models.TextField()

    # TODO: perform
