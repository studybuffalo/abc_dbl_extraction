def generate_statement(table):
	"""Generates statement for MySQL insertion.
	
	Takes table provided and generates the appropriate MySQL satement
	
	Args:
		table: the table name in which the string will be inserted
	
	Returns:
		returns a string statement suitable for MySQL insertion.
		
	Raises:
		None.
	"""

	if table == "abc_price":
		statement = ("INSERT INTO abc_price (url,din,"
					 "brand_name,strength,route,dosage_form,"
					 "generic_name,unit_price,lca,lca_text,"
					 "unit_issue) values (%s,%s,%s,%s,%s,%s,%s,%s,"
					 "%s,%s,%s)")
	
	elif table == "abc_coverage":
		statement = ("INSERT INTO abc_coverage (url,coverage,"
					 "criteria,criteria_sa,criteria_p,"
					 "group_1,group_66,group_66a,"
					 "group_19823,group_19823a,group_19824,"
					 "group_20400,group_20403,group_20514,"
					 "group_22128,group_23609) values (%s,%s,%s,"
					 "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
	
	elif table == "abc_special_authorization":
		statement = ("INSERT INTO abc_special_authorization (url,"
					 "title,link) values (%s,%s,%s)")
	
	elif table == "abc_ptc":
		statement = ("INSERT INTO abc_ptc (url,ptc_1,ptc_1_text,"
					 "ptc_2,ptc_2_text,ptc_3,ptc_3_text,ptc_4,"
					 "ptc_4_text) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)")
	
	elif table == "abc_atc":
		statement = ("INSERT INTO abc_atc (url,atc_1,atc_1_text,"
					 "atc_2,atc_2_text,atc_3,atc_3_text,"
					 "atc_4,atc_4_text,atc_5,atc_5_text) values (%s,"
					 "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
	
	elif table == "abc_extra_information":
		statement = ("INSERT INTO abc_extra_information (url,"
					 "date_listed,date_discontinued,"
					 "manufacturer,schedule,"
					 "interchangeable) values (%s,%s,%s,%s,%s,%s)")
	
	return statement