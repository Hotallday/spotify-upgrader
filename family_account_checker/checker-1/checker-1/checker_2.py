import os,sys,json,requests,time,random
import peewee
import datetime
from multiprocessing.pool import ThreadPool
from peewee import *
db = MySQLDatabase(host = '127.0.0.1',database ='spotify_2', user='root', passwd='')
#db = MySQLDatabase(host = '35.186.162.56',database ='spotify', user='root', passwd='ofeenel')
class family_accounts(peewee.Model):
        ID = peewee.SmallIntegerField()
        username = peewee.CharField(unique=True)
        password = peewee.CharField()
        country = peewee.FixedCharField()
        upgrades_available = peewee.IntegerField()
        last_checked = peewee.DateTimeField()
        login_tries = peewee.IntegerField()
        class Meta:
              database = db

class Checker:
    def __init__(self):      
        self.API = ["http://35.237.185.41:8000","http://35.185.205.157:8000","http://35.230.149.15:8000"]
        #self.API = ["http://127.0.0.1:5002"]
        self.MembersDELETED = 0
        self.ACCOUNTNEEDREUPGRADE = 0
        self.FAMILYACCOUNTS = family_accounts.select().where(
           (datetime.datetime.now() + datetime.timedelta(minutes = -5) > family_accounts.last_checked)).limit(50)
        
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
         request = client.delete(random.choice(self.API) +"/family/" + acc.username + ":" + acc.password+"/" + memberid,verify = True)
         if request.status_code == 204:
               acc.upgrades_available += 1                
               self.MembersDELETED += 1
    def deleteFamily(self,acc):
        acc.delete_instance()
        self.FAMILYACCOUNTSREMOVED += 1
    def Start(self,acc):
         acc.last_checked = datetime.datetime.now()
         acc.upgrades_available = 0
         client = requests.Session()
         try: request = client.get(random.choice(self.API) +"/family/" + acc.username + ":" + acc.password,verify = True)
         except requests.exceptions.RequestException: return
         if request.status_code == 200:
            self.FAMILYACCOUNTSWORKING += 1
            acc.login_tries = 0
            response = json.loads(request.text)
            if response["premium"] == True:             
               if response["country"]:
                  acc.country = response["country"]
               if len(response["members"]) > 0:
                  for x in response["members"]:
                      self.Remove(acc,x["membershipUuid"],client)
               if response["available_spots"]:
                  acc.upgrades_available += response["available_spots"]
               if len(response["invites"]) > 0:
                  acc.upgrades_available += len(response["invites"])
            else: self.deleteFamily(acc)
            if response["premium"] == True and acc.upgrades_available == 0 and response["can_invite"] == False: self.deleteFamily(acc)
         if request.status_code == 400:
               acc.login_tries +=1
               if acc.login_tries >= 5: self.deleteFamily(acc)
         acc.save()
if __name__ == '__main__': 
    while 1:
      Checker()
      time.sleep(5)