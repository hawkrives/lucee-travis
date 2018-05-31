#!/bin/bash

set -e
# set -v

function images {
	IFS=',' read -ra VERSIONS <<< "$LUCEE_VERSION"
	for version in "${VERSIONS[@]}"; do
		IFS=',' read -ra SERVERS <<< "$LUCEE_SERVER"
		for server in "${SERVERS[@]}"; do
			IFS=',' read -ra VARIANTS <<< "$LUCEE_VARIANTS"
			for variant in "${VARIANTS[@]}"; do
				# echo "lucee/lucee:$version"
				# echo "lucee/lucee:$version$variant"
				# echo "lucee/lucee:$version$variant$server"
				echo "lucee/lucee:$version$variant$server-tomcat$TOMCAT_VERSION-$TOMCAT_JAVA_VERSION$TOMCAT_BASE"
			done
		done
	done #| sort | uniq
}

for tag in $(images); do
	bash ./build-single-image.sh "$tag"
done
