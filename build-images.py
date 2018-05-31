#!/usr/bin/env python3

import subprocess
import os
import re
import yaml

with open('./matrix.yaml') as matrix_file:
	matrix = yaml.safe_load(matrix_file)

def get_minor_version(ver):
	return re.sub(r"^(\d+\.\d+).*", r"\1", ver)

def discover_images():
	lucee_versions = os.getenv('LUCEE_VERSION').split(',')
	lucee_servers = os.getenv('LUCEE_SERVER').split(',')
	lucee_variants = os.getenv('LUCEE_VARIANTS').split(',')
	tomcat_version = os.getenv('TOMCAT_VERSION')
	tomcat_java_version = os.getenv('TOMCAT_JAVA_VERSION')
	tomcat_base_image = os.getenv('TOMCAT_BASE')

	for lucee_version in lucee_versions:
		for lucee_server in lucee_servers:
			for lucee_variant in lucee_variants:
				alternate_tags = []

				is_default_tomcat = \
					tomcat_java_version == matrix['defaults']['TOMCAT_JAVA_VERSION'] and \
					tomcat_version == matrix['defaults']['TOMCAT_VERSION'] and \
					tomcat_base_image == matrix['defaults']['TOMCAT_BASE']

				if is_default_tomcat:
					alternate_tags.append(f"lucee/lucee:{lucee_version}{lucee_variant}{lucee_server}")
				if is_default_tomcat and (not lucee_variant and not lucee_server):
					alternate_tags.append(f"lucee/lucee:{get_minor_version(lucee_version)}")

				yield {
					'primary_tag': f"lucee/lucee:{lucee_version}{lucee_variant}{lucee_server}-tomcat{tomcat_version}-{tomcat_java_version}{tomcat_base_image}",
					'alternate_tags': alternate_tags,
				}

for image in discover_images():
	print(image)
