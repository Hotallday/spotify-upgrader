import os,sys,json,requests,time,random
import peewee
import datetime
from multiprocessing.pool import ThreadPool
from peewee import *
#db = MySQLDatabase(host = '127.0.0.1',database ='spotify', user='root', passwd='')
db = MySQLDatabase(host = '35.186.162.56',database ='spotify', user='root', passwd='ofeenel')
class family_accounts(peewee.Model):
        ID = peewee.SmallIntegerField()
        Username = peewee.CharField(unique=True)
        Password = peewee.CharField()
        Country = peewee.FixedCharField()
        a_s = peewee.IntegerField()
        last_check = peewee.DateTimeField()
        Tries = peewee.IntegerField()
        class Meta:
              database = db
class spotify_upgrades(peewee.Model):
        ID = peewee.IntegerField()
        Username = peewee.CharField(unique=True)
        Password = peewee.CharField()
        MembershipID = peewee.CharField(null = True)
        date_upgraded = peewee.DateTimeField()
        transaction_id = peewee.CharField(null = True)
        FID = peewee.SmallIntegerField(null= True)
        warranty = peewee.DateTimeField()
        class Meta:
              database = db
class Checker:
    def __init__(self):      
        self.API = ["http://35.237.185.41:8000","http://35.185.205.157:8000","http://35.230.149.15:8000"]
        #self.API = ["http://127.0.0.1:5002"]
        self.MembersDELETED = 0
        self.ACCOUNTNEEDREUPGRADE = 0
        self.FAMILYACCOUNTS = family_accounts.select().where(datetime.datetime.now() + datetime.timedelta(minutes = -30) > family_accounts.last_check).limit(50)
        
        self.FAMILYACCOUNTSREMOVED = 0
        self.FAMILYACCOUNTSWORKING = 0
        print("[CHECKING [{0}] FAMILY ACCOUNTS]".format(len(self.FAMILYACCOUNTS)))
        print("-------------------------")
        if len(self.FAMILYACCOUNTS) > 0:
            pool = ThreadPool(10)
            pool.map(self.Start,self.FAMILYACCOUNTS)
            pool.close()
            pool.join()

        print("     - [{0}] None shop accounts deleted.".format(self.MembersDELETED))
        print("     - [{0}] Shop accounts needed to be reupgraded.".format(self.ACCOUNTNEEDREUPGRADE))

        print("     - [{0}] Family accounts deleted.".format(self.FAMILYACCOUNTSREMOVED))

        print("     - [{0}] Family accounts working.".format(self.FAMILYACCOUNTSWORKING))
        print("__________________________")
    def Remove(self,acc,memberid,client):
        check = spotify_upgrades.select().where(spotify_upgrades.MembershipID == memberid)
        if len(check) == 0:
            request = client.delete(random.choice(self.API) +"/family/" + acc.Username + ":" + acc.Password+"/" + memberid,verify = True)
            if request.status_code == 204:
                  acc.a_s += 1                
                  self.MembersDELETED += 1
    def deleteFamily(self,acc):
        check = spotify_upgrades.select().where(spotify_upgrades.FID == acc.ID)
        for x in check:
            x.MembershipID = None
            x.FID = None
            x.save()
            self.ACCOUNTNEEDREUPGRADE +=1
        acc.delete_instance()
        self.FAMILYACCOUNTSREMOVED += 1
    def Start(self,acc):
         acc.last_check = datetime.datetime.now()
         acc.a_s = 0
         client = requests.Session()
         try: request = client.get(random.choice(self.API) +"/family/" + acc.Username + ":" + acc.Password,verify = True)
         except requests.exceptions.RequestException: return
         if request.status_code == 200:
            self.FAMILYACCOUNTSWORKING += 1
            acc.Tries = 0
            response = json.loads(request.text)
            if response["premium"] == True:             
               if response["country"]:
                  acc.Country = response["country"]
               if len(response["members"]) > 0:
                  for x in response["members"]:
                      self.Remove(acc,x["membershipUuid"],client)
               if response["available_spots"]:
                  acc.a_s += response["available_spots"]
               if len(response["invites"]) > 0:
                  acc.a_s += len(response["invites"])
            else: self.deleteFamily(acc)
            if response["premium"] == True and acc.a_s == 0 and response["can_invite"] == False: self.deleteFamily(acc)
         if request.status_code == 400:
            response = json.loads(request.text)
            if response["errors"]:
               if response["errors"][0]["message"]  and response["errors"][0]["message"] == "Invalid Credentials":
                  acc.Tries +=1
                  if acc.Tries >= 5: self.deleteFamily(acc)
         acc.save()
if __name__ == '__main__': 
    while 1:
      Checker()
      time.sleep(5)