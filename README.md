# utils-api-godaddy

This python script faciliates retrieving domain data from GoDaddy via its API. Requires reference to a file containing API key data. Will retrieve live/active domains and all records for each of those domains. The resulting record sets are saved as a CSV.

The API key data file should contain a single value, composed of an API key and a secret. This information is needed for the API calls to be made against your specific account. Any lines in the file that start with a hashtag (#) are treated as comments and ignored.

Example API key data file contents:
```
#API key and secret, separated by a colon
dE7hi3bc9xxxxxxxxxxxxxxxxxxxxxg7hi2fgx:XhfLuxxxxxxxxxxxxxxx8d756
```

Usage:
```
python utils-api-godaddy_v0.1.py -k gdapikey.cfg
python utils-api-godaddy_v0.1.py -k /home/jdjalm/gdapikey.cfg -s /var/backups/godaddy/
```

Possible future features:

1. Add option to attempt to retrieve any status domain
2. Add option to retrieve records for <=60 domains without artificial delay
3. Add option to save all records in one file
4. Support pagination on the call responses
