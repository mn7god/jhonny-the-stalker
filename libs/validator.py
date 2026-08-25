import re
import socket

NUMBER_RE = re.compile(r"\d{11,15}")
CNPJ_RE = re.compile(r"\d{14}")
CEP_RE = re.compile(r"\d{8}")
NAME_RE = re.compile(r"^[a-zA-Zà-ÿÀ-ÿ]+(?:[-'][a-zA-Zà-ÿÀ-ÿ]+)*(?:\s+[a-zA-Zà-ÿÀ-ÿ]+(?:[-'][a-zA-Zà-ÿÀ-ÿ]+)*)*$")
USERNAME_RE = re.compile(r"^[a-z0-9_.]{4,40}$")

class Validator:
    def __init__(self, data: str):
        if not data:
            raise ValueError("Need a data to validate.")
        self.data = data
    
    @staticmethod
    def clean_input(data: str, chars_to_remove: str):
        """Remove characters não numéricos de acordo com o que for necessário."""
        translation_table = str.maketrans({ord(c): None for c in chars_to_remove})
        return data.translate(translation_table)
    
    @staticmethod
    def calculate_cpf(cpf):
        cpf_f = cpf.replace(".","").replace("-","")
        nine_d = [int(item) for item in cpf_f[0:9]]
        s = sum(i * r for i, r in zip(nine_d, range(10, 1, -1)))
        r1 = s % 11
        v1 = 0 if r1 < 2 else 11 - r1

        s2 = sum(i2 * r2 for i2, r2 in zip(nine_d, range(11, 2, -1))) + v1 * 2
        r2 = s2 % 11
        v2 = 0 if r2 < 2 else 11 - r2
        
        return f"{v1}{v2}"
    
    @staticmethod
    def format_cpf(cpf):
        cpf_f = re.sub(r'\D', '', cpf)
        if len(cpf_f) not in (9, 11):
            return None
        return f"{cpf_f[:3]}.{cpf_f[3:6]}.{cpf_f[6:9]}-{Validator.calculate_cpf(cpf_f[:9])}"
        
    @staticmethod
    def cpf_validate(cpf):
        cpf_f = re.sub(r'\D', '', cpf)
        if len(cpf_f) != 11 or not cpf_f.isdigit() or cpf_f == cpf_f[0] * 11:
            return False
        calculated_digits = Validator.calculate_cpf(cpf_f[:9])
        return calculated_digits == cpf_f[9:]
    
    def ip_validator(self):
        try:
            socket.inet_aton(self.data)
            return self.data
        except:
            return False
    
    def number_validator(self):
        clean_number = self.clean_input(self.data, "-()+ ")
        if len(clean_number) in (11, 12, 13, 14, 15) and NUMBER_RE.fullmatch(clean_number):
            return clean_number
        
    def cnpj_validator(self):
        clean_cnpj = self.clean_input(self.data, "/.-")
        if len(clean_cnpj) == 14 and CNPJ_RE.fullmatch(clean_cnpj):
            return clean_cnpj
        
    def cep_validator(self):
        clean_cep = self.clean_input(self.data, "-")
        if len(clean_cep) == 8 and CEP_RE.fullmatch(clean_cep):
            return clean_cep
            
    def cpf_validator(self):
        clean_cpf = self.clean_input(self.data, "-.")
        cpf_val = self.cpf_validate(clean_cpf)
        cpf_len = len(clean_cpf)
        if cpf_val and cpf_len == 11:
            return (self.format_cpf(clean_cpf), clean_cpf)
            
    def name_validator(self):
        if NAME_RE.fullmatch(self.data):
            return self.data
            
    def username_validator(self):
        if USERNAME_RE.fullmatch(self.data):
            return self.data
