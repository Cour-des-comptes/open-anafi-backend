SQL_REQUEST_SIRET_SAFE = """
	SELECT e.ident AS siret,
		sum(e.cptdeb::numeric) AS cptdeb,
		sum(e.cptcre::numeric) AS cptcre, 
		e.exercice,
		e.cptop, 
		e.comptes,
		e.dp
	FROM execution_2010 AS e 
	{whereclause}
	GROUP BY siret, e.exercice,
	e.cptop, e.comptes, e.dp;
"""

SQL_REQUEST_SIRET = """
	SELECT e.ident AS siret,
		sum(e.cptdeb::numeric) AS cptdeb,
		sum(e.cptcre::numeric) AS cptcre, 
		e.exercice,
		e.cptop, 
		e.comptes,
		e.dp
	FROM execution_2010 AS e 
	WHERE (e.ident IN {sirets}) 
	AND ({exercices})
	GROUP BY siret, e.exercice,
	e.cptop, e.comptes, e.dp;
"""
SQL_REQUEST_SIREN = """
	SELECT substring(e.ident from 1 for 9) AS siren,
		sum(e.cptdeb) AS cptdeb,
		sum(e.cptcre) AS cptcre, 
		e.exercice,
		e.cptop, 
		e.comptes
	FROM execution_2010 AS e 
	WHERE e.ident LIKE {siren}
	AND ({exercices})
	GROUP BY siren, e.exercice,
	e.cptop, e.comptes;
"""
SQL_REQUEST_FINESS = """
	SELECT c.finess,
		sum(e.cptdeb) AS cptdeb,
		sum(e.cptcre) AS cptcre,
		e.exercice,
		e.cptop, 
		e.comptes
	FROM execution_2010 AS e
	INNER JOIN collectivite AS c 
	ON c.ident = e.ident
	WHERE c.finess = '{finess}' 
	AND ({exercices})
	GROUP BY siret, e.exercice,
	e.cptop, e.comptes;
"""

# pour avoir la dernière version du siret
SQL_REQUEST_COLLECTIVITE = """
	SELECT DISTINCT c.ident, c.ctype, c.cbudg, c.lbudg, c.mpoid, c.cnome
	FROM collectivite AS c, 
		(SELECT DISTINCT ident AS ident, MAX(exer) AS max_exer 
		FROM collectivite  
		WHERE ident IS NOT NULL GROUP BY ident) AS MC 
	WHERE c.ident IN {sirets} AND C.exer = MC.max_exer 
	AND C.ident = MC.ident
"""

SQL_REQUEST_COLLECTIVITE_SIREN = """
	SELECT DISTINCT c.ident, c.ctype, c.cbudg, c.lbudg, c.mpoid, c.cnome
	FROM collectivite AS c, 
		(SELECT DISTINCT ident AS ident, MAX(exer) AS max_exer 
		FROM collectivite  
		WHERE ident IS NOT NULL GROUP BY ident) AS MC 
	WHERE c.ident LIKE {sirens} AND C.exer = MC.max_exer 
	AND C.ident = MC.ident
"""

SQL_REQUEST_COLLECTIVITE_PER_YEAR = """
  SELECT DISTINCT c.ident, c.ctype, c.cbudg, c.lbudg, c.mpoid, c.cnome, c.exer, e.dp
	FROM collectivite AS c
	INNER JOIN execution_2010 AS e ON e.ident = c.ident
	WHERE c.ident IN {sirets} 
	AND c.exer = e.exercice
	AND c.exer IN {exercice}
"""


SQL_REQUEST_POPULATION = """
	SELECT sum(c.mpoid::int4), c.exer
	FROM collectivite AS c
	WHERE c.ident IN {sirets} AND c.exer IN {exercices}
	GROUP BY c.exer
	ORDER BY c.exer
"""

SQL_REQUEST_POPULATION_SIREN = """
	SELECT sum(c.mpoid::int4), c.exer
	FROM collectivite AS c
	WHERE c.ident LIKE {sirens} AND c.exer IN {exercices}
	GROUP BY c.exer
	ORDER BY c.exer
"""

