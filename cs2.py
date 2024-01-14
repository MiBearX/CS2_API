import json
import requests
from bs4 import BeautifulSoup
import sqlite3


csgoStashItems = {
    "Pistol" : ["CZ75-Auto", "Desert+Eagle", "Dual+Berettas", "Five-SeveN", "Glock-18", "P2000", "P250", 
                 "R8+Revolver", "Tec-9", "USP-S"],
    "SMG" : ["MAC-10", "MP5-SD", "MP7", "MP9", "PP-Bizon", "P90", "UMP-45"],
    "Shotgun" : ["MAG-7", "Nova", "Sawed-Off", "XM1014"],
    "Machinegun" : ["M249", "Negev"],
    "Rifle" : ["AK-47", "AUG", "AWP", "FAMAS", "G3SG1", "Galil+AR", "M4A1-S", "M4A4", "SCAR-20", "SG+553", "SSG+08"],
    "Knife" : ["Bayonet", "Bowie+Knife", "Butterfly+Knife", "Classic+Knife", "Falchion+Knife", "Flip+Knife", "Gut+Knife", 
                "Huntsman+Knife", "Karambit", "M9+Bayonet", "Navaja+Knife", "Nomad+Knife", "Paracord+Knife", "Shadow+Daggers", 
                "Skeleton+Knife", "Stiletto+Knife", "Survival+Knife", "Talon+Knife", "Ursus+Knife"]
                    }


def setupSQLDatabase():
    connection = sqlite3.connect("cs2Skins.db")
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gun_name TEXT,
            skin_name TEXT,
            rarity TEXT,
            gun_type TEXT,
            collection TEXT,
            image_url TEXT,
            price TEXT,
            stattrak_price TEXT
        )'''
    )

    connection.commit()
    connection.close()

def insertSkin(gunName, skinName, rarity, gun_type, collection, imageURL, price, st_Price):
    connection = sqlite3.connect("cs2Skins.db")
    cursor = connection.cursor()

    cursor.execute('''
    INSERT INTO skins(gun_name, skin_name, rarity, gun_type, collection, image_url, price, stattrak_price)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (gunName, skinName, rarity, gun_type, collection, imageURL, price, st_Price)
    )

    connection.commit()
    connection.close()


def updateSkin(gunName, skinName, rarity, gun_type, collection, imageURL, price, st_Price):
    connection = sqlite3.connect("cs2Skins.db")
    cursor = connection.cursor()
    cursor.execute('''
            UPDATE skins
            SET rarity = ?, gun_type = ?, collection = ?, image_url = ?, price = ?, stattrak_price = ?
            WHERE gun_name = ?, skin_name = ?
        ''', (rarity, gun_type, collection, imageURL, price, st_Price, gunName, skinName))
    
    connection.commit()
    connection.close()


def printItem(gunName, skinName, rarity, gunType, collection, imageURL, price, stPrice):
    print(gunName)
    print(skinName)
    print(rarity)
    print(gunType)
    print(price)
    print(f"Stattrack: {stPrice}")
    print(collection)
    print(imageURL)
    print()
    


def getIntPrice(priceString): # unfinished
    strList = str(priceString).split()
    return strList[-1] # this currently returns highest price (factory new)


def scrapeGunsCSGOSTASH(weaponName):
    basecsgoStashURL = "https://csgostash.com/weapon/"
    csgoStashURL = basecsgoStashURL + weaponName
    currentPage = requests.get(csgoStashURL)
    soup = BeautifulSoup(currentPage.content, "html.parser")
    weaponHeader = soup.find("div", class_="col-lg-12 text-center col-widen content-header").get_text()
    weaponTitle = weaponHeader.split()[:-1]
    weaponTitle = " ".join(weaponTitle)


    skins = soup.find_all("div", class_="col-lg-4 col-md-6 col-widen text-center")
    for skin in skins:
        info = skin.find("div", class_="well result-box nomargin")
        skinName = info.find("h3").get_text()

        if info.find("p", class_="nomargin") == None: # handles edge case where function scrapes a default gun, no rarity
            rarityAndType = None
            rarity = None
            gunType = None
        else:
            rarityAndType = info.find("p", class_="nomargin").get_text()
            rarity = str(rarityAndType).split()[:-1]
            if rarity[-1] == "Sniper":
                rarity = rarity[:-1] # omit "Sniper" from database
            
            gunType = str(rarityAndType).split()[-1]
            if rarity[-1] == "Machine":
                gunType = gunType.lower()
                gunType = rarity[-1] + gunType
                rarity = rarity[:-1]
            rarity = " ".join(rarity)

        imageURL = info.find("img")["src"]
        priceDivs = info.find_all("div", class_="price")
        #initalize price variables
        priceStr = None
        st_priceStr = None
        count = 0

        for priceDiv in priceDivs: # get both regular and stattrack prices
            if priceDiv == None or priceDiv.find("p").find("a") == None: # if skin is missing price data, skip
                count += 1
                continue

            if count == 0:
                priceStr = priceDiv.find("p").find("a").get_text()
            elif count == 1:
                st_priceStr = priceDiv.find("p").find("a").get_text()
            else:
                priceStr = None
                st_priceStr = None
            count += 1

            +count

        price = getIntPrice(priceStr)
        stPrice = getIntPrice(st_priceStr)

        collectionDiv = info.find("div", class_="collection")
        if collectionDiv:
            collection = collectionDiv.get_text().strip()
        else:
            collection = None
            

        insertSkin(weaponTitle, skinName, rarity, gunType, collection, imageURL, price, stPrice)
        printItem(weaponTitle, skinName, rarity, gunType, collection, imageURL, price, stPrice)


