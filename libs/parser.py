import cmd2

class Parser:
	
	cnpj_parser = cmd2.Cmd2ArgumentParser(description='CNPJ Searcher.')
	cnpj_parser.add_argument('CNPJ', type=str)
	
	cpf2_parser = cmd2.Cmd2ArgumentParser(description='CPF Searcher.')
	cpf2_parser.add_argument('CPF', type=str, help="CPF Number.")
	cpf2_parser.add_argument('-s', '--string', nargs='+', help="String to search.")
	cpf2_parser.add_argument('-w', '--workers', type=int, help="Workers count.")
	
	ip_parser = cmd2.Cmd2ArgumentParser(description='IP Searcher.')
	ip_parser.add_argument('IP', type=str)
	
	name_parser = cmd2.Cmd2ArgumentParser(description='Name Searcher.')
	name_parser.add_argument('NAME', nargs='+')
	
	ig_bruter_parser = cmd2.Cmd2ArgumentParser(description='Name Searcher.')
	ig_bruter_parser.add_argument('-u', '--username', type=str, help="Username to bruteforce on")
	ig_bruter_parser.add_argument('-w', '--wordlist', type=str, help="Wordlist path.")
	ig_bruter_parser.add_argument('-d', '--delay', help="Delay.")
	
	username_parser = cmd2.Cmd2ArgumentParser(description='Name Searcher.')
	username_parser.add_argument('USERNAME', type=str, help="Username to search.")
	
	name_webmii_parser = cmd2.Cmd2ArgumentParser(description='Webmii Name Searcher.')
	name_webmii_parser.add_argument('NAME', nargs='+')
	name_webmii_parser.add_argument('-s', '--strings', nargs='+', help="Strings to search.")
	
	number_parser = cmd2.Cmd2ArgumentParser(description='Number Searcher.')
	number_parser.add_argument('NUMBER', type=str)
	
	numbers_parser = cmd2.Cmd2ArgumentParser(description='Number Searcher.')
	numbers_parser.add_argument('NUMBERS', nargs='+')
	
	cep_parser = cmd2.Cmd2ArgumentParser(description='CEP Searcher.')
	cep_parser.add_argument('CEP', type=str)
