from django.db import models
from django.db.models import Q
import datetime
#from djmoney.models.fields import MoneyField
#from moneyed import Money, EUR
from .fields import PercentField
import datetime
import itertools

class Currency(models.Model):
    name = models.CharField(max_length=10)
    conversion_rate = models.FloatField(default=1) # into anchor currency
    full_name = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    comment = models.TextField(blank=True)

    def __init__(self, name, conversion_rate=1, full_name='', description='', comment=''):
        self.name = name
        self.conversion_rate = conversion_rate
        self.full_name = full_name
        self.description = description
        self.comment = comment
        self.save()
        for mb in MoneyBox.objects.all():
            mbs = MoneyBoxStock(money_box=mb, currency=self)
            mbs.save()

    def __str__(self):
        return "{} ({})".format(self.name, self.full_name)
        
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
    original_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        rate = self.calc_rate(datetime=datetime.datetime.now())
        return "{} - {} ({}x)".format(str(self.id), self.name, rate)

    def calc_rate(self, datetime):
        """
        Calculates the payment rate of an account on a specific date. If more than one pay phase applies to the date, their rates get multiplied. If none applies, the rate is set to 0.
        The date must be given in this format: datetime=datetime.date(year,month,day)  or for today's date: datetime=datetime.date.today()
        """
        current_phases = AccPayPhase.objects.filter(account = self.id).filter(Q(start=None)|Q(start__lte=datetime)).filter(Q(end=None)|Q(end__gte=datetime))
        if not current_phases:
            rate = 0
        else:
            rate = 1
            for payphase in current_phases:
                rate = rate * payphase.rate
        return rate

    @property
    def users_str(self):
        users = list(self.users.all())
        if users:
            usernames = users[0].name
            users.pop(0)
            for user in users:
                usernames += ", " + user.name
            return usernames
        else:
            return ""

    def deposit_str(self):
        return "{} €".format(format(self.deposit,'.2f'))

    def taken_str(self):
        return "{} kg".format(format(self.taken,'.1f'))

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

    @property
    def balance_str(self):
        self.calc_balance()
        return "{} €".format(format(self.balance,'.2f'))

    def calc_balance(self):
        balance = 0
        charges = Charge.objects.filter(account=self)
        for charge in charges:
            if charge.to_balance == True:
                balance += charge.value
            else:
                pass
        self.balance = balance
        self.save()
        #positive = Inpayment.objects.filter(originator_account=self).aggregate(sum('value')) + Restitution.objects.filter(originator_account=self).aggregate(sum('value')) + CostSharing.objects.filter(originator_account=self).aggregate(sum('value')) + Recovery.objects.filter(originator_account=self).aggregate(sum('value')) + Transfer.objects.filter(recipient_account=self).aggregate(sum('value'))
        #negative = Taking.objects.filter(originator_account=self).aggregate(sum('value')) + ProceedsSharing.objects.filter(originator_account=self).aggregate(sum('value')) + Donation.objects.filter(originator_account=self).aggregate(sum('value')) + Transfer.objects.filter(originator_account=self).aggregate(sum('value')) + PayOutBalance.objects.filter(originator_account=self).aggregate(sum('value'))
        # missing: Shared costs, proceeds, donations, and recoveries where self is involved as a recipient
        #self.add_balance(positive)
        #self.subtract_balance(negative)
        #self.save()

    @property
    def deposit_str(self):
        self.calc_deposit()
        return "{} €".format(format(self.deposit,'.2f'))

    def calc_deposit(self):
        deposit = 0
        charges = Charge.objects.filter(account=self)
        for charge in charges:
            if charge.to_balance == False:
                deposit += charge.value
            else:
                pass
        self.deposit = deposit
        self.save()

    @property
    def taken_str(self):
        self.calc_taken()
        return "{} kg".format(format(self.taken,'.1f'))

    def calc_taken(self):
        taken = 0
        takings = Taking.objects.filter(originator_account=self)
        restitutions = Restitution.objects.filter(originator_account=self)
        for taking in takings:
            taken += taking.amount * taking.batch.unit.weight/1000
        for restitution in restitutions:
            taken -= restitution.amount * restitution.batch.unit.weight/1000
        self.taken = taken
        self.save()

class AccPayPhase(models.Model):
    account = models.ForeignKey('Account', blank=True, null=True) # former ManyToManyField
    start = models.DateField(blank=True, null=True) # null means the phase has no minimum date
    end = models.DateField(blank=True, null=True) # null means the phase has no maximum date (use null here for a current phase without any end given yet)
    rate = models.FloatField(default=1)
    comment = models.TextField(blank=True)

    def __str__(self):
        if self.start == None:
            start = 'from the beginning'
        else:
            start = 'from ' + str(self.start) + ' on'
        if self.end == None:
            end = 'to forever'
        else:
            end = 'to ' + str(self.end)
        if self.start == None and self.end == None:
            start = 'always'
            end = ''
        # for acc in self.account.all():
        #     account_names += str(acc.name) + ', ' # TODO: don't put comma after last name
        account_name = self.account.name
        return "{}: {}x {} {}".format(account_name, self.rate, start, end)

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

    def __init__(self, name, stock_value=0):
        self.name = name
        self.stock_name = stock_name
        self.save()
        for c in Currency.objects.all():
            mbs = MoneyBoxStock(money_box=self, currency=c)
            mbs.save()

    def __str__(self):
        return "{}".format(self.name)

    def calc_stock_value(self):
        stocks = MoneyBoxStock.objects.filter(money_box=self)
        value = 0
        for moneyboxstock in stocks:
            value += moneyboxstock.stock * moneyboxstock.currency.conversion_rate
        self.stock_value = value
        self.save()

