# kArmasDatr
with datr browser for finding cookies

python3 kArmasDatr.py

python3 kArmasDatr.py --target fb -o datr.json

python3 kArmasDatr.py --url https://www.instagram.com/accounts/login/

python3 kArmasDatr.py --target ig   

# default, instagram.com

python3 kArmasDatr.py --target fb  

# facebook.com

python3 kArmasDatr.py --target ig-login

# /accounts/login/

python3 kArmasDatr.py --url https://www.instagram.com/ -o \~/datr.json

python3 kArmasDatr.py --timeout 20 --retries 3




curl -s 'https://www.instagram.com/' \
  -H "User-Agent: Mozilla/5.0 ..." \
  -H{
  "datr": "CAvFas-l1VKiexnH7ipUK5KV",
  "sources": {"set-cookie": "...", "cookiejar": "...", "html": "..."},
  "url": "https://www.instagram.com/",
  "fetched_at": 1791290000,
  "other_cookies": ["csrftoken", "ig_did", "mid"]
} "Cookie: datr=$DATR"

# use same cookie with curl from same site you dumped it from

curl -s 'https://www.instagram.com/' \
  -H "User-Agent: Mozilla/5.0 ..." \
  -H "Cookie: datr=$DATR"

  made in l0v3 bY kArmasec



  
