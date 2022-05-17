# Holded Backup - Python
Backup tool for Holded accounts on Python.

This application backups all contacts, invoices, drafts, payments, services, ... from [Holded](https://holded.com) to a MongoDB database using holded API.
You need a Holded API developer token for using this application.

You must to have installed a mongo server locally for using this version.

** THIS BACKUP WILL OVERWRITE A PREVIOUS BACKUP **

## INSTALLATION

$> pip3 install asyncio aiohttp motor

## USE

$> python3 backupMongo.py mongoDatabase holdedUserApiKey









Antonio M. Tenorio
