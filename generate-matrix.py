import yaml

with open('./matrix.yaml') as matrix_input:
	matrix = yaml.safe_load(matrix_input)

# print(matrix)

rows = []

for TOMCAT_VERSION in matrix['TOMCAT_VERSION']:
	for TOMCAT_JAVA_VERSION in matrix['TOMCAT_JAVA_VERSION']:
		for TOMCAT_BASE in matrix['TOMCAT_BASE']:
			for LUCEE_VERSION in matrix['LUCEE_VERSION']:
				for LUCEE_SERVER in matrix['LUCEE_SERVER']:
					for LUCEE_VARIANT in matrix['LUCEE_VARIANT']:
						row = {
							'TOMCAT_VERSION': TOMCAT_VERSION,
							'TOMCAT_JAVA_VERSION': TOMCAT_JAVA_VERSION,
							'TOMCAT_BASE': TOMCAT_BASE,
							'LUCEE_VERSION': LUCEE_VERSION,
							'LUCEE_SERVER': LUCEE_SERVER,
							'LUCEE_VARIANT': LUCEE_VARIANT,
						}

						matches = False
						for exclusion in matrix['exclusions']:
							exclusion_keys = set(exclusion.keys())
							matches = matches or all([row[key] == exclusion[key] for key in exclusion_keys])
						if matches:
							continue

						rows.append(row)

strs = [
	" ".join([
		f"TOMCAT_VERSION={row['TOMCAT_VERSION']}",
		f"TOMCAT_JAVA_VERSION={row['TOMCAT_JAVA_VERSION']}",
		f"TOMCAT_BASE={row['TOMCAT_BASE']}",
		f"LUCEE_VERSION={row['LUCEE_VERSION']}",
		f"LUCEE_SERVER={row['LUCEE_SERVER']}",
		f"LUCEE_VARIANT={row['LUCEE_VARIANT']}",
	]) for row in rows
]

# for combo in strs:
# 	print(combo)

with open('./.travis.yml') as travis_config:
	conf = yaml.safe_load(travis_config)

conf['env']['matrix'] = strs

conf_stringified = yaml.dump(conf, default_flow_style=False, width=240, indent=2)

print(conf_stringified)

with open('./.travis.yml', 'w') as travis_config:
	travis_config.write(conf_stringified)
