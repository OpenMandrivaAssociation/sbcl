#!/bin/sh
package=sbcl
curl -s -L -A 'Mozilla/5.0 (X11; Linux x86_64)' https://sourceforge.net/projects/${package}/files/ |grep -b1 'Download Latest Version' |tail -n1 |sed -e "s,.*>${package}-,,;s,-source\.tar.*,,"

