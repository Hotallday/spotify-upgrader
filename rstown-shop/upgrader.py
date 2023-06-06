import peewee,configparser,requests,json,argparse,os,logging
from os.path import dirname, abspath
from faker import Faker
from peewee import *

try:
    config = configparser.ConfigParser()
    config.read(r'C:\xampp\htdocs\config\config.ini')
    #config.read(os.path.join(dirname(dirname(dirname(abspath(__file__)))) + '/config/config.ini'))
    db_host = config.get('database', 'host')
    db_db = config.get('database', 'db')
    db_user = config.get('database', 'user')
    db_pawd = config.get('database', 'pass')
except:
     print( {'type_':'error','msg':"Unable to get database information from config file."})
     raise SystemExit


parser = argparse.ArgumentParser(description='Upgrade spotify account.')
parser.add_argument("-u", "--username", required=True,
	help="Username of the spotify user.")
parser.add_argument("-p", "--password", required=True,
	help="Password of the spotify user.")

API = config.get('main','api').split(',')
db = MySQLDatabase(host = db_host,database =db_db, user=db_user, passwd=db_pawd)
fake= Faker()
CLIENT = requests.Session()

#logging.basicConfig(filename=os.path.join(dirname(dirname(dirname(abspath(__file__)))) + "/logs/upgrader_logs.log"),
                            #format='%(asctime)s;%(levelname)s;%(message)s',
                            #datefmt='%Y-%m-%d %H:%M:%S',
                            #level=logging.INFO)

logging.basicConfig(filename=os.path.join('C:/xampp/htdocs/logs/upgrader_logs.log'),
                            format='%(asctime)s;%(levelname)s;%(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO)

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
class upgrader():
      def __init__(self,username, password):
         self.errors = {

            'Invite limit reached':{'type_':'error','msg':"You enter an invalid email address."},
            'Internal Server Error':{'type_':'error','msg':"Unable to upgrade your spotify account at this certain time."},
            'Invalid credentials for the member user' : {'type_':'error','msg':"Wrong username and password for spotify account."},
            'Confirm Invitation. This is a Premium Account': {'type_':'warning','msg':"This account is already premium."},
            'This account is already a member of a plan':{'type_':'warning','msg':"This account is already premium."},
            'Invalid email address':{'type_':'error','msg':"You enter an invalid email address."},
            'Switch restriction limit reached':{'type_':'warning','msg':"The limit of upgrades for this account has been reached. Please try again with another spotify account."},
            'User is not eligible':{'type_':'error','msg':"Unable to upgrade your spotify account at this certain time."},
         }
         self.username = username
         self.password = password
      def getInfo(self):
         for site in API:
            try: request_response = CLIENT.get(site + "/family/" + self.username + ":" + self.password,
                  timeout=15,
                  verify = True)
            except requests.exceptions.RequestException: continue
            except requests.Timeout: continue
            logging.info(request_response.text)
            if request_response.status_code != 200:
               response = json.loads(request_response.text)
               if 'errors' in response and 'message' in response['errors'][0] and response['errors'][0]['message']:
                  message = response['errors'][0]['message']
                  if message == "Invalid Credentials": 
                     print( {'type_':'error','msg':"Wrong username and password for spotify account."},flush= True)
                     raise SystemExit
                  continue;
            if request_response.status_code == 200:
               response = json.loads(request_response.text)
               if response["premium"] == True:
                  print( {'type_':'warning','msg':"This account is already premium."},flush= True)
                  raise SystemExit
               self.country = response["country"]
               return True
      def upgrade(self):
          f_accs = self.getFamilyAccounts()
          if len(f_accs) == 0: 
             print( {'type_':'warning','msg':"Your spotify account country is not currently supported."},flush = True)
             raise SystemExit
          first_name = fake.name()
          address = fake.address()
          data = {
               "password": self.password,
               "email":  self.username,
               "first_name": first_name,
               "address": {
                        "line2": "",
                        "postalCode":  "1580",
                        "city": address,
                        "partnerCheck": "",
                        "line1": address
                     },
               "country" :  self.country,
               "last_name": first_name     
          }
          for fam_account in f_accs:
              for site in API:
                  try:
                     request_response = CLIENT.post(site + "/family/" + fam_account.username + ":" + fam_account.password, json.dumps(data),headers ={'content-type': 'application/json'},timeout=30,verify = True)
                  except requests.exceptions.RequestException: continue
                  except requests.Timeout: continue
                  logging.info(request_response.text)
                  if request_response.status_code == 201:
                     response = json.loads(request_response.text)
                     fam_account.available_upgrades -= 1
                     fam_account.save()
                     print({'type_':'success','membershipUuid':response["membershipUuid"], 'f_id':fam_account.ID, 'msg':"Your spotify account has been successfully upgraded."},flush = True) 
                     raise SystemExit
                  if request_response.status_code != 201:
                     response = json.loads(request_response.text)
                     err = self.handleErrors(response)
                     if err == "break": 
                        break
          print({'type_':'error','msg':"Unable to upgrade your spotify account at this certain time."},flush = True)
      def handleErrors(self,response):
          message = ''
          if 'message' in response and response['message'] is not None:
             print(self.errors.get(response['message'],{'type_':'error','msg':"Failed to upgrade this spotify account at this current time, please try again later."}),flush = True)
          if 'errors' in response and 'message' in response['errors'][0]:
             message = response['errors'][0]['message']
             if message == "Invalid Credentials": 
                return "break"
          if 'errors' in response and 'message' in response['errors'] and response['errors']['message'] and 'text' not in response["errors"]:
             message = response['errors']['message']
             if message == "Invalid Credentials": 
                return "break"
             print(self.errors.get(message,{'type_':'error','msg':"Failed to upgrade this spotify account at this current time, please try again later."}),flush = True)
          else:
             if ('errors' in response and 'message' in response['errors'][0] and 'text' in response["errors"][0]["data"]) and (message == "Invalid response. Confirm Invitation" or "Invalid response. Create Invitation."):
                data_msg = json.loads(response["errors"][0]["data"]['text'])
                msg= data_msg["failure"]["message"]
                if msg == "Invite limit reached": 
                   return "break"
                print(self.errors.get(msg,{'type_':'error','msg':"Failed to upgrade this spotify account at this current time, please try again later."}),flush = True)
          raise SystemExit
      def getFamilyAccounts(self):
          return family_accounts.select().where(family_accounts.available_upgrades > 0 , family_accounts.country == self.country, family_accounts.login_tries == 0).order_by(fn.Rand()).limit(3)
if __name__ == '__main__': 
   args = vars(parser.parse_args())
   username = args["username"]
   password = args["password"]
   c = upgrader(username,password)
   a = c.getInfo()
   if a is True:
      c.upgrade();