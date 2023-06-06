#!/usr/bin/env python3
import requests,json,sys,peewee,datetime, pytz,os,configparser
from pathlib import Path
from os.path import dirname, abspath
from peewee import *
from multiprocessing.pool import ThreadPool
try:
    config = configparser.ConfigParser()
    config.read(r'C:\xampp\htdocs\V5\config\config.ini')
    #config.read(os.path.join(dirname(dirname(dirname(abspath(__file__)))) + '/config/config.ini'))
    db_host = config.get('database', 'host')
    db_db = config.get('database', 'db')
    db_user = config.get('database', 'user')
    db_pawd = config.get('database', 'pass')
except:
     print( {'type_':'error','msg':"Unable to get database information from config file."})
     raise SystemExit
db = MySQLDatabase(host = db_host,database =db_db, user=db_user, passwd=db_pawd)
class family_accounts(peewee.Model):
        ID = peewee.SmallIntegerField()
        username = peewee.CharField(unique=True)
        password = peewee.CharField()
        country = peewee.FixedCharField()
        last_checked = peewee.DateTimeField()
        available_upgrades = peewee.SmallIntegerField()
        login_tries = peewee.SmallIntegerField()
        class Meta:
              database = db
class spotify_upgrades(peewee.Model):
        ID = peewee.SmallIntegerField()
        username = peewee.CharField(unique=True)
        membership_id = peewee.CharField()
        family_id = peewee.SmallIntegerField()
        visitor_id = peewee.SmallIntegerField()
        class Meta:
              database = db
