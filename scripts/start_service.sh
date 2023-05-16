#!/bin/bash
ls -lah /opt/oddsMachines/new-staging-parsers-main/
find /opt/oddsMachines/new-staging-parsers-main/ -type f -exec chmod 660 {} \;
find /opt/oddsMachines/new-staging-parsers-main/ -type d -exec chmod 770 {} \;
sudo chown -R python-runner:om_adm /opt/oddsMachines/new-staging-parsers-main/
sudo systemctl start new_staging_eurobet_parser.service 