class MoneyBoxStock(models.Model):
    money_box = models.ForeignKey('MoneyBox')
    currency = models.ForeignKey('Currency')
    stock = models.FloatField(default=0)

    def inpayment(self, amount):
        self.stock += amount

    def payout(self, amount):
        self.stock -= amount

    def transfer(self, amount, recipient):
        self.payout(amount)
        recipient.inpayment(amount)

    def __str__(self):
        return "{}: {}".format(self.money_box, self.currency)

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
    conditions = models.ManyToManyField('StorageCondition', blank=True) # list of storage conditions this position complies
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
    min_interval = models.FloatField(null=True, blank=True) # minimum interval between orders from this supplier in days
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

class VAT(models.Model):
    percentage = models.DecimalField(max_digits=4, decimal_places=2)
    name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return "{} ({})".format(self.percentage, self.name)

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
    full_name = models.CharField(max_length=100)
    abbr = models.CharField(max_length=100) # abbreviation of the unit, important for the display
    plural = models.CharField(max_length=100, blank=True, default='') # how the unit shall be called in the plural
    contents = models.CharField(max_length=100, blank=True, default='') # Only for non-continuous units for which the contents shouldn't be displayed in the anchor unit, e.g. "250 ml" if the anchor unit is grams.
    weight = models.FloatField(null=True, blank=True) # in grams resp. anchor unit
    continuous = models.BooleanField() # True for bulk units like kg or L if the goods get weighed. False 

    def __str__(self):
        return "{} ({})".format(self.full_name, self.abbr)

    def display(self, amount, show_contents=True):
        """
        Returns a string consisting of an amount, the unit (prn plural) and the contents of the unit (can be deactivated)
        The string may be used in batch/consumable information (stock, average etc) and as transaction description.
        Examples:  "2 bottles per 500 ml"; "1 package per 200 g"; "1.390 kg"
        """
        # If the unit is continuous, the contents (like "per 500 ml") won't be shown
        if self.continuous == True:
            return "{} {}".format(format(amount, '.3f'), self.abbr)
        else:
            # If the attribute field is empty or not asked for, we won't write anything after the unit
            if not self.contents == '' and show_contents == True:
                cont = " per {}".format(self.contents)
            else:
                cont = ""
            # If the plural attribute is empty, we'll use the abbreviation instead, better than printing nothing.
            if not amount == 1 and not self.plural == '':
                return "{} {}{}".format(format(amount, '.0f'), self.plural, cont)
            else:
                return "{} {}{}".format(format(amount, '.0f'), self.abbr, cont)

    def unit_weight(self, batch_or_consumable):
        """
        Returns a string specifying the contents of the unit. Works both for batch and for consumable, since they both have unit as foreign key.
        """
        if batch_or_consumable.unit.contents == '':
            return "1 {} contains {} gr".format(batch_or_consumable.unit.abbr, batch_or_consumable.unit.weight)
        else:
            return "1 {} contains {} ({} gr)".format(batch_or_consumable.unit.abbr, batch_or_consumable.unit.contents, batch_or_consumable.unit.weight)

class ItemCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

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
    # original_id = models.IntegerField(blank=True, null=True)

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

    # def calc_stock(self): # calculates the stock as sum of the associated batches
    #     # doesn't work
    #     batches = Batch.objects.filter(consumable = self)
    #     for batch in batches:
    #         self.stock += batch.stock
    #     self.save()

    @property
    def stock_str(self):
        return "{} {}".format(format(self.calc_stock(), '.3f'), self.unit.abbr)

    def calc_stock(self):
        """
        Calculates the stock of a consumable. For each transaction, the unit of the batch gets divided through the unit of the consumable.
        For example, linseed oil (consumable) has the unit L (930 gr). B1 is a batch of linseed oil with the unit "500 ml bottle" (465 gr).
        If someone takes 1 bottle of B1, we will calculate: 1 * 465 / 930 = 1/2
        So for the consumable stock, it means a subtraction of 0.5
        """
        stock = 0
        for taking in Taking.objects.filter(batch__consumable=self):
            stock -= taking.amount * taking.batch.unit.weight / self.unit.weight
        for restitution in Restitution.objects.filter(batch__consumable=self):
            stock += restitution.amount * restitution.batch.unit.weight/self.unit.weight
        return stock

class ProductCategory(ItemCategory):
    pass

    def __str__(self):
        return self.name

class Product(Consumable):
    category = models.ForeignKey('ProductCategory', blank=True, null=True)
    density = models.FloatField(blank=True, null=True) # kg/l
    storability = models.FloatField(blank=True, null=True) # in days
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
    # sc_essential = models.CommaSeparatedIntegerField(max_length=50, blank=True, null=True) # list of essential storage conditions
    # sc_favorable = models.CommaSeparatedIntegerField(max_length=50, blank=True, null=True) # list of favorable storage conditions
    # sc_unfavorable = models.CommaSeparatedIntegerField(max_length=50, blank=True, null=True) # list of unfavorable storage conditions
    # sc_intolerable = models.CommaSeparatedIntegerField(max_length=50, blank=True, null=True) # list of intolerable storage conditions
    lossfactor = PercentField(default=0) # presumed lossfactor per month in % for this product (e.g. 3 => it is presumed to lose 3% of the stock every month of storage)
    official = models.PositiveSmallIntegerField(blank=True, null=True) # whether the product shall be uploaded in the online portal. 0 = not at all; 1 = without strage conditions; 2 = completely
    original_id = models.IntegerField(blank=True, null=True)


    def __str__(self):
        return "({}) {}".format(self.id, self.name)

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

class DeviceCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

class Device(Durable):
    category = models.ForeignKey('DeviceCategory')
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
    owner_account = models.ForeignKey('Account', blank=True, null=True)
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
    original_id = models.IntegerField(blank=True, null=True)

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
        return "{} ({} €/{})".format(self.name, format(self.price, '.2f'), self.unit.abbr) # , self.supplier, self.purchase_date

    def __str__(self):
        cont = ""
        try:
            if not self.unit.contents == '':
                cont = " ({} {})".format(self.unit.contents, self.unit.abbr)
        except AttributeError:
            pass
        return "B{} - {}{} by {} from {}".format(str(self.id), self.name, cont, self.supplier, self.purchase_date)

    @property
    def stock_str(self):
        return "{} {}".format(format(self.calc_stock(), '.3f'), self.unit.abbr)

    def calc_stock(self):
        stock = 0
        for taking in Taking.objects.filter(batch=self):
            stock -= taking.amount
        for restitution in Restitution.objects.filter(batch=self):
            stock += restitution.amount
        return stock

    @property
    def monthly_consumption_str(self):
        if self.monthly_consumption == 0:
            return "None"
        else:
            return "{} " " {}".format(format(self.monthly_consumption, '.3f'), self.unit.abbr)

    @property
    def taken_str(self):
        return "{} " " {}".format(format(self.taken, '.3f'), self.unit.abbr)

    def price_str_long(self):
        return "{} € per {}".format(format(self.price, '.2f'), self.unit.abbr)

    @property
    def price_str(self):
        return "{} €/{}".format(format(self.price,'.2f'), self.unit.abbr)

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

    @property
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
        return self.consumption_evaluation

class BatchStorage(models.Model):
    batch = models.ForeignKey('Batch')
    position = models.ForeignKey('StorageSpace')
    is_reserve = models.BooleanField(default=False) # set True if this storage space is not meant to be used for direct taking by participants (resp. for money: direct insertion)
    amount_approx = models.FloatField(blank=True, null=True) # e.g. 25 for a bag with 24.697 kg
    comment = models.TextField(blank=True)

class ContainerCategory(ItemCategory):
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
    processor = models.ForeignKey('Supplier', blank=True, null=True, related_name="processor") # the supplier from whom the product has been processed (optional; in many cases the distributor itself)
    grower = models.ForeignKey('Supplier', blank=True, null=True, related_name="grower") # the supplier from whom the product has been grown (optional; in many cases the distributor itself)
    variety = models.CharField(max_length=50, blank=True)
    vat = models.ForeignKey('VAT', related_name="VAT")
    distance_total = models.FloatField(blank=True, null=True) # replaces the distance of the supplier
    distance_add = models.FloatField(blank=True, null=True) # will be added to the distance of the supplier
    orderpos = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=True)
    supply_stock = models.FloatField(blank=True, null=True) # in product unit

    def __str__(self):
        return "{} from {}".format(self.consumable.name, self.distributor.name)

class Offer(models.Model):
    # Describes a specific offer of an offered consumable.
    general_offer = models.ForeignKey('GeneralOffer')
    parcel = models.FloatField() # how much g a single package or filling unit is (e.g. 25kg bag -> 25000; 1kg packages -> 1000; bulk with any amount in kg -> 1000)
    quantity = models.IntegerField() # how many parcels have to be taken at once
    favorite = models.BooleanField(default=False)
    official = models.PositiveSmallIntegerField(default=0) # whether the offer shall be uploaded in the online portal. 0 = not at all; 1 = without price information; 2 = completely
    total_price = models.FloatField(null=True, blank=True) #MoneyField; 
    discount = models.FloatField(null=True, blank=True) #MoneyField; 
    available = models.BooleanField(default=True)
    available_from = models.DateField(null=True, blank=True)
    available_until = models.DateField(null=True, blank=True)
    orderpos = models.IntegerField(null=True, blank=True)
    comment = models.TextField(blank=True)
    supply_stock = models.FloatField(null=True, blank=True) # in product unit (caution, this is the stock of this offer with its specific packaging)

    def __str__(self):
        return "{} ({}g)".format(self.general_offer, self.parcel)

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
    entered_by_user = models.ForeignKey('User')
    user_comment = models.TextField()
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

