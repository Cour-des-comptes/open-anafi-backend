import logging

logger = logging.getLogger(__name__)

class SoldeFactory():
	@staticmethod
	def factory(type_solde, solde):
		# each lambda function take c: credits dictionary and d: debits dictionnary
		if type_solde == "SX":
			# Solde Débiteur
			if solde == "C":
				return_func = lambda c, d: c[1] + c[2] + c[3] + c[4] - d[7]
			elif solde == "D":
				return_func = lambda c, d: d[1] + d[2] + d[3] + d[4] - c[7]
			elif solde == "SC":
				return_func = lambda c, d: c[1] + c[2] + c[3] + c[4] - d[7]
			elif solde == "SD":
				return_func = lambda c, d: d[1] + d[2] + d[3] + d[4] - c[7]
			else:
				logger.debug(f'{type_solde} {solde}')
				raise ValueError("Wrong type_solde and solde association")
		elif type_solde == "SS":
			# Solde Créditeur
			if solde == "C":
				return_func = lambda c, d: c[2] + c[3] + c[4] - d[7]
			elif solde == "D":
				return_func = lambda c, d: d[2] + d[3] + d[4] - c[7]
			elif solde == "SC":
				return_func = lambda c, d: c[1] + c[2] + c[3] + c[4] - d[7]
			elif solde == "SD":
				return_func = lambda c, d: d[1] + d[2] + d[3] + d[4] - c[7]
			else:
				logger.debug(f'{type_solde} {solde}')
				raise ValueError("Wrong type_solde and solde association")			
		elif type_solde == "BR":
			if solde == "C":
				return_func = lambda c, d: c[2] - c[6] - d[7]
			elif solde == "D":
				return_func = lambda c, d: d[2] - d[6] - c[7]
			elif solde == "SD":
				return_func = lambda c, d: d[2] - d[6] - d[7]
			elif solde == "SC":
				return_func = lambda c, d: c[2] - c[6] - c[7]
			else:
				logger.debug(f'{type_solde} {solde}')
				raise ValueError("Wrong type_solde and solde association")
		elif type_solde == "BO":
			if solde == "C":
				return_func = lambda c, d: c[6]
			elif solde == "D":
				return_func = lambda c, d: d[6]
			else:
				logger.debug(f'{type_solde} {solde}')
				raise ValueError("Wrong type_solde and solde association")
		elif type_solde == "BX":
			if solde == "C" or solde == "SC":
				return_func = lambda c, d: c[2] - d[7]
			elif solde == "D" or solde == "SD":
				return_func = lambda c, d: d[2] - c[7]
			else:
				logger.debug(f'{type_solde} {solde}')
				raise ValueError("Wrong type_solde and solde association")
		elif type_solde == "NB":
			if solde == "C":
				return_func = lambda c, d: c[3] + c[4]
			elif solde == "D":
				return_func = lambda c, d: d[3] + d[4]
			else:
				logger.debug(f'{type_solde} {solde}')
				raise ValueError("Wrong type_solde and solde association")
		elif type_solde == "BE":
			if solde == "C" or solde == "SC":
				return_func = lambda c, d: c[1]
			elif solde == "D" or solde == "SD":
				return_func = lambda c, d: d[1]
			else:
				logger.debug(f'{type_solde} {solde}')
				raise ValueError("Wrong type_solde and solde association")
		else:
			logger.debug(type_solde)
			raise ValueError("Wrong type_solde and solde association")
		return return_func