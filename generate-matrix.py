import yaml
import itertools
import sys

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

combinations = []
for tomcat, combination in itertools.groupby(rows, lambda row: (row['TOMCAT_VERSION'], row['TOMCAT_JAVA_VERSION'], row['TOMCAT_BASE'])):
	result = {
		'TOMCAT_VERSION': tomcat[0],
		'TOMCAT_JAVA_VERSION': tomcat[1],
		'TOMCAT_BASE': tomcat[2],
		'LUCEE_VERSION': set(),
		'LUCEE_SERVER': set(),
		'LUCEE_VARIANT': set(),
	}

	for row in combination:
		result['LUCEE_VERSION'].add(str(row['LUCEE_VERSION']))
		result['LUCEE_SERVER'].add(str(row['LUCEE_SERVER']))
		result['LUCEE_VARIANT'].add(str(row['LUCEE_VARIANT']))

	combinations.append(result)

strs = []
for combo in combinations:
	lucee_versions = ",".join(sorted(combo['LUCEE_VERSION']))
	lucee_servers = ",".join(sorted(combo['LUCEE_SERVER']))
	lucee_variants = ",".join(sorted(combo['LUCEE_VARIANT']))

	strs.append(" ".join([
		f"TOMCAT_VERSION={combo['TOMCAT_VERSION']}",
		f"TOMCAT_JAVA_VERSION={combo['TOMCAT_JAVA_VERSION']}",
		f"TOMCAT_BASE={combo['TOMCAT_BASE']}",
		f"LUCEE_VERSION={lucee_versions}",
		f"LUCEE_SERVER={lucee_servers}",
		f"LUCEE_VARIANTS={lucee_variants}",
	]))

# for combo in strs:
# 	print(combo)

# sys.exit(0)
conf = {
	**matrix['travis'],
	'env': {
		'matrix': strs,
	},
}

conf_stringified = yaml.dump(conf, default_flow_style=False, width=240, indent=2)

print(conf_stringified)

with open('./.travis.yml', 'w') as travis_config:
	travis_config.write(conf_stringified)
