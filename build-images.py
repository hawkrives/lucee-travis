#!/usr/bin/env python3

import subprocess
import os
import re
import yaml

with open('./matrix.yaml') as matrix_file:
	matrix = yaml.safe_load(matrix_file)

is_master_build = os.getenv('TRAVIS_BRANCH', None) == 'master'
print('will we deploy:', 'yes' if is_master_build else 'no')

def get_minor_version(ver):
	return re.sub(r"^(\d+\.\d+).*", r"\1", ver)

def discover_images():
	lucee_versions = os.getenv('LUCEE_VERSION').split(',')
	lucee_servers = os.getenv('LUCEE_SERVER').split(',')
	lucee_variants = os.getenv('LUCEE_VARIANTS').split(',')
	tomcat_version = os.getenv('TOMCAT_VERSION')
	tomcat_java_version = os.getenv('TOMCAT_JAVA_VERSION')
	tomcat_base_image = os.getenv('TOMCAT_BASE_IMAGE')

	for lucee_version in lucee_versions:
		for lucee_server in lucee_servers:
			for lucee_variant in lucee_variants:
				alternate_tags = []

				is_default_tomcat = \
					tomcat_java_version == matrix['default_tomcat']['TOMCAT_JAVA_VERSION'] and \
					tomcat_version == matrix['default_tomcat']['TOMCAT_VERSION'] and \
					tomcat_base_image == matrix['default_tomcat']['TOMCAT_BASE_IMAGE']

				if is_default_tomcat:
					alternate_tags.append(f"{lucee_version}{lucee_variant}{lucee_server}")

				config = {
					'LUCEE_VERSION': lucee_version,
					'LUCEE_SERVER': lucee_server,
					'LUCEE_VARIANT': lucee_variant,
					'TOMCAT_VERSION': tomcat_version,
					'TOMCAT_JAVA_VERSION': tomcat_java_version,
					'TOMCAT_BASE_IMAGE': tomcat_base_image,
				}

				manual_tags = [
					tag_name
					for tag_name, tag_requirements in matrix['tags'].items()
					if all([config[key] == tag_requirements[key] for key in set(config.keys())])
				]
				alternate_tags += manual_tags

				yield {
					'primary_tag': f"{lucee_version}{lucee_variant}{lucee_server}-tomcat{tomcat_version}-{tomcat_java_version}{tomcat_base_image}",
					'alternate_tags': alternate_tags,
					'base_tag': f"lucee:{lucee_version}-tomcat{tomcat_version}-{tomcat_java_version}{tomcat_base_image}",
					'config': config,
				}

for image in discover_images():
	minor = get_minor_version(image['config']['LUCEE_VERSION'])

	build_args = {
		**image['config'],
		'LUCEE_MINOR': minor,
		'LUCEE_IMAGE': image['base_tag'],
	}
	build_args = [arg for key, value in build_args.items() for arg in ['--build-arg', f"{key}={value}"]]

	tags = [image['primary_tag'], *image['alternate_tags']]
	tags = [arg for value in tags for arg in ['-t', f"kryestofer/lucee:{value}"]]

	if not image['config']['LUCEE_SERVER'] and not image['config']['LUCEE_VARIANT']:
		tags += ["-t", image['base_tag']]

	if image['config']['LUCEE_SERVER'] == '-nginx':
		if image['config']['TOMCAT_BASE_IMAGE'] == '-alpine':
			dockerfile = './Dockerfile.nginx.alpine'
		else:
			dockerfile = './Dockerfile.nginx'
	else:
		dockerfile = './Dockerfile'

	command = [
		"docker", "build",
		*build_args,
		"-f", dockerfile,
		*tags,
		".",
	]

	print(' '.join(command))

	proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
	print(proc.stdout)
	print(proc.stderr)

	for tag in [tag for tag in tags if tag.startswith('kryestofer/')]:
		print(tag)
		if is_master_build:
			push_proc = subprocess.run(["docker", "push", tag], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
			print(push_proc.stdout)
			print(push_proc.stderr)
		else:
			print('not on master; skipping deployment')
