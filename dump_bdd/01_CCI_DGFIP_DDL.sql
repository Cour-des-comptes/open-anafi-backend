
-- Drop table

-- DROP TABLE public.collectivite;

CREATE TABLE public.collectivite (
	exer int2 NULL,
	ident varchar(14) NULL,
	idhel varchar(250) NULL,
	ndept varchar(3) NULL,
	insee varchar(3) NULL,
	lcomm varchar(250) NULL,
	mpoid int4 NULL,
	nomen varchar(10) NULL,
	cpste varchar(10) NULL,
	categ varchar(10) NULL,
	siret varchar(14) NULL,
	finess varchar(9) NULL,
	cnumd varchar(3) NULL,
	canex varchar(1) NULL,
	cappl varchar(1) NULL,
	ccolr varchar(5) NULL,
	cnome varchar(250) NULL,
	csnom varchar(250) NULL,
	lbudg varchar(250) NULL,
	cbudg varchar(250) NULL,
	secteur varchar(250) NULL,
	catbuh varchar(250) NULL,
	catbug varchar(250) NULL,
	codbud1 varchar(250) NULL,
	codbud2 varchar(250) NULL,
	ctype varchar(3) NULL,
	cstyp varchar(250) NULL,
	cacti varchar(250) NULL,
	dcrea varchar(4) NULL,
	damaj varchar(250) NULL,
	hrmaj varchar(250) NULL,
	coma1 varchar(250) NULL,
	nb1 varchar(250) NULL,
	nb2 varchar(250) NULL,
	nb3 varchar(250) NULL,
	nb4 varchar(250) NULL,
	nbann1 varchar(250) NULL,
	nbann2 varchar(250) NULL,
	siret1 varchar(250) NULL,
	lprin varchar(250) NULL,
	cregi varchar(250) NULL,
	canor varchar(250) NULL,
	crecu varchar(250) NULL,
	siret2 varchar(250) NULL,
	ctrd_prev varchar(250) NULL,
	ctrd_exec varchar(250) NULL,
	dated_prev varchar(250) NULL,
	dated_exec varchar(250) NULL,
	codique varchar(250) NULL,
	ddefi varchar(250) NULL,
	cgest varchar(250) NULL,
	dsirt varchar(250) NULL,
	nvoie varchar(250) NULL,
	cvoie varchar(250) NULL,
	tvoie varchar(250) NULL,
	lvoie varchar(250) NULL,
	lgest varchar(250) NULL,
	codie varchar(250) NULL,
	siren_epci varchar(250) NULL,
	nj_epci varchar(250) NULL,
	fisc_epci varchar(250) NULL,
	nb_com varchar(250) NULL,
	cpt515 bpchar(1) NULL,
	dt_crea timestamp NULL,
	dsi_strate_2013 varchar(30) NULL DEFAULT 'Aucune strate'::character varying,
	modif_d timestamp NULL,
	creat_d timestamp NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX collectivite_ctype_idx ON public.collectivite USING btree (ctype);
CREATE INDEX collectivite_ex_idt_no_idx ON public.collectivite USING btree (exer, ident, nomen);
CREATE INDEX collectivite_exer_ident_idx ON public.collectivite USING btree (exer, ident);
CREATE INDEX collectivite_exer_idx ON public.collectivite USING btree (exer);
CREATE INDEX collectivite_finess_idx ON public.collectivite USING btree (finess);
CREATE INDEX collectivite_ident_idx ON public.collectivite USING btree (ident);
CREATE INDEX collectivite_nomen_idx ON public.collectivite USING btree (nomen);

-- Drop table

-- DROP TABLE public.comptes;

CREATE TABLE public.comptes (
	comptes varchar(250) NULL,
	libelles varchar(250) NULL,
	fin_num_comptes varchar(1) NULL,
	modif_d timestamp NULL,
	creat_d timestamp NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX comptes_cpt_idx ON public.comptes USING btree (comptes);

-- Drop table

-- DROP TABLE public.comptes_prev;

CREATE TABLE public.comptes_prev (
	comptes varchar(250) NULL,
	libelle bpchar(15) NULL,
	creat_d timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	modif_d timestamp NULL
);
CREATE INDEX comptes_prev_cpt_idx ON public.comptes_prev USING btree (comptes);

-- Drop table

-- DROP TABLE public.departement;

CREATE TABLE public.departement (
	dp_code varchar(5) NOT NULL,
	dp_nom varchar(64) NOT NULL,
	dp_cd_id_reg varchar(5) NULL,
	reg_name varchar(50) NULL,
	creat_d timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	modif_d timestamp NULL
);
CREATE INDEX departement_code_idx ON public.departement USING btree (dp_code);

-- Drop table

-- DROP TABLE public.execution_2010;

CREATE TABLE public.execution_2010 (
	exercice int2 NULL,
	ident varchar(14) NULL,
	fonction varchar(16) NULL,
	comptes varchar(250) NULL,
	cptop int4 NULL,
	cptdeb numeric(22,2) NULL,
	cptcre numeric(22,2) NULL,
	dp varchar(1) NULL,
	dt_crea timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	creat_d timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	modif_d timestamp NULL
)
PARTITION BY LIST (exercice);
CREATE INDEX execution_2010_cmpts_idx ON ONLY public.execution_2010 USING btree (comptes);
CREATE INDEX execution_2010_cptcr_idx ON ONLY public.execution_2010 USING btree (cptcre);
CREATE INDEX execution_2010_cptdb_idx ON ONLY public.execution_2010 USING btree (cptdeb);
CREATE INDEX execution_2010_cptp_idx ON ONLY public.execution_2010 USING btree (cptop);
CREATE INDEX execution_2010_dp_idx ON ONLY public.execution_2010 USING btree (dp);
CREATE INDEX execution_2010_ex_idx ON ONLY public.execution_2010 USING btree (exercice);
CREATE INDEX execution_2010_idnt_cmpts_ex_cptp_dp_cptdb_cptcr_idx ON ONLY public.execution_2010 USING btree (ident, comptes, exercice, cptop, dp, cptdeb, cptcre);
CREATE INDEX execution_2010_idnt_cmpts_ex_cptp_dp_cptdb_idx ON ONLY public.execution_2010 USING btree (ident, comptes, exercice, cptop, dp, cptdeb);
CREATE INDEX execution_2010_idnt_cmpts_ex_cptp_dp_idx ON ONLY public.execution_2010 USING btree (ident, comptes, exercice, cptop, dp);
CREATE INDEX execution_2010_idnt_cmpts_ex_cptp_idx ON ONLY public.execution_2010 USING btree (ident, comptes, exercice, cptop);
CREATE INDEX execution_2010_idnt_cmpts_ex_idx ON ONLY public.execution_2010 USING btree (ident, comptes, exercice);
CREATE INDEX execution_2010_idnt_idx ON ONLY public.execution_2010 USING btree (ident);

-- Drop table

-- DROP TABLE public.exercice_gestion;

CREATE TABLE public.exercice_gestion (
	exercice int2 NULL,
	"position" varchar(20) NULL,
	creat_d timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	modif_d timestamp NULL
);

-- Drop table

-- DROP TABLE public.metrics;

CREATE TABLE public.metrics (
	exer int2 NULL,
	ident varchar(14) NULL,
	population int4 NULL,
	dt_crea timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	modif_d timestamp NULL,
	creat_d timestamp NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX metrics_exer_ident_idx ON public.metrics USING btree (exer, ident);
CREATE INDEX metrics_exer_ident_pop_idx ON public.metrics USING btree (exer, ident, population);

-- Drop table

-- DROP TABLE public.nature_juridique;

CREATE TABLE public.nature_juridique (
	code_nat_jur varchar(250) NOT NULL,
	libelle_nature varchar(250) NOT NULL,
	creat_d timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	modif_d timestamp NULL
);

-- Drop table

-- DROP TABLE public.nomenclature;

CREATE TABLE public.nomenclature (
	nomen varchar(10) NOT NULL,
	libelle_nomenclature varchar(250) NOT NULL,
	creat_d timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	modif_d timestamp NULL
);
CREATE INDEX nomenclature_libi_idx ON public.nomenclature USING btree (libelle_nomenclature);
CREATE INDEX nomenclature_nomen_idx ON public.nomenclature USING btree (nomen);

-- Drop table

-- DROP TABLE public.operations;

CREATE TABLE public.operations (
	exer int2 NULL,
	code_operation int4 NULL,
	libelle_operation varchar(250) NULL,
	creat_d timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	modif_d timestamp NULL
);
CREATE INDEX operations_cd_op_idx ON public.operations USING btree (code_operation);
CREATE INDEX operations_lib_idx ON public.operations USING btree (libelle_operation);

-- Drop table

-- DROP TABLE public.prevision;

CREATE TABLE public.prevision (
	exercice int2 NULL,
	ident varchar(14) NULL,
	fonction varchar(16) NULL,
	comptes varchar(250) NULL,
	code varchar(1) NULL,
	mtbp numeric(22,2) NULL,
	mtdm numeric(22,2) NULL,
	mtvc numeric(22,2) NULL,
	dp varchar(1) NULL,
	dt_crea timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	creat_d timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	modif_d timestamp NULL
)
PARTITION BY LIST (exercice);
CREATE INDEX prevision_cmpts_idx ON ONLY public.prevision USING btree (comptes);
CREATE INDEX prevision_ex_idx ON ONLY public.prevision USING btree (exercice);
CREATE INDEX prevision_idnt_cmpts_ex_idx ON ONLY public.prevision USING btree (ident, comptes, exercice);
CREATE INDEX prevision_idnt_idx ON ONLY public.prevision USING btree (ident);

-- Drop table

-- DROP TABLE public.type_activite;

CREATE TABLE public.type_activite (
	code_activite varchar(250) NOT NULL,
	libelle_activite varchar(250) NOT NULL,
	creat_d timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	modif_d timestamp NULL
);

-- Drop table

-- DROP TABLE public.type_budget;

CREATE TABLE public.type_budget (
	code_budget varchar(250) NOT NULL,
	libelle_budget varchar(250) NOT NULL,
	creat_d timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	modif_d timestamp NULL
);

-- Drop table

-- DROP TABLE public.type_etablissements;

CREATE TABLE public.type_etablissements (
	code_type_ets varchar(250) NOT NULL,
	libelle_ets varchar(250) NOT NULL,
	code_nat_jur varchar(250) NOT NULL,
	creat_d timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	modif_d timestamp NULL
);
CREATE INDEX typ_ets_lib_idx ON public.type_etablissements USING btree (libelle_ets);

-- Drop table

-- DROP TABLE public.type_sous_type_etablissements;

CREATE TABLE public.type_sous_type_etablissements (
	code_type_ets varchar(250) NOT NULL,
	code_sous_type varchar(250) NOT NULL,
	libelle_sous_type varchar(250) NOT NULL,
	creat_d timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	modif_d timestamp NULL
);