class TransactionType(models.Model):
    name = models.CharField(max_length=50)
    is_entry_type = models.BooleanField()
    to_balance = models.BooleanField()
    no = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    originator_account = models.ForeignKey('Account', related_name="originator_account")
    # involved_accounts = models.ManyToManyField('Account', related_name="involved_accounts", blank=True)
    entered_by_user = models.ForeignKey('User') # Person who typed in the transaction
    date = models.DateField()
    entry_date = models.DateField(auto_now_add=True) # Date when transaction is entered into the system
    amount = models.FloatField()
    comment = models.TextField(blank=True)
    value = models.FloatField(default=0, blank=True, null=True)
    #positive = models.NullBooleanField()
    #to_balance = models.NullBooleanField()
    status = models.ForeignKey('TransactionStatus', blank=True, null=True)
    transaction_type = models.ForeignKey('TransactionType', blank=True, null=True)

    def __str__(self):
        return "Tr {}: Account {} on {} (entered by {})".format(self.id, self.originator_account.name, self.date, self.entered_by_user.name)

    @property
    def comment_str(self):
        if self.comment == "":
            return ""
        else:
            return "'{}'".format(self.comment)

    @property
    def entry_details_str(self):
        return "entered on {} by {}".format(self.entry_date, self.entered_by_user.name)
    
    def value_str(self, account):
        # Returns the value of a transaction affecting the selected account, in the anchor currency, as a string.
        # In case the value shall be displayed generally, not regarding a specific account, provide account=0. The value will then be returned directly from the value attribute.
        if account == 0:
            return "{} €".format(format(self.value,'.2f'))
        else:
            # For the case multiple accounts are involved (transfer, cost sharing etc.), we have to choose the charge affecting the selected account.
            # If the account is both originator and participating, there can be 2 charges for the same account, that's why "filter" and a for loop are used instead of "get" (also for some potentially upcoming features)
            charges = Charge.objects.filter(transaction=self, account=account)
            value = 0
            for charge in charges:
                value += charge.value
            return "{} €".format(format(value,'.2f'))

    def balance_str(self, account):
    # Returns the resulting balance of the selected account after the transaction, in the anchor currency, as a string.
    # In an account-specific transaction list, this function will be applied to every listed transaction, so the column shows the account's balance change over time.
        # In some cases the balance of the originator account shall be shown (for example, in a batch-specific transaction list). If so, provide account=0
        if account == 0:
            account = self.originator_account.id
        # If the transaction doesn't affect the balance but the deposit, the balance field should be empty in this row (-> else case)
        # This If is a bit hacky, it assumes there aren't any other subclasses which don't affect the balance. The two lines below could be an alternative solution, not tested yet.
        if not self.__class__ == Depositation and not self.__class__ == PayOutDeposit:
        #linked_charges = Charge.objects.filter(transaction=self, account=account, to_balance=True)
        #if linked_charges:
            balance = 0
            # Filtering all the charges leading up to and including this transaction.
            # As the transactions in the list are sorted by date (and if same, by id), either the date must be lower, or the same but without a higher id.
            charges = Charge.objects.filter(account=account, to_balance=True).filter(Q(date__lt = self.date) | Q(Q(date = self.date) & Q(transaction__lte = self.id)))
            for charge in charges:
                #if charge.date < self.date or (charge.date == self.date and charge.id <= self.id): # if the Q combination above causes any problems, you can use this instead.
                balance += charge.value
            return "{} €".format(format(balance,'.2f'))
        else:
            return ""

class Charge(models.Model):
    # Defines a change in balance or deposit of one account. Most transactions will have one associated charge, transfers mostly two, cost sharing etc. will have multiple.
    transaction = models.ForeignKey('Transaction')
    account = models.ForeignKey('Account')
    value = models.FloatField(default=0) # MoneyField
    to_balance = models.BooleanField(default=True) # false = to deposit
    date = models.DateField()
    # perhaps a Boolean field for positive/negative

    def __str__(self):
        return "Tr{}: {}".format(self.transaction.id, self.account.name)

class BatchTransaction(Transaction):
    batch = models.ForeignKey('Batch')

class Taking(BatchTransaction): # taking of goods from balance
    type_name = "Taking" # for s in Transaction.__subclasses__(): print (s.__qualname__)

    def __str__(self):
        return "Tr{} {} on {}: {}: {} {} (submitted by {})".format(str(self.id), self.originator_account.name, self.date, self.batch, self.amount, self.batch.unit.abbr, self.entered_by_user.name)

    @property
    def type(self):
        return self.__class__

    def row_color(self, account):
        return ""

    def matter_str(self, account, show_contents=True, show_batch=True):
        if account == 0:
            originator = self.originator_account.name
        else:
            originator = "You"
        if show_batch == True:
            batch = " from batch no. {} ({} from {} in {} for {}€/{})".format(self.batch.id, self.batch.name, self.batch.supplier.name if self.batch.supplier else "", self.batch.supplier.broad_location if self.batch.supplier else "", format(self.batch.price,'.2f'), self.batch.unit.abbr)
        else:
            batch = ""
        # if self.batch.unit.continuous == False and not self.amount == 1:
        #     unit = self.batch.unit.plural
        # else:
        #     unit = self.batch.unit.abbr
        return "{} took {}{}".format(originator, self.batch.unit.display(self.amount, show_contents), batch), "", ""

    # @property
    # def type_name(self):
    #     return "Taking"

    # @property
    # def amount_str(self):
    #     return "{} {} from".format(self.amount, self.batch.unit.abbr)

    # def matter_str(self, account):
    #     return "batch no. {} ({} from {} in {} for {}€/{})".format(self.batch.id, self.batch.name, self.batch.supplier.name if self.batch.supplier else "", self.batch.supplier.broad_location if self.batch.supplier else "", format(self.batch.price,'.2f'), self.batch.unit.abbr)

    def perform(self):
        self.transaction_type = TransactionType.objects.get(no=1)
        self.save()
        batch = Batch.objects.get(pk=self.batch.id) # type(transaction.batch) == Batch
        batch.subtract_stock(self.amount)
        batch.add_taken(self.amount)
        batch.save()
        self.value = self.amount * batch.price * (-1)
        # account.subtract_balance(self.value)
        self.originator_account.add_taken(self.amount)
        self.originator_account.save()
        self.save()
        charge = Charge(transaction=self, account=self.originator_account, value=self.value, to_balance=True, date=self.date)
        charge.save()

    @property
    def details(self):
        pass

    def batch_stock_str(self):
        stock = 0
        for taking in Taking.objects.filter(batch=self.batch).filter(Q(date__lt = self.date) | Q(Q(date = self.date) & Q(id__lte = self.id))):
            stock -= taking.amount
        for restitution in Restitution.objects.filter(batch=self.batch).filter(Q(date__lt = self.date) | Q(Q(date = self.date) & Q(id__lte = self.id))):
            stock += restitution.amount
        return self.batch.unit.display(stock, False)

    def consumable_stock_str(self):
        stock = 0
        for taking in Taking.objects.filter(batch__consumable=self.batch.consumable).filter(Q(date__lt = self.date) | Q(Q(date = self.date) & Q(id__lte = self.id))):
            stock -= taking.amount * taking.batch.unit.weight / taking.batch.consumable.unit.weight
        for restitution in Restitution.objects.filter(batch__consumable=self.batch.consumable).filter(Q(date__lt = self.date) | Q(Q(date = self.date) & Q(id__lte = self.id))):
            stock += restitution.amount * restitution.batch.unit.weight / restitution.batch.consumable.unit.weight
        return self.batch.consumable.unit.display(stock)

    # def unperform(self): # TODO
    #     batch = Batch.objects.get(pk=self.batch.id) # type(transaction.batch) == Batch
    #     batch.add_stock(self.amount)
    #     batch.subtract_taken(self.amount)
    #     batch.save()
    #     self.value = self.amount * batch.price
    #     account = Account.objects.get(pk=self.originator_account.id)
    #     account.add_balance(self.value)
    #     account.subtract_taken(self.amount)
    #     account.save()
    #     self.save()

