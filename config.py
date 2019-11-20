import os
from dotenv import load_dotenv
load_dotenv()



class Config(object):
  SQLALCHEMY_DATABASE_URI= os.environ['DATABASE_URL']
  SECRET_KEY  = "chloe"
  DEBUG=True