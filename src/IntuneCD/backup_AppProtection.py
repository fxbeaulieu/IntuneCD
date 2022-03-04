#!/usr/bin/env python3

"""
This module backs up all App Protection Polices in Intune.

Parameters
----------
path : str
    The path to save the backup to
output : str
    The format the backup will be saved as
token : str
    The token to use for authenticating the request
"""

import json
import os
import yaml

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .graph_batch import batch_assignment, get_object_assignment

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceAppManagement/managedAppPolicies"

## Get all App Protection policies and save them in specified path
def savebackup(path, output, token):
    configpath = path+"/"+"App Protection/"
    data = makeapirequest(endpoint, token)

    assignment_responses = batch_assignment(data,f'deviceAppManagement/','/assignments',token,app_protection=True)

    ## If profile is ManagedAppConfiguration, skip to next
    for profile in data['value']:
        if profile['@odata.type'] == "#microsoft.graph.targetedManagedAppConfiguration":
            continue

        assignments = get_object_assignment(profile['id'],assignment_responses)
        if assignments:
            profile['assignments'] = assignments
        
        remove_keys = {'id', 'createdDateTime', 'version',
                       'lastModifiedDateTime', 'deployedAppCount', 'isAssigned'}
        for k in remove_keys:
            profile.pop(k, None)

        print("Backing up App Protection: " + profile['displayName'])
        if os.path.exists(configpath) == False:
            os.mkdir(configpath)

        if 'targetedAppManagementLevels' in profile:
            fname = clean_filename(f"{profile['displayName']}_{profile['targetedAppManagementLevels']}")
        else:
            fname = clean_filename(f"{profile['displayName']}_{str(profile['@odata.type'].split('.')[2])}")

        ## Save App Protection as JSON or YAML depending on configured value in "-o"
        if output != "json":
            with open(configpath+fname+".yaml", 'w') as yamlFile:
                yaml.dump(profile, yamlFile, sort_keys=False,
                          default_flow_style=False)
        else:
            with open(configpath+fname+".json", 'w') as jsonFile:
                json.dump(profile, jsonFile, indent=10)