class Restitution(BatchTransaction): # return goods to the storage
    original_taking = models.ForeignKey('Taking', blank=True, null=True)
    approved_by = models.ForeignKey('User', blank=True, null=True)
    approval_comment = models.TextField(blank=True)

    def __str__(self):
        return "Tr{} {} on {}: {}: {} {} (submitted by {})".format(str(self.id), self.originator_account.name, self.date, self.batch, self.amount, self.batch.unit.abbr, self.entered_by_user.name)

    @property
    def type(self):
        return self.__class__

    def row_color(self, account):
        return ""

    def perform(self): # not tested yet
        self.transaction_type = TransactionType.objects.get(no=2)
        batch = Batch.objects.get(pk=self.batch.id) # type(transaction.batch) == Batch
        batch.add_stock(self.amount)
        batch.subtract_taken(self.amount)
        batch.save()
        self.value = self.amount * batch.price
        #account.add_balance(self.value)
        self.originator_account.subtract_taken(self.amount)
        self.originator_account.save()
        self.save()
        charge = Charge(transaction=self, account=self.originator_account, value=self.value, to_balance=True, date=self.date)
        charge.save()

    def matter_str(self, account, show_contents=True, show_batch=True):
        if account == 0:
            originator = self.originator_account.name
        else:
            originator = "You"
        if show_batch == True:
            batch = " to batch no. {} ({} from {} in {} for {}€/{})".format(self.batch.id, self.batch.name, self.batch.supplier.name if self.batch.supplier else "", self.batch.supplier.broad_location if self.batch.supplier else "", format(self.batch.price,'.2f'), self.batch.unit.abbr)
        else:
            batch = ""
        return "{} restituted {}{}".format(originator, self.batch.unit.display(self.amount, show_contents), batch), "", ""

    # @property
    # def type_name(self):
    #     return "Restitution"

    # @property
    # def amount_str(self):
    #     return "{} {} from".format(self.amount, self.batch.unit.abbr)

    # def matter_str(self, account):
    #     return "batch no. {} ({} from {} in {} for {}€/{})".format(self.batch.id, self.batch.name, self.batch.supplier.name, self.batch.supplier.broad_location, format(self.batch.price,'.2f'), self.batch.unit.abbr)

    def batch_stock_str(self):
        stock = 0
        for taking in Taking.objects.filter(batch=self.batch).filter(Q(date__lt = self.date) | Q(Q(date = self.date) & Q(id__lte = self.id))):
            stock -= taking.amount
        for restitution in Restitution.objects.filter(batch=self.batch).filter(Q(date__lt = self.date) | Q(Q(date = self.date) & Q(id__lte = self.id))):
            stock += restitution.amount
        return self.batch.unit.display(stock, False)

    def consumable_stock_str(self):
        stock = 0
        for taking in Taking.objects.filter(batch__consumable=self.batch.consumable).filter(Q(date__lt = self.date) | Q(Q(date = self.date) & Q(id__lte = self.id))):
            stock -= taking.amount * taking.batch.unit.weight / taking.batch.consumable.unit.weight
        for restitution in Restitution.objects.filter(batch__consumable=self.batch.consumable).filter(Q(date__lt = self.date) | Q(Q(date = self.date) & Q(id__lte = self.id))):
            stock += restitution.amount * restitution.batch.unit.weight / restitution.batch.consumable.unit.weight
        return self.batch.consumable.unit.display(stock)