def scrapeKnivesCSGOSTASH(knifeName):
    basecsgoStashURL = "https://csgostash.com/weapon/"
    csgoStashURL = basecsgoStashURL + knifeName
    currentPage = requests.get(csgoStashURL)
    soup = BeautifulSoup(currentPage.content, "html.parser")
    weaponHeader = soup.find("div", class_="col-lg-12 text-center col-widen content-header").get_text()
    weaponTitle = weaponHeader.split()[:-1]
    weaponTitle = " ".join(weaponTitle)


    skins = soup.find_all("div", class_="col-lg-4 col-md-6 col-widen text-center")
    for skin in skins:
        info = skin.find("div", class_="well result-box nomargin")
        skinName = info.find("h3").get_text()

        if info.find("p", class_="nomargin") == None: # handles edge case where function scrapes a default gun, no rarity
            rarityAndType = None
            rarity = None
            gunType = None
        else:
            rarityAndType = info.find("p", class_="nomargin").get_text()
            rarity = str(rarityAndType).split()[:-1]
            if rarity[-1] == "Sniper":
                rarity = rarity[:-1] # omit "Sniper" from database
            rarity = " ".join(rarity)
            gunType = str(rarityAndType).split()[-1]
            

        imageURL = info.find("img")["src"]
        priceDivs = info.find_all("div", class_="price")
        #initalize price variables
        priceStr = None
        st_priceStr = None
        count = 0

        for priceDiv in priceDivs: # get both regular and stattrack prices
            if priceDiv == None or priceDiv.find("p").find("a") == None: # if skin is missing price data, skip
                count += 1
                continue

            if count == 0:
                priceStr = priceDiv.find("p").find("a").get_text()
            elif count == 1:
                st_priceStr = priceDiv.find("p").find("a").get_text()
            else:
                priceStr = None
                st_priceStr = None
            count += 1

            +count

        price = getIntPrice(priceStr)
        stPrice = getIntPrice(st_priceStr)

        collectionDiv = info.find("div", class_="collection")
        collection = "Multiple Cases/Collections"
            

        insertSkin(weaponTitle, skinName, rarity, gunType, collection, imageURL, price, stPrice)
        printItem(weaponTitle, skinName, rarity, gunType, collection, imageURL, price, stPrice)


def scrapeGlovesCSGOStash():
    page = 1
    while page <= 2:
        csgoStashURL = f"https://csgostash.com/gloves?page={page}"
        currentPage = requests.get(csgoStashURL)
        soup = BeautifulSoup(currentPage.content, "html.parser")


        skins = soup.find_all("div", class_="col-lg-4 col-md-6 col-widen text-center")
        for skin in skins:
            info = skin.find("div", class_="well result-box nomargin")
            skinName = info.find("h3").get_text()
            skinName = skinName.split(" | ")
            weaponTitle = skinName[0]
            skinName = skinName[-1]

            if info.find("p", class_="nomargin") == None: # handles edge case where function scrapes a default weapon, no rarity
                rarityAndType = None
                rarity = None
                gunType = None
            else:
                rarityAndType = info.find("p", class_="nomargin").get_text()
                rarity = str(rarityAndType).split()[:-1]
                if rarity[-1] == "Sniper":
                    rarity = rarity[:-1] # omit "Sniper" from database
                rarity = " ".join(rarity)
                gunType = str(rarityAndType).split()[-1]
            

            imageURL = info.find("img")["src"]
            priceDivs = info.find_all("div", class_="price")
            #initalize price variables
            priceStr = None
            st_priceStr = None
            count = 0

            for priceDiv in priceDivs: # get both regular and stattrack prices
                if priceDiv == None or priceDiv.find("p").find("a") == None: # if skin is missing price data, skip
                    count += 1
                    continue

                if count == 0:
                    priceStr = priceDiv.find("p").find("a").get_text()
                elif count == 1:
                    st_priceStr = priceDiv.find("p").find("a").get_text()
                else:
                    priceStr = None
                    st_priceStr = None
                count += 1

                +count

            price = getIntPrice(priceStr)
            stPrice = getIntPrice(st_priceStr)

            collectionDiv = info.find("div", class_="collection")
            collection = "Multiple Cases"
                

            insertSkin(weaponTitle, skinName, rarity, gunType, collection, imageURL, price, stPrice)
            printItem(weaponTitle, skinName, rarity, gunType, collection, imageURL, price, stPrice)
        page += 1
        


def scrapeAllGuns():
    for type in csgoStashItems:
        if type == "Knife":
            continue
        for gunName in csgoStashItems[type]:
            scrapeGunsCSGOSTASH(gunName)


def scrapeAllKnives():
    for knifeName in csgoStashItems["Knife"]:
        scrapeKnivesCSGOSTASH(knifeName)


def scrapeallItems():
    for type in csgoStashItems:
        if type == "Knife":
            for knifeName in csgoStashItems[type]:
                scrapeKnivesCSGOSTASH(knifeName)
            continue
        for gunName in csgoStashItems[type]:
            scrapeGunsCSGOSTASH(gunName)

    scrapeGlovesCSGOStash()

def viewData():
    connection = sqlite3.connect("cs2Skins.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM skins WHERE gun_type = 'Rifle'")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    connection.close()
    

if __name__ == "__main__":
    setupSQLDatabase()
    scrapeallItems()
    #viewData()
    
    