
from supabase import create_client, Client

url: str = "https://vrwzhwkdvwuyshvzcjvt.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZyd3pod2tkdnd1eXNodnpjanZ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI3NTI2NTQsImV4cCI6MjA0ODMyODY1NH0.82MpAR5bWTTlQNzmlW1vNaomMygFiDu7mMCXGDT2s8I"
supabase: Client = create_client(url, key)
# user = supabase.auth.sign_in_with_password({ "email": "egor.a.mironov@gmail.com", "password": "funcode" })
data = (supabase.table("users").select("*").execute())
print(data)