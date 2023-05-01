#!/bin/bash
# Usage: bash healthCheckFromUrl.sh <URL>
# Use curl to access a URL. If it fails, send a notification email to addresses in MAIL_LIST. 
# This script is located in /root and scheduled in /etc/crontab
#
# Steps to use this script (only do this in production):
# 1. Add your email address to MAIL_LIST with format <mail 1>;<mail 2>;<mail 3>:...
# 2. chmod 744 healthCheckFromUrl.sh
# 3. chown root accessFromUrl.sh
# 4. chgrp root accessFromUrl.sh
# 5. move this script to /root
# 6. Add this to /etc/crontab: 0  0,6,12,18  * * *   root    /root/healthCheckFromUrl.sh https://rodan-staging.simssa.ca/
# 7. Add this to /etc/crontab: 0  0,6,12,18  * * *   root    /root/healthCheckFromUrl.sh https://rodan2.simssa.ca/

URL=$1
MAIL_LIST="wan.y.lin@mail.mcgill.ca"

if curl -sSf $URL > /dev/null 2>&1 --connect-timeout 10; then
    logger -t HealthCheck "$URL is up!"
else
    IFS=';' read -ra ARRAY <<< "$MAIL_LIST"
    for MAIL in "${ARRAY[@]}"; do
        DATE=$(date)
        mail -s "Cannot access $URL" -r rodan@production-rodan2-gpu $MAIL <<< "Timestamp: $DATE"
    done
fi