SQL_REQUEST_SIRET_BALANCE = """
	SELECT e.ident AS siret,
		sum(e.cptdeb) AS cptdeb,
		sum(e.cptcre) AS cptcre, 
		e.exercice,
		e.cptop, 
		e.comptes,
		b.libelle_budget,
		c.nomen,
		c.lbudg
	FROM execution_2010 AS e JOIN collectivite AS c on e.ident = c.ident JOIN type_budget AS b on b.code_budget = c.cbudg
	WHERE 
		c.exer = e.exercice
	AND
	  e.ident IN {sirets} 
	AND ({exercices})
	GROUP BY e.ident, e.exercice,
	e.cptop, e.comptes, b.libelle_budget, c.nomen, c.lbudg;
"""

SQL_REQUEST_SIREN_BALANCE = """
	SELECT e.ident AS siret,
		sum(e.cptdeb) AS cptdeb,
		sum(e.cptcre) AS cptcre, 
		e.exercice,
		e.cptop, 
		e.comptes,
		b.libelle_budget,
		c.nomen,
		c.lbudg
	FROM execution_2010 AS e JOIN collectivite AS c on e.ident = c.ident JOIN type_budget AS b on b.code_budget = c.cbudg
	WHERE 
		c.exer = e.exercice
	AND
	e.ident LIKE '{siren}%'
	AND ({exercices})
	GROUP BY e.ident, e.exercice,
	e.cptop, e.comptes, b.libelle_budget, c.nomen, c.lbudg;
"""

SQL_REQUEST_DATAFRAME = """
	SELECT e.ident AS siret,
		sum(e.cptdeb::numeric) AS cptdeb,
		sum(e.cptcre::numeric) AS cptcre, 
		e.exercice AS exercice,
		e.cptop, 
		e.comptes,
		e.dp
	FROM execution_2010 AS e 
	WHERE {clause}
	GROUP BY siret, e.exercice,
	e.cptop, e.comptes, e.dp;
"""

SQL_REQUEST_COLLECTIVITE_AGG = """
	SELECT c.ident, c.ctype, c.cbudg, c.lbudg, c.mpoid, c.exer AS exercice, c.cnome
	FROM collectivite AS c 
	WHERE {clause}
"""

SQL_REQUEST_POPULATION_AGG = """
	SELECT sum(c.mpoid::int4), c.exer AS exercice
	FROM collectivite AS c
	WHERE {clause}
	GROUP BY exercice
	ORDER BY exercice
"""


class AggregationRequestMaker:

  @staticmethod
  def _get_siret_by_year_clause(siret_frame, exges_list, exercice='exer'):
    """
    :param exges_list:
    :param siret_frame:
    :return: sql_clause: str
    """
    sql_clause = ""
    first = True
    for ex in exges_list:
      df_year = siret_frame[siret_frame.exer == ex]['ident'].tolist()
      if df_year:
        idents = f'{df_year}'.replace('[', '(').replace(']', ')')
        if not first:
          sql_clause += " OR "
        sql_clause += f"({exercice} = {ex} AND ident IN {idents})"
        first = False
    return sql_clause

  @staticmethod
  def get_data_frame_request(siret_frame, exges_list):
    """

    :param exges_list:
    :param siret_frame:
    :return:
    """
    clause = AggregationRequestMaker._get_siret_by_year_clause(siret_frame, exges_list, exercice='exercice')
    return SQL_REQUEST_DATAFRAME.format(clause=clause)

  @staticmethod
  def get_population_request(siret_frame, exges_list):
    """

    :param exges_list:
    :param siret_frame:
    :return:
    """
    clause = AggregationRequestMaker._get_siret_by_year_clause(siret_frame, exges_list)
    return SQL_REQUEST_POPULATION_AGG.format(clause=clause)

  @staticmethod
  def get_siret_request(siret_frame, exges_list):
    """

    :param exges_list:
    :param siret_frame:
    :return:
    """
    clause = AggregationRequestMaker._get_siret_by_year_clause(siret_frame, exges_list)
    return SQL_REQUEST_COLLECTIVITE_AGG.format(clause=clause)
