import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("/Users/alextaylor/Desktop/hackathon_2019/Hackathon 2019-3b7fec39ea0f.json")
firebase_admin.initialize_app(cred)

# Get a database reference to our posts
ref = db.reference('https://lmigos.firebaseio.com/messages/-LjRVSiJcpJ_X7ilCKEBhttps://lmigos.firebaseio.com/messages/-LjRVSiJcpJ_X7ilCKEB/body')

# Read the data at the posts reference (this is a blocking operation)
print(ref.get())