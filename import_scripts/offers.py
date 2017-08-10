# -*- coding: utf-8 -*-

import csv
import datetime
from core import models
from difflib import get_close_matches
import operator

"""
Questions:
- Special characters like umlaute and ß are ignored with errors='ignore', how can we read them?
"""

def identify_consumable(name):
    pass

def oechsler():
    with open('import_scripts/Oechsler Preisliste.csv', newline='', encoding='utf-8', errors='ignore') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        distributor = models.Supplier.objects.filter(name='Oechsler')[0]
        vat7 = models.VAT.objects.filter(percentage=7)[0]
        unit_kg = models.Unit.objects.get(abbr='kg')
        existing_gos = models.GeneralOffer.objects.filter(distributor=distributor)
        existing_os = models.Offer.objects.filter(general_offer__in=existing_gos)
        checked_gos = list()
        activated_gos = list()
        updated_gos = list()
        new_gos = list()
        checked_os = list()
        updated_os = list()
        activated_os = list()
        new_os = list()
        cnames = list()
        for c in models.Consumable.objects.all():
            cnames.append(c.name)
        for index,row in enumerate(reader):
            name = str(row[0])
            matches = get_close_matches(name, cnames, n=1)
            if matches:
                consumable = models.Consumable.objects.get(name=matches[0])
            else:
                consumable = None # create consumable
            if consumable:
                o_go_id = index
                egos = existing_gos.filter(original_id=o_go_id)
                if egos:
                    go = egos[0]
                    if go.original_active == False:
                        go.original_active = True
                        go.save()
                        activated_gos.append(go)
                    if not go.consumable == consumable or not go.original_name == name:
                        go.consumable = consumable
                        go.original_name = name
                        go.save()
                        updated_gos.append(go)
                    checked_gos.append(go)
                else:
                    go = models.GeneralOffer(consumable=consumable, distributor=distributor, vat=vat7, original_id=o_go_id, original_name=name, original_active=True)
                    go.save()
                    new_gos.append(go)
                # for column in row[1:4]:
                oos = list()
                if row[1]:
                    oo = list()
                    oo.append(index*4+1) # oo[0]  o_o_id
                    oo.append(0.5) # oo[1]
                    oo.append(row[1].replace(',', '.')[0:-2]) # oo[2]
                    oos.append(oo)
                if row[2]:
                    oo = list()
                    oo.append(index*4+2) # oo[0]  o_o_id
                    oo.append(1) # oo[1]
                    oo.append(row[2].replace(',', '.')[0:-2]) # oo[2]
                    oos.append(oo)
                if row[3]:
                    oo = list()
                    oo.append(index*4+3) # oo[0]  o_o_id
                    oo.append(5) # oo[1]
                    oo.append(row[3].replace(',', '.')[0:-2]) # oo[2]
                    oos.append(oo)
                if row[4]:
                    oo = list()
                    oo.append(index*4+4) # oo[0]  o_o_id
                    oo.append(25) # oo[1]
                    oo.append(row[4].replace(',', '.')[0:-2]) # oo[2]
                    oos.append(oo)

                eos = existing_os.filter(general_offer=go)
                for oo in oos:
                    eo_try = eos.filter(original_id=oo[0])
                    if eo_try:
                        o = eo_try[0]
                        if o.original_active == False:
                            o.original_active = True
                            o.save()
                            activated_os.append(o)
                        if not float(o.parcel) == float(oo[1]) or not float(o.original_total_price) == float(oo[2]): # if we don't use float(), there are differences like 25 <> 25.0
                            o.parcel = oo[1]
                            o.total_price = oo[2]
                            o.original_total_price = oo[2]
                            o.save()
                            updated_os.append(o)
                        checked_os.append(o)
                    else:
                        o = models.Offer(general_offer=go, unit=unit_kg, parcel=oo[1], continuous=False, total_price=oo[2], original_id=oo[0], original_total_price=oo[2], original_active=True)
                        o.save()
                        new_os.append(o)
        egos = set(existing_gos)
        cgos = set(checked_gos)
        ngos = set(new_gos)
        unchecked_gos = [item for item in egos if item not in cgos and item not in ngos and not item.original_active == False]
        # unchecked_gos = map(object., set(existing_gos), set(checked_gos))
        for go in unchecked_gos:
            go.original_active = False
            go.save()
        # unchecked_os = map(object.__sub__, set(existing_os), set(checked_os))
        # unchecked_os = list(set(existing_os) - set(checked_os))
        eos = set(existing_os)
        cos = set(checked_os)
        nos = set(new_os)
        unchecked_os = [item for item in eos if item not in cos and item not in nos and not item.original_active == False]
        for o in unchecked_os:
            o.original_active = False
            o.save()
        print('Deactivated general offers:', unchecked_gos)
        print('Activated general offers:', activated_gos)
        print('Updated general offers: ', updated_gos)
        print('New general offers: ', new_gos)
        print('Deactivated offers:', unchecked_os)
        print('Activated offers:', activated_os)
        print('Updated offers: ', updated_os)
        print('New offers: ', new_os)


                #     o = models.Offer(general_offer=go, unit=unit_kg, parcel=0.5, continuous=False, total_price=row[1].replace(',', '.')[0:-2], original_id=o_o_id)
                #     o.save()
                # if row[2]:
                #     o_o_id = (index(row)-1)*4+2
                #     o = models.Offer(general_offer=go, unit=unit_kg, parcel=1, continuous=False, total_price=row[2].replace(',', '.')[0:-2], original_id=o_o_id)
                #     o.save()
                # if row[3]:
                #     o_o_id = (index(row)-1)*4+3
                #     o = models.Offer(general_offer=go, unit=unit_kg, parcel=5, continuous=False, total_price=row[3].replace(',', '.')[0:-2], original_id=o_o_id)
                #     o.save()
                # if row[4]:
                #     o_o_id = (index(row)-1)*4+4
                #     o = models.Offer(general_offer=go, unit=unit_kg, parcel=25, continuous=False, total_price=row[4].replace(',', '.')[0:-2], original_id=o_o_id)
                #     o.save()