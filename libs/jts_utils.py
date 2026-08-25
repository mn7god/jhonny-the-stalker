import re
import hashlib
from pathlib import Path

class Utils:
	@staticmethod
	def format_cnpj_numbers_list(num_list: list):
		new_list = []
		for item in num_list:
			number = item['ddd'] + item['numero']
			new_list.append(number)
		
		return new_list
	
	@staticmethod
	def return_hex(path: Path):
		if path.exists() and path.is_file():
			with open(str(path), 'rb') as f:
				data = f.read(65551)
			return hashlib.sha256(data).hexdigest()
			
		return None
	
