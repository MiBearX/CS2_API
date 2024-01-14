from flask import Flask, jsonify
from flask_restful import Resource, Api
import sqlite3
import json
from cs2 import csgoStashItems, printItem

app = Flask("CS2_API")
api = Api(app)
app.json.sort_keys = False


def validateWeaponType(wType):
    lowerWType = wType.lower()
    for formattedWeaponType in csgoStashItems.keys():
        if lowerWType == formattedWeaponType.lower():
            return formattedWeaponType


def validateWeaponName(wName, wType):
    lowerWName = wName.lower()
    for formattedWName in csgoStashItems[wType]:
        if lowerWName == formattedWName.lower():
            return formattedWName.replace("+", " ")

def processSQLRow(sqlRow, retData):
    (id, weaponName, skinName, rarity, weaponType, collection, imgURL, price, stPrice) = sqlRow
    retData.append({
        "weapon" : weaponName,
        "skinName" : skinName,
        "rarity" : rarity,
        "category" : weaponType,
        "collection" : collection,
        "imgURL" : imgURL,
        "price" : price,
        "StatTrackPrice" : stPrice
        })
    #printItem(weaponName, skinName, rarity, weaponType, collection, imgURL, price, stPrice)


class Weapon(Resource):

    def get(self, weaponType = None, weaponName = None):
        connection = sqlite3.connect("cs2Skins.db")
        cursor = connection.cursor()
        retData = []
        if weaponType is None:
            # queries all weapons
            query = "SELECT * FROM skins"
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                processSQLRow(row, retData)
        elif weaponName is None:
            # queries all skins for specific weapon type
            weaponType = validateWeaponType(weaponType)
            query = "SELECT * FROM skins WHERE gun_type = ?"
            cursor.execute(query, (weaponType,))
            rows = cursor.fetchall()
            for row in rows:
                processSQLRow(row, retData)
        else:
            # queries skins for specific gun
            weaponName = validateWeaponName(weaponName, validateWeaponType(weaponType))
            query = "SELECT * FROM skins WHERE gun_name = ?"
            cursor.execute(query, (weaponName,))
            rows = cursor.fetchall()
            for row in rows:
                processSQLRow(row, retData)
        

        
        connection.commit()
        connection.close()
        return jsonify(retData)

api.add_resource(Weapon, "/weapons", "/weapons/<string:weaponType>", "/weapons/<string:weaponType>/<string:weaponName>")


if __name__ == "__main__":
    #jsonData = json.dumps(csgoStashItems, indent = 3)
    
    app.run(debug=True)