class Inpayment(Transaction): # insertion of money to balance
    currency = models.ForeignKey('Currency') # , default=Currency.objects.get(pk=1)
    money_box = models.ForeignKey('MoneyBox')
    confirmed_by = models.ForeignKey('User', blank=True, null=True)
    confirmation_comment = models.TextField(blank=True)

    def __str__(self):
        return "Tr{} {} on {}: {} {} (submitted by {})".format(str(self.id), self.originator_account.name, self.date, self.amount, self.currency, self.entered_by_user.name)

    @property
    def type(self):
        return self.__class__

    def row_color(self, account):
        return ""

    def perform(self):
        self.transaction_type = TransactionType.objects.get(no=3)
        self.save()
        self.value = self.amount * self.currency.conversion_rate
        moneyboxstock = MoneyBoxStock.objects.get(money_box=self.money_box, currency=self.currency) # foreign key?
        moneyboxstock.inpayment(self.amount)
        moneyboxstock.save()
        #self.originator_account.add_balance(value)
        #self.originator_account.save()
        self.save()
        charge = Charge(transaction=self, account=self.originator_account, value=self.value, to_balance=True, date=self.date)
        charge.save()

    def matter_str(self, account):
        if account == 0:
            originator = self.originator_account.name
        else:
            originator = "You"
        if self.currency.name == "€":
            return "{} paid in {} € via {}".format(originator, format(self.amount,'.2f'), self.money_box.name), "", ""
        else:
            return "{} paid in {} {} ({} €) via {}".format(originator, format(self.amount,'.2f'), self.currency.name, format(self.value,'.2f'), self.money_box.name), "", ""

    # @property
    # def type_name(self):
    #     return "Inpayment"

    # @property
    # def amount_str(self):
    #     if self.currency.name == "€":
    #         return "{} {} ->".format(format(self.amount,'.2f'), self.currency.name)
    #     else:
    #         return "{} {} ({} €) ->".format(format(self.amount,'.2f'), self.currency.name, format(self.value,'.2f'))

    # def matter_str(self, account):
    #     if self.confirmed_by == None:
    #         return "{}, not confirmed yet".format(self.money_box.name)
    #     else:
    #         return "{}, confirmed by {} '{}'".format(self.money_box.name, self.confirmed_by.name, self.confirmation_comment)

class Depositation(Transaction): # insertion of money to deposit
    currency = models.ForeignKey('Currency') # , default=Currency.objects.get(pk=1)
    money_box = models.ForeignKey('MoneyBox')
    confirmed_by = models.ForeignKey('User', blank=True, null=True)
    confirmation_comment = models.TextField(blank=True)

    def __str__(self):
        return "Tr{} {} on {}: {} {} (submitted by {})".format(str(self.id), self.originator_account.name, self.date, self.amount, self.currency, self.entered_by_user.name), ""

    @property
    def type(self):
        return self.__class__

    def row_color(self, account):
        return ""

    def perform(self):
        self.transaction_type = TransactionType.objects.get(no=4)
        self.save()
        self.value = self.amount * self.currency.conversion_rate
        moneyboxstock = MoneyBoxStock.objects.get(money_box=self.money_box, currency=self.currency) # foreign key?
        moneyboxstock.inpayment(self.amount)
        moneyboxstock.save()
        # self.originator_account.add_deposit(self.value)
        # self.originator_account.save()
        self.save()
        charge = Charge(transaction=self, account=self.originator_account, value=self.value, to_balance=False, date=self.date)
        charge.save()

    def matter_str(self, account):
        if account == 0:
            originator = self.originator_account.name
        else:
            originator = "You"
        if self.currency.name == "€":
            return "{} deposited {} € via {}".format(originator, format(self.amount,'.2f'), self.money_box.name), "", ""
        else:
            return "{} deposited {} {} ({} €) via {}".format(originator, format(self.amount,'.2f'), self.currency.name, self.value, self.money_box.name), "", ""

    # @property
    # def type_name(self):
    #     return "Depositation"

    # @property
    # def amount_str(self):
    #     if self.currency.name == "€":
    #         return "{} {} ->".format(format(self.amount,'.2f'), self.currency.name)
    #     else:
    #         return "{} {} ({} €) ->".format(format(self.amount,'.2f'), self.currency.name, format(self.value,'.2f'))

    # def matter_str(self, account):
    #     if self.confirmed_by == None:
    #         return "{}, not confirmed yet".format(self.money_box.name)
    #     else:
    #         return "{}, confirmed by {} '{}'".format(self.money_box.name, self.confirmed_by.name, self.confirmation_comment)

class PayOutBalance(Transaction):
    currency = models.ForeignKey('Currency')
    money_box = models.ForeignKey('MoneyBox')

    # perform
    # self.transaction_type = TransactionType.objects.get(no=5)

    @property
    def type(self):
        return self.__class__

    def row_color(self, account):
        return ""

class PayOutDeposit(Transaction):
    currency = models.ForeignKey('Currency')
    money_box = models.ForeignKey('MoneyBox')

    # perform
    # self.transaction_type = TransactionType.objects.get(no=6)

    @property
    def type(self):
        return self.__class__

    def row_color(self, account):
        return ""

