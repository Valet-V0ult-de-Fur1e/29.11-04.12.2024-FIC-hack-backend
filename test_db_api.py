
# from supabase import create_client, Client


# def get_hash(input_string: str) -> str:
#     import hashlib
#     string_hash = hashlib.sha256(input_string.encode("utf-8")).hexdigest()
#     print(string_hash)
#     return string_hash


# print(get_hash('nfyz') == get_hash('nfyz'))
    

# url: str = "https://vrwzhwkdvwuyshvzcjvt.supabase.co"
# key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZyd3pod2tkdnd1eXNodnpjanZ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI3NTI2NTQsImV4cCI6MjA0ODMyODY1NH0.82MpAR5bWTTlQNzmlW1vNaomMygFiDu7mMCXGDT2s8I"
# supabase: Client = create_client(url, key)
# data = (supabase.table("users").insert(
#     {
#         "login":"serLogin",
#         "mail":"ser.a.svodov@email.com",
#         "name_first":"Sergey",
#         "name_last":"Svodov",
#         "password_hash":get_hash('123qwerssdfsdfy123'),
#     }
#     ).execute())


# print(data)
# assert len(data.data) > 0

# data = (supabase.table("users").select("*").execute())
# print(data)
# assert len(data.data) > 0
import datetime
print(type(datetime.datetime.now().strftime("%Y-%m-%d")))