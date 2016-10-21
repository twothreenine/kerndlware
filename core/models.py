from django.db import models
from djmoney.models.fields import MoneyField
from moneyed import Money, EUR
from .fields import PercentField

class Role(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    comment = models.TextField() # test

class User(models.Model):
    active = models.BooleanField()
    comment = models.TextField()
    accounts = models.ManyToManyField('Account')

class Person(User):
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    streetname = models.CharField(max_length=100)
    streetnumber = models.SmallIntegerField()
    zipcode = models.IntegerField()
    town = models.CharField(max_length=100)
    address_notice = models.TextField()
    email = models.EmailField(max_length=254)
    website = models.TextField()
    telephone = models.BigIntegerField()
    
class VirtualUser(User):
    name = models.CharField(max_length=50)
    description = models.TextField()

class Account(models.Model):
    name = models.CharField(max_length=50, default="")
    users = models.ManyToManyField('User', blank=True)
    deposit = MoneyField(max_digits=10, decimal_places=4, default_currency='EUR')
    credit = MoneyField(max_digits=10, decimal_places=4, default_currency='EUR')
    taken = models.FloatField()

    def add_credit(self, amount):
        self.credit += Money(amount, EUR)

    def add_deposit(self, amount):
        self.deposit += Money(amount, EUR)

    def add_taken(self, amount):
        self.taken += amount

    def __str__(self):
        return "{} - {}".format(str(self.id), self.name)

class AccPayPhases(models.Model):
    account = models.ForeignKey('Account')
    start_date = models.DateField()
    end_date = models.DateField()
    rate = models.FloatField(default=1)
    comment = models.TextField()

class Engagement(models.Model):
    person = models.ForeignKey('Person')
    role = models.ForeignKey('Role')
    comment = models.TextField()

class StorageCondition(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()

class StorageLocation(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    streetname = models.CharField(max_length=100)
    streetnumber = models.SmallIntegerField()
    zipcode = models.IntegerField()
    town = models.CharField(max_length=100)
    address_notice = models.TextField()

class StorageSpace(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.ForeignKey('StorageLocation')
    active_winter = models.BooleanField()
    active_summer = models.BooleanField()
    temperature_winter_min = models.FloatField()
    temperature_winter_max = models.FloatField()
    temperature_summer_min = models.FloatField()
    temperature_summer_max = models.FloatField()
    humidity_winter_min = PercentField()
    humidity_winter_max = PercentField()
    humidity_summer_min = PercentField()
    humidity_summer_max = PercentField()
    brightness_winter = PercentField()
    brightness_summer = PercentField()
    reachability_winter = PercentField()
    reachability_summer = PercentField()
    smelliness_winter = PercentField()
    smelliness_summer = PercentField()
    ventilation_winter = PercentField()
    ventilation_summer = PercentField()
    rodentfree = models.NullBooleanField() # safe from mice without further packaging
    mothfree = models.NullBooleanField() # safe from moths without further packaging
    conditions = models.ManyToManyField('StorageCondition') # list of storage conditions this position complies
    height_level = models.FloatField() # height above room floor
    width = models.FloatField() # width of the pace in cm
    depth = models.FloatField() # width of the pace in cm
    height = models.FloatField() # height of the space from height_level on in cm
    loadability = models.FloatField() # in kg

class Material(models.Model):
# predefines materials for storage containers and packaging materials
# paper, foodsave plastic, non-foodsave plastic, unknown plastic, wood, stainless steel, aluminium, zellophane, white glass, green glass, brown glass, other glass
# übersetzen: Stoff, Pappe, Weißblech
    name = models.CharField(max_length=100)
    description = models.TextField()
    comment = models.TextField()
    foodsave = PercentField()
    cleanness = PercentField()
    smelliness = PercentField()
    reachability = PercentField() # how easy it is to open and to close
    resistance_smell = PercentField()
    resistance_light = PercentField()
    resistance_humidity = PercentField()
    capability_oil = PercentField() # how well it is suitable for oily goods like oily seeds (min 60%) or oil itself
    ventilation = PercentField()
    rodentfree = models.NullBooleanField() # whether it keeps the product safe from mice without further packaging
    mothfree = models.NullBooleanField() # whether it keeps the product safe from moths without further packaging

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    full_names = models.TextField()
    is_wholesale = models.BooleanField()
    is_retailer = models.BooleanField()
    is_processor = models.BooleanField()
    is_grower = models.BooleanField()
    is_devicer = models.BooleanField() # besser übersetzen, sb who offers devices
    is_containerer = models.BooleanField() # besser übersetzen, sb who offers containers
    is_packager = models.BooleanField() # besser übersetzen, sb who offers packaging material
    contact_person = models.ForeignKey('Person')
    min_order_value = MoneyField(max_digits=8, decimal_places=3, default_currency='EUR')
    min_order_weight = models.DecimalField(max_digits=7, decimal_places=2)
    max_order_weight = models.DecimalField(max_digits=7, decimal_places=2) # maximum order weight per order in kg
    basic_cost = MoneyField(max_digits=8, decimal_places=3, default_currency='EUR')
    delivery_cost_gen = MoneyField(max_digits=8, decimal_places=3, default_currency='EUR')
    delivery_cost_per_unit = MoneyField(max_digits=8, decimal_places=3, default_currency='EUR')
    unit_for_delivery_cost = models.FloatField() # in kg
    min_interval = models.FloatField() # minimum interval between orders from this supplier in months
    description = models.TextField()
    streetname = models.CharField(max_length=100)
    streetnumber = models.SmallIntegerField()
    zipcode = models.IntegerField()
    town = models.CharField(max_length=100)
    address_notice = models.TextField()
    distance = models.FloatField() # the length of the delivery route (one-way) to the food coop storage place
    email = models.EmailField(max_length=254)
    website = models.TextField()
    telephone = models.BigIntegerField()
    structure = models.TextField() # the corporate structure, e.g. family-run
    focus = models.TextField() # the business focus, e.g. a specific group of products
    processing = models.TextField() # what the supplier can process with own machines
    distribution = models.TextField() # how the supplier usually distributes his products
    animals = models.TextField() # information about animal farming by the supplier or products sold by him
    official = models.PositiveSmallIntegerField() # whether the supplier shall be uploaded in the online portal. 0 = not at all; 1 = without cost information; 2 = completely

class ProductCat(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

class VAT(models.Model):
    percentage = models.DecimalField(max_digits=4, decimal_places=2)
    description = models.CharField(max_length=30)

class ProductAvail(models.Model):
# Levels of availability, from none to surplus, in the storage and in general. Shows to all users vaguely in which amounts they can take the products from the storage.
# If a product has an almost empty stock but is easy to re-order, don't change ffthe availability to "scarce". Only do this if, for example, the suppliers don't have it until the next harvest, 
# or it is so hard to deliver that you want to reduce the amount in that it is taken, e.g. make it exclusive for core participants.
    name = models.CharField(max_length=30)
    description = models.TextField()
    color = models.CharField(max_length=6)

class QualityFunction(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    feature = models.CharField(max_length=100) # enter the name(s) of the feature(s) for which this function is meant to be used
    a = models.FloatField()
    b = models.FloatField()
    c = models.FloatField()

class QualityFeature(models.Model): # TODO: options for automatically calculating conditions to be implemented
    name = models.CharField(max_length=100)
    description = models.TextField()
    conditions_0 = models.TextField()
    conditions_100 = models.TextField()
    comment = models.TextField()
    importance = PercentField()
    function= models.ForeignKey('QualityFunction')

class SupplierRating(models.Model): # General rating of the supplier. Every offer can still be rated specifically.
    supplier = models.ForeignKey('Supplier')
    feature = models.ForeignKey('QualityFeature')
    rating = PercentField()
    importance = PercentField()
    reason = models.TextField()
    comment = models.TextField()
    official = models.PositiveSmallIntegerField() # whether the rating shall be uploaded in the online portal. 0 = not at all; 1 = without importance; 2 = completely

class Unit(models.Model):
    name = models.CharField(max_length=100)
    weight = models.FloatField() # in grams
    continuous = models.BooleanField()

class Item(models.Model):
    name = models.CharField(max_length=100)

class Consumable(Item):
    description = models.TextField()
    active = models.BooleanField()
    orderpos = models.IntegerField()
    unit = models.ForeignKey('Unit')
    presumed_price = MoneyField(max_digits=8, decimal_places=3, default_currency='EUR')
    vat = models.ForeignKey('VAT')
    estimated_consumption = models.FloatField() # presumed amount taken per month altogether (sum of all the participant's consumption guesses for this product)
    average_consumption = models.FloatField() # the actual average amount taken per month altogether
    taken = models.FloatField() # the whole amount ever taken from this product by the participants
    stock = models.FloatField() # amount of this product in stock
    on_order = models.FloatField() # amount of this product on order
    planning = models.FloatField() # amount of this product in orders in planning stage
    availability = models.ForeignKey('ProductAvail') # TODO: Make enum

    def add_stock(self, amount):
        self.stock += amount

    def add_taken(self, amount):
        self.taken += amount

    def add_on_order(self, amount):
        self.on_order += amount

    def add_planning(self, amount):
        self.planning += amount

class Product(Consumable):
    category = models.ForeignKey('ProductCat')
    density = models.FloatField() # kg/l
    storability = models.DurationField()
    usual_taking_min = models.FloatField() # in which amounts the product is usually taken at once
    usual_taking_max = models.FloatField() # in which amounts the product is usually taken at once
    storage_temperature_min = models.FloatField()
    storage_temperature_optimal = models.FloatField()
    storage_temperature_max = models.FloatField()
    storage_humidity_min = PercentField()
    storage_humidity_optimal = PercentField()
    storage_humidity_max = PercentField()
    storage_reachability_min = PercentField()
    storage_smelliness_max = PercentField()
    storage_height_min = models.FloatField()
    storage_height_optimal = models.FloatField()
    storage_height_max = models.FloatField()
    storage_brightness_min = PercentField()
    storage_brightness_max = PercentField()
    storage_ventilation_min = PercentField()
    storage_ventilation_max = PercentField()
    storage_mothfree_needed = models.NullBooleanField()
    storage_micefree_needed = models.NullBooleanField()
    sc_essential = models.CommaSeparatedIntegerField(max_length=50) # list of essential storage conditions
    sc_favorable = models.CommaSeparatedIntegerField(max_length=50) # list of favorable storage conditions
    sc_unfavorable = models.CommaSeparatedIntegerField(max_length=50) # list of unfavorable storage conditions
    sc_intolerable = models.CommaSeparatedIntegerField(max_length=50) # list of intolerable storage conditions
    lossfactor = models.FloatField() # presumed lossfactor per month in % for this product (e.g. 3 => it is presumed to lose 3% of the stock every month of storage)
    official = models.PositiveSmallIntegerField() # whether the product shall be uploaded in the online portal. 0 = not at all; 1 = without strage conditions; 2 = completely

class Durable(Item):
    pass

class DeviceStatus(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

class DeviceCat(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

class Device(Durable):
    category = models.ForeignKey('DeviceCat')
    status = models.ForeignKey('DeviceStatus')
    active = models.BooleanField()

class DeviceByInstalments(Device):
    interval_months = models.FloatField() # months and days will be added
    interval_days = models.FloatField() # months and days will be added
    number_of_instalments = models.IntegerField()
    deducted = models.FloatField() # amount that already has been deducted

class Instalment(models.Model):
    account = models.ForeignKey('Account')
    device = models.ForeignKey('DeviceByInstalments')
    instalment_number = models.IntegerField()
    rate = models.FloatField()
    amount = MoneyField(max_digits=10, decimal_places=4, default_currency='EUR')

class Batch(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    consumable = models.ForeignKey('Consumable', blank=True, null=True)
    supplier = models.ForeignKey('Supplier', blank=True, null=True)
    owner_account = models.ForeignKey('Account')
    unit = models.ForeignKey('Unit', blank=True, null=True)
    price = MoneyField(max_digits=8, decimal_places=3, default_currency='EUR')
    production_date = models.DateField(blank=True, null=True) # date of production, harvest, or purchase (for devices: start of warranty)
    purchase_date = models.DateField(blank=True, null=True) # date of production, harvest, or purchase (for devices: start of warranty)
    date_of_expiry = models.DateField(blank=True, null=True) # durability date; resp. for devices: end of service life, e.g. end of warranty
    stock = models.FloatField(default=0) # the exact amount in stock (desired value according to transitions)
    average_consumption = models.FloatField(default=0)
    taken = models.FloatField(default=0)
    parcel_approx = models.FloatField(default=0)
    special_density = models.FloatField(default=0)

    def add_stock(self, amount):
        self.stock += amount

    def add_taken(self, amount):
        self.taken += amount

class BatchStorage(models.Model):
    batch = models.ForeignKey('Batch')
    position = models.ForeignKey('StorageSpace')
    is_reserve = models.BooleanField() # set True if this storage space is not meant to be used for direct taking by participants (resp. for money: direct insertion)
    amount_approx = models.FloatField() # e.g. 25 for a bag with 24.697 kg
    comment = models.TextField()

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
    basic_price = MoneyField(max_digits=8, decimal_places=3, default_currency='EUR')
    total_price = MoneyField(max_digits=8, decimal_places=3, default_currency='EUR')
    discount = MoneyField(max_digits=8, decimal_places=3, default_currency='EUR')
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
    total_cost = MoneyField(max_digits=8, decimal_places=3, default_currency='EUR')
    total_price = MoneyField(max_digits=8, decimal_places=3, default_currency='EUR')
    discount = MoneyField(max_digits=8, decimal_places=3, default_currency='EUR')
    basic_cost = MoneyField(max_digits=8, decimal_places=3, default_currency='EUR')
    delivery_cost = MoneyField(max_digits=8, decimal_places=3, default_currency='EUR')
    deliverer_account = models.ForeignKey('Account', related_name="deliverer_account") # who paid for the delivery or transport. If the delivery cost has to be paid to the supplier, this has to be null.
    sum_of_lot_prices = MoneyField(max_digits=8, decimal_places=3, default_currency='EUR')
    balance = MoneyField(max_digits=8, decimal_places=3, default_currency='EUR')
    compensation_account = models.ForeignKey('Account') # who pays or gets the balance
    status = models.ForeignKey('TransactionStatus')
    date_creation = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

class Transaction(models.Model):
    charged_account = models.ForeignKey('Account')
    by_user = models.ForeignKey('User') # Person who types in the transaction
    date = models.DateField()
    entry_date = models.DateField(auto_now_add=True) # Date when transaction is entered into the system
    batch = models.ForeignKey('Batch')
    amount = models.FloatField()
    status = models.ForeignKey('TransactionStatus', blank=True, null=True)
    comment = models.TextField()

class TakingGood(Transaction): # taking of goods from credit
    pass

class TrCredit_in_Money(Transaction): # insertion of money to credit
    pass

class TrCredit_in_Good(Transaction): # insertion of goods to credit
    insertion = models.ForeignKey('Insertion')

class TrCredit_out_Money(Transaction): # taking of money from credit
    pass

class TrDeposit_in(Transaction): # insertion of money or goods to deposit
    pass

class TrDeposit_out(Transaction): # taking of money or goods from deposit
    pass

class TrCommon(Transaction):
    excepted_accounts = models.ManyToManyField('Account')

class TrDistribution(Transaction):
    excepted_accounts = models.ManyToManyField('Account')
    
class TrTransfer(Transaction):
    recipient_account = models.ForeignKey('Account')
