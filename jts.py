import re
import cmd2
import time
from time import sleep
from pathlib import Path
from libs.parser import Parser
from libs.printit import Color as cl
from libs.ig_brute import IgInteract
from libs.printit import PrintIt as pt
from libs.data_requester import Requester
from libs.cpf_finder import CPFLiveConsult

CPF_RE = re.compile(r"^(\*\*\*\.\d{3}\.\d{3}-\*\*)|(\*\*\*\d{3}\d{3}\*\*)")

def printit(d: dict):
    for key, value in d.items():
        print(f"[{cl.GREEN}*{cl.RESET}] {cl.GREEN}{key.capitalize()}{cl.RESET}: {value}")

def style_print(d: str):
    splited = d.split("$")
    print(f"{cl.GREEN}{splited[0]}{cl.RESET}: {splited[1].strip()}\n {cl.GREEN}{splited[2].strip()}{cl.RESET}: {splited[3]}\n")
    
class Console(cmd2.Cmd):
    
    def __init__(self):
        super().__init__(
            persistent_history_file=".jts_history",
            persistent_history_length=1000
        )
        self.prompt = "\033[7;49;97mjts\033[0m> "
        self.intro = pt.banner()
    
    @cmd2.with_category("Corp")
    @cmd2.with_argparser(Parser.cnpj_parser)
    def do_cnpj(self, args):
        if args.CNPJ:
            pt.info("Starting CNPJ search...")
            data = Requester(args.CNPJ).cnpj()
            if "error" not in data:
                printit(data);return
                
            pt.error("Error in API request.");return
            
        pt.invalid_usage("cnpj")
            
    @cmd2.with_category("People")
    @cmd2.with_argparser(Parser.cpf2_parser)
    def do_cpf_bruter(self, args):
        if not args.CPF or not CPF_RE.match(args.CPF):
            pt.invalid_usage("cpf_bruter"); return
    
        workers = args.workers if args.workers else 12
        string = " ".join(args.string) if args.string else None
        
        pt.info("Starting CPF brute force...")
        CPFLiveConsult(args.CPF, workers, string).get_results()
        
    @cmd2.with_category("Device")
    @cmd2.with_argparser(Parser.ip_parser)
    def do_ip(self, args):
        if args.IP:
            pt.info("Starting IP search...")
            data = Requester(args.IP).ip()
            if "error" not in data:
                printit(data);return
                
            pt.error("Error in API request.");return
            
        pt.invalid_usage("ip")
            
    @cmd2.with_category("People")
    @cmd2.with_argparser(Parser.name_parser)
    def do_name(self, args):
        if args.NAME and len(args.NAME) in (1,2,3,4,5):
            pt.info("Starting name search...")
            data = Requester(" ".join(args.NAME)).name()
            i = 0
            try:
                for item in data:
                    print(f"{cl.GREEN}Result-{i}{cl.RESET}: {item}")
                    time.sleep(0.1)
                    i += 1
                    
                return
            
            except Exception:
                pt.error("Error in API request.");return
        
        pt.invalid_usage("name")
            
    @cmd2.with_category("People")
    @cmd2.with_argparser(Parser.ig_bruter_parser)
    def do_ig_bruteforcer(self, args):
        if args.username != None and args.wordlist != None:
            d = args.delay if isinstance(args.delay, int) and args.delay >= 5 else 5
            IgInteract(args.username, Path(args.wordlist).resolve(), timeout=d).ig_connect()
            return
            
        pt.invalid_usage("ig_bruteforcer")
                
    @cmd2.with_category("Users")
    @cmd2.with_argparser(Parser.username_parser)
    def do_username(self, args):
        if args.USERNAME:
            pt.info("Starting username search...")
            Requester(args.USERNAME).username()
            return
                
        pt.invalid_usage("username")
                    
    @cmd2.with_category("Users")
    @cmd2.with_argparser(Parser.name_webmii_parser)
    def do_webmii_name(self, args):
        if args.NAME and len(args.NAME) in (2,3,4,5):
            pt.info("Starting Webmii name search...")
            data = Requester(" ".join(args.NAME)).name_webmii()
            if "error" not in data:
                
                if args.strings:
                    for item in data:
                        if any(s in item for s in args.strings):
                            style_print(item)                       
                            
                        sleep(0.1)
                    
                    return
                    
                else:
                    for item in list(data):                 
                        style_print(item)                       
                        sleep(0.1)
                    
                    return
                
            pt.error("Error in API request.");return
            
        pt.invalid_usage("webmii_name")
            
    @cmd2.with_category("People")
    @cmd2.with_argparser(Parser.number_parser)
    def do_number(self, args):
        if args.NUMBER:
            pt.info("Starting number search...")
            data = Requester(args.NUMBER).number(mode="single")
            if "error" not in data:
                printit(data);return
                
            pt.error("Error in API request.");return
            
        pt.invalid_usage("number")
            
    @cmd2.with_category("People")
    @cmd2.with_argparser(Parser.numbers_parser)
    def do_numbers(self, args):
        if args.NUMBERS:
            pt.info("Starting numbers search...")
            data = Requester(args.NUMBERS).number(mode="multi")
            for item in data:
                printit(item)
                print("")
                
        pt.invalid_usage("numbers")
                    
    @cmd2.with_category("Corp")
    @cmd2.with_argparser(Parser.cep_parser)
    def do_cep(self, args):
        if args.CEP:
            pt.info("Starting CEP search...")
            data = Requester(args.CEP).cep()
            if "error" not in data:
                printit(data);return
                
            pt.error("Error in API request.");return
            
        pt.invalid_usage("cep")
            
if __name__ == "__main__":
    Console().cmdloop()