class Transfer(Transaction): # IDEE: Value will be calculated by  wird durch Angaben in Felder Amount und entweder Currency oder Batch berechnet
    recipient_account = models.ForeignKey('Account')
    currency = models.ForeignKey('Currency', blank=True, null=True)
    batch = models.ForeignKey('Batch', blank=True, null=True)

    @property
    def type(self):
        return self.__class__

    def row_color(self, account):
        return ""

    def perform(self):
        self.transaction_type = TransactionType.objects.get(no=7)
        # if not self.currency == None:
        #     self.value = self.amount * self.currency.conversion_rate
        # else:
        #     batch = Batch.objects.get(pk=self.batch.id) # type(transaction.batch) == Batch
        #     self.value = self.amount * batch.price
        self.save()
        cs = Charge(transaction=self, account=self.originator_account, value=self.amount*(-1), to_balance=True, date=self.date) # self.amount could be replaced by self.value if calculated per batch or currency
        cs.save()
        # self.sender_account.subtract_balance(self.value)
        # self.sender_account.save()
        cr = Charge(transaction=self, account=self.recipient_account, value=self.amount, to_balance=True, date=self.date) # self.amount could be replaced by self.value if calculated per batch or currency
        cr.save()
        # self.recipient_account.add_balance(self.value)
        # self.recipient_account.save()

    def matter_str(self, account):
        if account == 0:
            return "{} transferred {} € to {}".format(self.originator_account.name, format(self.amount,'.2f'), self.recipient_account.name), "", ""
        else:
            acc = Account.objects.get(pk=account)
            if self.originator_account == acc:
                return "You transferred {} € to {}".format(format(self.amount,'.2f'), self.recipient_account.name), "", ""
            elif self.recipient_account == acc:
                return "{} transferred {} € to you".format(self.originator_account.name, format(self.amount,'.2f')), "", ""
            else:
                return " ", "", ""


    # @property
    # def type_name(self):
    #     return "Transfer"

    # @property # TODO
    # def amount_str(self):
    #     if self.currency.name == "€":
    #         return "{} {}".format(format(self.amount,'.2f'), self.currency.name)
    #     else:
    #         return "{} {} ({} €)".format(format(self.amount,'.2f'), self.currency.name, format(self.value,'.2f'))

    # def matter_str(self, account):
    #     acc = Account.objects.get(pk=account)
    #     if acc == self.originator_account:
    #         return "sent to {}".format(self.recipient_account.name)
    #     elif acc == self.recipient_account:
    #         return "sent by {}".format(self.originator_account.name)
    #     else:
    #         return " "


class ShareTransaction(Transaction):
    participating_accounts = models.ManyToManyField('Account')
    shares = models.ManyToManyField('Charge', blank=True, related_name="shares")
    originator_share = models.ForeignKey('Charge', blank=True, null=True, related_name="originator_share")
    approved_by = models.ForeignKey('User', blank=True, null=True)
    approval_comment = models.TextField(blank=True)

    def perform(self, transaction_type_id, participating_accounts):
        self.transaction_type = TransactionType.objects.get(no=transaction_type_id)
        self.save()
        currency = Currency.objects.get(pk=1)
        if not currency == None:
            self.value = self.amount * currency.conversion_rate
        else:
            batch = Batch.objects.get(pk=self.batch.id) # type(transaction.batch) == Batch
            self.value = self.amount * batch.price
        sum_of_rates = 0
        for account in participating_accounts: # self.participating_accounts.all()
            rate = account.calc_rate(datetime=self.date)
            sum_of_rates += rate
            if rate > 0:
                self.participating_accounts.add(account)
        if sum_of_rates > 0:
            if self.transaction_type.no == 8 or self.transaction_type.no == 11:
                type_factor = -1
            else:
                type_factor = 1
            co = Charge(transaction=self, account=self.originator_account, value=self.value*type_factor*(-1), to_balance=True, date=self.date)
            co.save()
            self.originator_share = co
            for account in self.participating_accounts.all():
                share = type_factor * self.value * account.calc_rate(datetime=self.date) / sum_of_rates
                cp = Charge(transaction=self, account=account, value=share, to_balance=True, date=self.date)
                cp.save()
                self.shares.add(cp)
        else:
            print("Error: Sum of current account rates is 0")
        self.save()

    def matter_str(self, account):
        if self.transaction_type.no == 8:
            str_part_1 = "divided costs of"
            str_part_2 = "among"
        elif self.transaction_type.no == 9:
            str_part_1 = "divided proceeds of"
            str_part_2 = "among"
        elif self.transaction_type.no == 10:
            str_part_1 = "donated"
            str_part_2 = "to"
        elif self.transaction_type.no == 11:
            str_part_1 = "recovered"
            str_part_2 = "from"
        count = self.participating_accounts.count()
        if account == 0:
            return "{} {} {} € {} ".format(self.originator_account.name, str_part_1, format(self.amount,'.2f'), str_part_2), "{} participants".format(count), ""
        else:
            acc = Account.objects.get(pk=account)
            if self.originator_account == acc:
                originator = "You"
            else:
                originator = self.originator_account.name
            if self.participating_accounts.filter(pk=account).count() and self.originator_account == acc:
                share = self.shares.get(account=acc).value # Charge.objects.filter(transaction=self, account=acc)[0].value
                return "{} {} {} € {} ".format(originator, str_part_1, format(self.amount,'.2f'), str_part_2), "{} participants".format(count), " (own share: {} €)".format(format(share, '.2f'))
            else:
                return "{} {} {} € {} ".format(originator, str_part_1, format(self.amount,'.2f'), str_part_2), "{} participants".format(count), ""

class CostSharing(ShareTransaction):

    @property
    def type(self):
        return self.__class__

    def row_color(self, account):
        acc = Account.objects.get(pk=account)
        if self.originator_account == acc:
            return "#77ff70" # TODO
        elif self.participating_accounts.filter(pk=account).count():
            return "#f77770" # TODO

