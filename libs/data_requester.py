import re
import json
import time
import random
import requests
from subprocess import run
from .jts_utils import Utils as ut
from .user_agents import return_ua
from .cpf_finder import CPFLiveConsult
from .validator import Validator as val
from playwright.sync_api import sync_playwright

apis = {
    'number': "http://apilayer.net/api/validate?",
    'ip': "http://ip-api.com/json/",
    'cnpj': "https://api.opencnpj.org/",
    'cep': "https://viacep.com.br/ws/"
}

class Requester:
    
    def __init__(self, data):
        if not data:
            raise ValueError("Need a data to validate.")
        self.data = data
        
    def cnpj(self):
        v = val(self.data).cnpj_validator()
        if v != None:
            ua = {
                'User-Agent': return_ua(), 
                'Host': 'api.opencnpj.org', 
                'Connection': 'keep-alive'
            }
            r = requests.get(url=apis['cnpj']+v, headers=ua)
            if r.status_code == 200 and "invalid_cnpj" not in r.text:
                js = json.loads(r.text)
                data = {
                    'cnpj': js['cnpj'],
                    'razao_social': js['razao_social'],
                    'nome_fantasia': js['nome_fantasia'],
                    'data_inicio': js['data_inicio_atividade'],
                    'logradouro': js['logradouro'],
                    'numero': js['numero'],
                    'complemento': js['complemento'],
                    'bairro': js['bairro'],
                    'cep': js['cep'],
                    'email': js['email'],
                    'telefones': ut.format_cnpj_numbers_list(js['telefones']),
                }
                return data
                
        return {"error": "invalid_cnpj"}
         
    def ip(self):
        v = val(self.data).ip_validator()
        if v != None:
            ua = {
                'User-Agent': return_ua(), 
                'Host': 'ip-api.com', 
                'Connection': 'keep-alive'
            }
            r = requests.get(url=apis['ip']+v, headers=ua)
            if r.status_code == 200 and "invalid" not in r.text:
                js = json.loads(r.text)
                data = {
                    'isp': js['isp'],
                    'org': js['org'],
                    'as': js['as'],
                    'country': js['country'],
                    'region': js['region'],
                    'city': js['city'],
                    'zip_code': js['zip'],
                    'lat': js['lat'],
                    'lon': js['lon'],
                    'timezone': js['timezone'],
                    'google_maps_url': f"https://www.google.com/maps/@{js['lat']},{js['lon']},15z"
                }
                return data
                
        return {"error": "invalid_ip"}
         
    def number(self, mode="single"):
        if mode == "single":
            v = val(self.data).number_validator()
            if v != None:
                ua = {
                    'User-Agent': return_ua(), 
                    'Host': 'apilayer.net', 
                    'Connection': 'keep-alive'
                }
                r = requests.get(url=apis['number'], 
                    headers=ua, 
                    params={
                        'access_key': 'f134484ed14981a957368f2a06aaa251', 
                        'number': v
                    }
                )
                if r.status_code == 200 and '"valid":false' not in r.text:
                    js = json.loads(r.text)
                    data = {
                        'number': js['international_format'],
                        'country_code': js['country_code'],
                        'country_name': js['country_name'],
                        'location': js['location'],
                        'carrier': js['carrier'],
                        'line_type': js['line_type']
                    }
                    return data
                
        elif mode == "multi":
            datas = []
            for num in self.data:
                v = val(num).number_validator()
                if v != None:
                    ua = {
                        'User-Agent': return_ua(), 
                        'Host': 'apilayer.net', 
                        'Connection': 'keep-alive'
                    }
                    r = requests.get(url=apis['number'], 
                        headers=ua, 
                        params={
                            'access_key': 'f134484ed14981a957368f2a06aaa251', 
                            'number': v
                        }
                    )
                    if r.status_code == 200 and '"valid":false' not in r.text:
                        js = json.loads(r.text)
                        data = {
                            'number': js['international_format'],
                            'country_code': js['country_code'],
                            'country_name': js['country_name'],
                            'location': js['location'],
                            'carrier': js['carrier'],
                            'line_type': js['line_type']
                        }
                        datas.append(data)
                        
                time.sleep(random.randint(1,6))
                    
            return datas
                
        return {"error": "invalid_number"}
         
    def cep(self):
        v = val(self.data).cep_validator()
        if v != None:
            ua = {
                'User-Agent': return_ua(), 
                'Host': 'viacep.com.br', 
                'Connection': 'keep-alive'
            }
            r = requests.get(url=apis['cep']+v+"/json", 
                headers=ua, 
            )
            if r.status_code == 200 and '"erro"' not in r.text:
                js = json.loads(r.text)
                data = {
                    'cep': js['cep'],
                    'logradouro': js['logradouro'],
                    'bairro': js['bairro'],
                    'regiao': js['regiao'],
                    'ddd': js['ddd'],
                }
                return data
                
        return {"error": "invalid_cep"}
        
    def cpf(self):
        v = val(self.data).cpf_validator()
        if v != None:
            for item in v:
                data = load_data(item)
                if data != []:
                    return data
                    
        return {"error": "invalid_cpf"}
        
    def name(self):
        v = val(self.data).name_validator()
        if v != None:
            data = load_data(v)
            if data:
                return data
                
        return {"error": "invalid_name"}
        
    def name_webmii(self):
    
        v = val(self.data).name_validator()
        if not v:
            return ["error: invalid_name"]
    
        results = []
    
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars"
                ]
            )
    
            context = browser.new_context(
                user_agent=return_ua(),
                viewport={"width": 1366, "height": 768},
                locale="en-US",
                timezone_id="America/New_York"
            )
    
            page = context.new_page()

            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
    
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
    
                window.chrome = { runtime: {} };
    
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Inc.';
                    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                    return getParameter(parameter);
                };
            """)
    
            page.set_extra_http_headers({
                "accept-language": "en-US,en;q=0.9",
                "upgrade-insecure-requests": "1"
            })
    
            url = f"https://webmii.com/people?n={v}"
            page.goto(url, timeout=60000)
    
            page.wait_for_load_state("networkidle")
    
            page.mouse.move(
                random.randint(200, 800),
                random.randint(200, 600)
            )
            time.sleep(random.uniform(1.5, 3.5))
    
            page.mouse.wheel(0, random.randint(300, 1200))
            time.sleep(random.uniform(1, 2.5))
    
            links = page.locator("a")
            count = links.count()
    
            for i in range(count):
                try:
                    el = links.nth(i)
                    text = el.inner_text().strip()
                    href = el.get_attribute("href")
    
                    if text and href and href.startswith("http"):
                        results.append(f"Text$ {text} $URL$ {href}")
    
                except:
                    continue
    
            browser.close()
    
        return results
    
    def username(self):
        v = val(self.data).username_validator()
        if v != None:
            try:
                run(["maigret", v, "--auto-disable", "--timeout", "10", "--retries", "0", "--no-extracting"])
            except KeyboardInterrupt:
                print("User aborted.")
