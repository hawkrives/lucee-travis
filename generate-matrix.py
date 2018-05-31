import yaml
import itertools
import sys

with open('./matrix.yaml') as matrix_input:
	matrix = yaml.safe_load(matrix_input)

# print(matrix)

matrix_vars = matrix['matrix']
rows = []

for TOMCAT_VERSION in matrix_vars['TOMCAT_VERSION']:
	for TOMCAT_JAVA_VERSION in matrix_vars['TOMCAT_JAVA_VERSION']:
		for TOMCAT_BASE_IMAGE in matrix_vars['TOMCAT_BASE_IMAGE']:
			for LUCEE_VERSION in matrix_vars['LUCEE_VERSION']:
				for LUCEE_SERVER in matrix_vars['LUCEE_SERVER']:
					for LUCEE_VARIANT in matrix_vars['LUCEE_VARIANT']:
						row = {
							'TOMCAT_VERSION': TOMCAT_VERSION,
							'TOMCAT_JAVA_VERSION': TOMCAT_JAVA_VERSION,
							'TOMCAT_BASE_IMAGE': TOMCAT_BASE_IMAGE,
							'LUCEE_VERSION': LUCEE_VERSION,
							'LUCEE_SERVER': LUCEE_SERVER,
							'LUCEE_VARIANT': LUCEE_VARIANT,
						}

						should_exclude = any([
							True
							for exclusion in matrix['exclusions']
							if all([row[key] == exclusion[key] for key in set(exclusion.keys())])
						])
						if should_exclude:
							continue

						rows.append(row)

combinations = []
for tomcat, combination in itertools.groupby(rows, lambda row: (row['TOMCAT_VERSION'], row['TOMCAT_JAVA_VERSION'], row['TOMCAT_BASE_IMAGE'])):
	result = {
		'TOMCAT_VERSION': tomcat[0],
		'TOMCAT_JAVA_VERSION': tomcat[1],
		'TOMCAT_BASE_IMAGE': tomcat[2],
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
		f"TOMCAT_BASE_IMAGE={combo['TOMCAT_BASE_IMAGE']}",
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
