from pymongo import MongoClient

# MongoDB Atlas connection
client = MongoClient(
    "mongodb+srv://lalithkrishna:K%40kanini128@cluster0.mzhxnw3.mongodb.net/?retryWrites=true&w=majority"
)

# Database
db = client["medtriage"]

# Collections
patients = db["patients"]
users = db["users"]
