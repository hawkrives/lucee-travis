import itertools
import sys
import yaml


def should_include_combo(combination, exclusions):
	for exclusion in exclusions:
		if all([combination[key] == exclusion[key] for key in set(exclusion.keys())]):
			return False

	return True


def find_all_matrix_rows(matrix):
	matrix_vars = matrix['matrix']

	for TOMCAT_VERSION in matrix_vars['TOMCAT_VERSION']:
		for TOMCAT_JAVA_VERSION in matrix_vars['TOMCAT_JAVA_VERSION']:
			for TOMCAT_BASE_IMAGE in matrix_vars['TOMCAT_BASE_IMAGE']:
				for LUCEE_VERSION in matrix_vars['LUCEE_VERSION']:
					for LUCEE_SERVER in matrix_vars['LUCEE_SERVER']:
						for LUCEE_VARIANT in matrix_vars['LUCEE_VARIANT']:
							yield {
								'TOMCAT_VERSION': TOMCAT_VERSION,
								'TOMCAT_JAVA_VERSION': TOMCAT_JAVA_VERSION,
								'TOMCAT_BASE_IMAGE': TOMCAT_BASE_IMAGE,
								'LUCEE_VERSION': LUCEE_VERSION,
								'LUCEE_SERVER': LUCEE_SERVER,
								'LUCEE_VARIANT': LUCEE_VARIANT,
							}


def combine_rows_by_tomcat(rows):
	def group_by_tomcat(row):
		return (row['TOMCAT_VERSION'], row['TOMCAT_JAVA_VERSION'], row['TOMCAT_BASE_IMAGE'])

	for tomcat, combination in itertools.groupby(rows, group_by_tomcat):
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

		yield result


def combinations_to_travis_env(combinations):
	for combo in combinations:
		lucee_versions = ",".join(sorted(combo['LUCEE_VERSION']))
		lucee_servers = ",".join(sorted(combo['LUCEE_SERVER']))
		lucee_variants = ",".join(sorted(combo['LUCEE_VARIANT']))

		yield " ".join([
			f"TOMCAT_VERSION={combo['TOMCAT_VERSION']}",
			f"TOMCAT_JAVA_VERSION={combo['TOMCAT_JAVA_VERSION']}",
			f"TOMCAT_BASE_IMAGE={combo['TOMCAT_BASE_IMAGE']}",
			f"LUCEE_VERSION={lucee_versions}",
			f"LUCEE_SERVER={lucee_servers}",
			f"LUCEE_VARIANTS={lucee_variants}",
		])


def main():
	with open('./matrix.yaml') as matrix_input:
		matrix = yaml.safe_load(matrix_input)

	rows = [
		row
		for row in find_all_matrix_rows(matrix)
		if should_include_combo(row, matrix['exclusions'])
	]

	combinations = combine_rows_by_tomcat(rows)

	travis_env_rows = combinations_to_travis_env(combinations)

	conf = {
		**matrix['travis'],
		'env': {
			'matrix': travis_env_rows,
		},
	}

	conf_stringified = yaml.dump(conf, default_flow_style=False, width=240, indent=2)

	print(conf_stringified)

	with open('./.travis.yml', 'w') as travis_config:
		travis_config.write(conf_stringified)