class checker():
    def __init__(self): 

        self.NONE_SHOP_DELETED = 0
        self.ACCOUNTS_UPGRADED = 0 
        self.NON_UPGRADED_DELETED = 0 

        self.DEBUG = config.get('main','debug')
        self.CLIENT = requests.Session()
        
        self.importAccounts()

        self.API = config.get('main','api').split(',')

        self.Members = spotify_upgrades.select()
        
       
        self.Family_Accounts = family_accounts.select().where((datetime.datetime.now() + datetime.timedelta(minutes = -200) > family_accounts.last_checked))
        print( "Loaded "+str(len(self.Members))+" SpotiLife members accounts.", sep=' ', end='\n', file=sys.stdout, flush=True)
        print( "Loaded "+str(len(self.Family_Accounts))+" SpotiLife family owner accounts.", sep=' ', end='\n', file=sys.stdout, flush=True)
        if len(self.Family_Accounts) > 0:
            pool = ThreadPool(10)
            pool.map(self.check, self.Family_Accounts)
            pool.close()
            pool.join()
        self.removeuseless()

    def check(self,family_account):
        family_account.last_checked = datetime.datetime.now(pytz.timezone('US/Eastern'))
        for SITE in self.API:
            try: request_response = self.CLIENT.get(SITE + "/family/" + family_account.username + ":" + family_account.password,timeout=15,verify = True)
            except requests.exceptions.RequestException: continue
            except requests.Timeout: continue
            if request_response.status_code != 200:
               try:
                  response = json.loads(request_response.text)
                  if response['errors'][0]['message']:
                     if 'Request Page Account Profile'in response['errors'][0]['message']:
                        family_account.login_tries += 1
                        family_account.save()
                        return
                     if 'Invalid Credentials' in response['errors'][0]['message']:
                        family_account.login_tries = 5
                        family_account.save()
                        self.log( "Wrong Username or password.",0,family_account)
                        return
               except: continue
               continue
            try:
               response_text = json.loads(request_response.text)
            except: 
               return 
            Email = response_text['email']
            isPremium = response_text['premium']
            Available_Spots = response_text['available_spots']
            Can_Invite = response_text['can_invite']
            Members  = response_text['members']
            Invites  = response_text['invites']
            Country = response_text['country']
            if isPremium is False:
               family_account.login_tries = 5
               family_account.save() 
               self.log("Remove account is not premium.",0,family_account)
               return
            if isPremium and Available_Spots is 5 and Can_Invite is False:
               family_account.login_tries  = 5
               family_account.save() 
               self.log("Remove account belongs to a family plan.",0,family_account)
               return
            if (isPremium and Available_Spots <= 5 and Can_Invite) or (isPremium and (len(Members) + len(Invites)) > 0 and Can_Invite is False):
               family_account.country = Country
               family_account.available_upgrades = Available_Spots + len(Invites)
               family_account.login_tries = 0
               self.log("This is a family owner account",1,family_account)
               self.checkMembers(family_account,Members)
               family_account.save()
               return
            self.log("Upgrading account to premium.",2,family_account)
            self.upgrade(family_account)
        family_account.save() 
    def log(self,text,code,family_account = None):
       if self.DEBUG:
          message = "[debug] - "  
          if code == 0:message = message + "[error] - "
          if code == 2:message = message + "[info] - "    
          if code == 1:message = message  +"[success] - "
          if family_account != None: 
             message = message + "["+family_account.username+":" + family_account.password+ "] - " + text
          else:
             message = message + text
          print(message, sep=' ', end='\n', file=sys.stdout, flush=True)
         
    def upgrade(self,family_account):    
        for SITE in self.API:
            try: 
               request_response = self.CLIENT.get(SITE + "/upgrade/" + family_account.username + ":" + family_account.password,timeout=15,verify = True)
            except requests.exceptions.RequestException: continue
            except requests.Timeout: continue
            if request_response.status_code != 200:
               try:
                  response = json.loads(request_response.text)
               except:
                  continue
               if 'errors' in response and 'message' in response['errors'][0] and response['errors'][0]['message']:
                  if 'Invalid Credentials' in response['errors'][0]['message']:
                     family_account.login_tries = 5
                     self.log( "Wrong Username or password.",0,family_account) 
                     return
                  if 'This is a none premium account' in response['errors'][0]['message']:
                     family_account.login_tries = 5
                     self.log( "This is a none premium account.",0,family_account)
                     return
                  if 'This account is already family owner' in response['errors'][0]['message']:
                     self.log( "This account is already family owner",0,family_account)
                     return
                  if 'This account belongs to a family plan' in response['errors'][0]['message']:
                     family_account.login_tries = 5
                     self.log( "This account belongs to a family plan",0,family_account)
                     return
               else: continue
            if 'Success' in request_response.text:
               family_account.login_tries = 0
               family_account.available_upgrades = 5
               self.ACCOUNTS_UPGRADED +=1
               self.log( "Account upgraded to spotify family owner.",1,family_account)
               return
            else: 
               family_account.login_tries += 1
               self.log( "Failed to upgrade account to premium.",0,family_account)
               continue

    def checkMembers(self,family_account,members):
        self.log( "Checking "+str(len(members))+" family member accounts.",2,family_account)
        MembsID = []          
        for member in members:
            membershipUuid = str(member['membershipUuid'])
            for memb in self.Members:
                if membershipUuid == memb.membership_id:
                   family_account.available_upgrades -= 1
                   MembsID.append(memb.membership_id)
                   self.log( "Shop account member with ID - " +membershipUuid,2,family_account)
                   break
        for mems in members:
            membershipUuid = str(mems['membershipUuid'])
            if membershipUuid not in MembsID:
                 for SITES in self.API:
                     try: 
                        request =  self.CLIENT.delete(SITES +"/family/" + family_account.username + ":" + family_account.password+"/" + membershipUuid,timeout=30,verify = True)
                     except requests.exceptions.RequestException: continue
                     except requests.Timeout: continue
                     if request.status_code == 204:
                        family_account.available_upgrades +=1
                        self.log( "Removed none shop member with ID - " +membershipUuid ,2,family_account)
                        self.NONE_SHOP_DELETED += 1
                        break
        checkMembers_ = spotify_upgrades.select().where(spotify_upgrades.family_id == family_account.ID)
        if len(checkMembers_) > 0:
            for x in checkMembers_:
               if x.membership_id not in MembsID:
                  self.log( " Removed non-upgraded shop member with ID - " + x.membership_id ,2,family_account)
                  self.NON_UPGRADED_DELETED+= 1
                  x.delete()
    def importAccounts(self):
       accs = Path("accounts.txt")
       if accs.is_file():        
          f = open("accounts.txt","r")
          myList = []
          for line in f:
             acc = line.replace('\n', '').split(':')
             myList.append({"username": acc[0], "password": acc[1]})
          family_accounts.insert_many(myList).on_conflict('replace').execute()
          f.close()
          os.remove("accounts.txt")
    def removeuseless(self):
        deleted = family_accounts.delete().where(family_accounts.login_tries >= 2)
        print("Removed "+str(deleted.execute())+" family owner account.", sep=' ', end='\n', file=sys.stdout, flush=True)
        print( "Upgraded "+str(self.ACCOUNTS_UPGRADED)+" spotify premium accounts to spotify family owner.", sep=' ', end='\n', file=sys.stdout, flush=True)
        print( "Removed "+str(self.NONE_SHOP_DELETED)+" none shop accounts.", sep=' ', end='\n', file=sys.stdout, flush=True)
        print( "Removed "+str(self.NON_UPGRADED_DELETED)+" none upgraded shop accounts.", sep=' ', end='\n', file=sys.stdout, flush=True)
if __name__ == '__main__': 
   c = checker();


