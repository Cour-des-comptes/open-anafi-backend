class DatabaseTools:
	@staticmethod
	def get_final_query(tables, joins_conditions, where_conditions):
		selected_columns = []
		from_selections = []
		singleton_joins = True

		select = ""
		froms = ""
		joins = ""
		group_by = ""

		where = "WHERE" if len(where_conditions) > 0 or len(joins_conditions) > 0 else ""
		optional_and = "AND" if len(where_conditions) > 0 and len(joins_conditions) > 0 else ""

		for table in tables:
			current_table_name = table['name']
			from_selections.append(current_table_name)

			for column in table['columns']:
				if column['selected'] and column['option'] == "SUM":
					selected_columns.append(f"sum({current_table_name}.{column['name']})")
				elif column['selected'] and column['option'] == "GROUP BY":
					selected_columns.append(f"{current_table_name}.{column['name']}")
					group_by += f"{current_table_name}.{column['name']}, "
				elif column['selected']:
					selected_columns.append(f"{current_table_name}.{column['name']}")

		for join in joins_conditions:
			if singleton_joins:
				singleton_joins = False
				joins += f"{join.get('column1')} = {join.get('column2')}"
			else:
				joins += f" AND {join.get('column1')} = {join.get('column2')}"


		for selected_column in selected_columns:
			if selected_column == selected_columns[-1]:
				select += f' {selected_column} '
			else:
				select += f' {selected_column}, '

		for from_selection in from_selections:
			if from_selection == from_selections[-1]:
				froms += f' {from_selection} '
			else:
				froms += f' {from_selection}, '

		group_by_keyword = "GROUP BY" if group_by != "" else "" 

		final_query = f'SELECT {select} FROM {froms} {where} {joins} {optional_and} {where_conditions} {group_by_keyword} {group_by[:-2]} LIMIT 1000'

		return final_query

	@staticmethod
	def get_tables_from_columns(columns):
		result = []
		for column in columns:
			result.append(column['name'].split('.')[0])
		return list(set(result))

	@staticmethod
	def format_condition(condition):
		result = ""
		data = condition.get('data')

		if type(data) is str:
			#C'est une constante tappée
			pass
		else:
			#C'est un tableau qui contient une liste
			if condition.get('operator').get('data') == 'IN':
				result += f"{condition.get('name')} IN ("
				for value in data:
					result += f"'{value}', " if type(value) is str else f"{value}, "
				result = result[:-2]
				result += ') '
			else:
				result = f"{condition.get('name')} {condition.get('operator').get('data')} '{data[0]}' " if type(data[0]) is str else f"{condition.get('name')} {condition.get('operator').get('data')} {data[0]} "

		return result

	@staticmethod
	def format_where(where_conditions):
		result = ""
		for item in where_conditions:
			if item.get('type') == "condition":
				result += DatabaseTools.format_condition(item)
			else:
				result += f"{item.get('data')} "
		return result

	@staticmethod
	def get_final_query_simple(columns, joins_conditions, where_conditions):
		selected_columns = []
		from_selections = []
		singleton_joins = True

		tables = DatabaseTools.get_tables_from_columns(columns)

		select = ""
		froms = ""
		joins = ""
		group_by = ""
		formatted_where = DatabaseTools.format_where(where_conditions)

		where = "WHERE" if len(where_conditions) > 0 or len(joins_conditions) > 0 else ""
		optional_and = "AND" if len(where_conditions) > 0 and len(joins_conditions) > 0 else ""

		for table in tables:
			from_selections.append(table)

		for column in columns:
			if column['inResult'] and column['option'] == "SUM":
				selected_columns.append(f"sum({column['name']})")
			elif column['inResult'] and column['option'] == "GROUP BY":
				selected_columns.append(f"{column['name']}")
				group_by += f"{column['name']}, "
			elif column['inResult']:
				selected_columns.append(f"{column['name']}")

		for join in joins_conditions:
			if singleton_joins:
				singleton_joins = False
				joins += f"{join.get('column1')} = {join.get('column2')}"
			else:
				joins += f" AND {join.get('column1')} = {join.get('column2')}"

		for selected_column in selected_columns:
			if selected_column == selected_columns[-1]:
				select += f' {selected_column} '
			else:
				select += f' {selected_column}, '

		for from_selection in from_selections:
			if from_selection == from_selections[-1]:
				froms += f' {from_selection} '
			else:
				froms += f' {from_selection}, '

		group_by_keyword = "GROUP BY" if group_by != "" else ""

		final_query = f'SELECT {select} FROM {froms} {where} {joins} {optional_and} {formatted_where} {group_by_keyword} {group_by[:-2]} LIMIT 1000'

		return final_query