class ProceedsSharing(ShareTransaction):

    @property
    def type(self):
        return self.__class__

    def row_color(self, account):
        return ""

    # def matter_str(self, account):
    #     count = self.participating_accounts.count()
    #     if account == 0:
    #         return "{} divided proceeds of {} € among ".format(self.originator_account.name, format(self.amount,'.2f')), "{} participants".format(count), ""
    #     else:
    #         acc = Account.objects.get(pk=account)
    #         if self.originator_account == acc:
    #             if self.participating_accounts.filter(pk=account).count():
    #                 share = Charge.objects.filter(transaction=self, account=acc)[1].value
    #                 return "You divided proceeds of {} € among ".format(format(self.amount,'.2f')), "{} participants".format(count), " (own share: {} €)".format(format(share, '.2f'))
    #             else:
    #                 return "You divided proceeds of {} € among ".format(format(self.amount,'.2f')), "{} participants".format(count), ""
    #         elif self.participating_accounts.filter(pk=account).count():
    #              return "{} divided proceeds of {} € among ".format(self.originator_account.name, format(self.amount,'.2f')), "{} participants".format(count), ""
    #         else:
    #              return " ", "", ""

    # def amount_str(self):
    #     return "{} €".format(format(self.amount,'.2f'))

    # def matter_str(self, account):
    #     count = self.participating_accounts.count()
    #     acc = Account.objects.get(pk=account)
    #     if acc == self.originator_account:
    #         if self.participating_accounts.filter(pk=account).count():
    #             share = Charge.objects.filter(transaction=self, account=acc)[1].value
    #             return "proportioned on {} participants (own share: {} €)".format(count, format(share,'.2f'))
    #         elif not self.participating_accounts.filter(pk=account).count():
    #             return "proportioned on {} participants".format(count)
    #         else:
    #             return " "
    #     elif self.participating_accounts.filter(pk=account).count():
    #         return "shared by {} (proportioned on {} recipients)".format(self.originator_account.name, count)
    #     else:
    #         return " "

class Donation(ShareTransaction):

    @property
    def type(self):
        return self.__class__

    def row_color(self, account):
        return ""


    # def matter_str(self, account):
    #     count = self.participating_accounts.count()
    #     acc = Account.objects.get(pk=account)
    #     if account == self.originator_account:
    #         return "proportioned on {} participants".format(count)
    #     elif self.participating_accounts.filter(pk=account).count():
    #         return "donated by {} (proportioned on {} recipients)".format(self.originator_account.name, count)
    #     else:
    #         pass

    # def perform(self, participating_accounts):
    #     self.transaction_type = TransactionType.objects.get(no=10)
    #     self.save()
    #     currency = Currency.objects.get(pk=1)
    #     if not currency == None:
    #         self.value = self.amount * currency.conversion_rate
    #     else:
    #         batch = Batch.objects.get(pk=self.batch.id) # type(transaction.batch) == Batch
    #         self.value = self.amount * batch.price
    #     sum_of_rates = 0
    #     for account in participating_accounts: # self.participating_accounts.all()
    #         rate = account.calc_rate(datetime=self.date)
    #         sum_of_rates += rate
    #         if rate > 0:
    #             self.participating_accounts.add(account)
    #     if sum_of_rates > 0:
    #         co = Charge(transaction=self, account=self.originator_account, value=self.value*(-1), to_balance=True, date=self.date)
    #         co.save()
    #         self.originator_charge = co
    #         for account in self.participating_accounts.all():
    #             share = self.value * account.calc_rate(datetime=self.date) / sum_of_rates
    #             cp = Charge(transaction=self, account=account, value=share, to_balance=True, date=self.date)
    #             cp.save()
    #             self.shares.add(cp)
    #     else:
    #         print("Error: Sum of current account rates is 0")
    #     self.save()

class Recovery(ShareTransaction): # donation backwards

    @property
    def type(self):
        return self.__class__

    def row_color(self, account):
        acc = Account.objects.get(pk=account)
        if self.originator_account == acc:
            return "#77ff70" # TODO
        elif self.participating_accounts.filter(pk=account).count():
            return "" # TODO

    # def matter_str(self, account):
    #     count = self.participating_accounts.count()
    #     if account == 0:
    #         return "{} recovered {} € from ".format(self.originator_account.name, format(self.amount,'.2f')), "{} participants".format(count), ""
    #     else:
    #         acc = Account.objects.get(pk=account)
    #         if self.originator_account == acc:
    #             return "You recovered {} € from ".format(format(self.amount,'.2f')), "{} participants".format(count), ""
    #         elif self.participating_accounts.filter(pk=account).count():
    #              return "{} recovered {} € from ".format(self.originator_account.name, format(self.amount,'.2f')), "{} participants".format(count), ""
    #         else:
    #              return " ", "", ""

    # def perform(self, participating_accounts):
    #     self.transaction_type = TransactionType.objects.get(no=11)
    #     self.save()
    #     currency = Currency.objects.get(pk=1)
    #     if not currency == None:
    #         self.value = self.amount * currency.conversion_rate
    #     else:
    #         batch = Batch.objects.get(pk=self.batch.id) # type(transaction.batch) == Batch
    #         self.value = self.amount * batch.price
    #     sum_of_rates = 0
    #     for account in participating_accounts: # self.participating_accounts.all()
    #         rate = account.calc_rate(datetime=self.date)
    #         sum_of_rates += rate
    #         if rate > 0:
    #             self.participating_accounts.add(account)
    #     if sum_of_rates > 0:
    #         co = Charge(transaction=self, account=self.originator_account, value=self.value*(-1), to_balance=True, date=self.date)
    #         co.save()
    #         self.originator_charge = co
    #         for account in self.participating_accounts.all():
    #             share = self.value * account.calc_rate(datetime=self.date) / sum_of_rates
    #             cp = Charge(transaction=self, account=account, value=share, to_balance=True, date=self.date)
    #             cp.save()
    #             self.shares.add(cp)
    #     else:
    #         print("Error: Sum of current account rates is 0")
    #     self.save()