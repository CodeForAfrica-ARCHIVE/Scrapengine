#/bin/bash
# append wget on each line
typeset TMP_FILE=$( mktemp )
touch "${TMP_FILE}"
cp -p /tmp/ke_gazettes.txt "${TMP_FILE}"
sed -e 's/^/wget /' "${TMP_FILE}" > /tmp/ke_gazettes.txt
