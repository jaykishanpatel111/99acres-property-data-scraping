import csv
import json
import os
import logging
from datetime import datetime
from random import choice, uniform, random
import time
import requests

from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent

import threading
from threading import Lock


# Create a lock object to prevent CSV corruption
csv_lock = threading.Lock()


list_apitoken =['eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk4NjM0NDAuNzUyLCJleHAiOjE3Njk4NjM1NjAuNzUyLCJocSI6IjNjZWQ0OTZjODExZjA1MDY2ZWFiZWU4NjcyYTUzYjBjIiwid2IiOiIwZWE3MzQ3OTBhMDYzMTc4NjQ4ZTkzMjc2MzliZjBlZSJ9.FG3DQ3uZ6nuKUSjsqtpDcc96hPk7Kt-LXOUjeW2V4a4', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk4NjM3NDIuODIzLCJleHAiOjE3Njk4NjM4NjIuODIzLCJocSI6IjNjZWQ0OTZjODExZjA1MDY2ZWFiZWU4NjcyYTUzYjBjIiwid2IiOiIwZWE3MzQ3OTBhMDYzMTc4NjQ4ZTkzMjc2MzliZjBlZSJ9.6sq0kSgyA52m1yv8fq-wwGB_1GwwpW-kTVb91vHd0bg', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk4NjM4MTAuMjk1LCJleHAiOjE3Njk4NjM5MzAuMjk1LCJocSI6IjNjZWQ0OTZjODExZjA1MDY2ZWFiZWU4NjcyYTUzYjBjIiwid2IiOiIwZWE3MzQ3OTBhMDYzMTc4NjQ4ZTkzMjc2MzliZjBlZSJ9.sSbSr8WzMNtl9iru5ASIB9mFhIdxVKNgU5t73et8Pdk', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk4NjM4ODQuOSwiZXhwIjoxNzY5ODY0MDA0LjksImhxIjoiMzRhMDg3NjNlMjY2Njk2MTFhNjg3YTE5OThlZjUwMjciLCJ3YiI6IjBlYTczNDc5MGEwNjMxNzg2NDhlOTMyNzYzOWJmMGVlIn0.0flXRuh6eNrnRS1tnRwBWP8ohj7GolSadJX9jrNcOp8', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk4NjM5NDAuNTU2LCJleHAiOjE3Njk4NjQwNjAuNTU2LCJocSI6IjM0YTA4NzYzZTI2NjY5NjExYTY4N2ExOTk4ZWY1MDI3Iiwid2IiOiIwZWE3MzQ3OTBhMDYzMTc4NjQ4ZTkzMjc2MzliZjBlZSJ9.Mk6xNxS2BBxQYTB2zNZfnCgtvLqqInRliF5BPluubHY', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk4NjM5NjkuODcsImV4cCI6MTc2OTg2NDA4OS44NywiaHEiOiIzNGEwODc2M2UyNjY2OTYxMWE2ODdhMTk5OGVmNTAyNyIsIndiIjoiMGVhNzM0NzkwYTA2MzE3ODY0OGU5MzI3NjM5YmYwZWUifQ.Ug-mQo4zaUg25iigW-24NEeglQpifLz5768bnMX-wLA', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk4NjQwMDUuODIxLCJleHAiOjE3Njk4NjQxMjUuODIxLCJocSI6IjM0YTA4NzYzZTI2NjY5NjExYTY4N2ExOTk4ZWY1MDI3Iiwid2IiOiIwZWE3MzQ3OTBhMDYzMTc4NjQ4ZTkzMjc2MzliZjBlZSJ9.enfi5-QWBdqpf07zwwQyzLRPzwsjFcZWmahm2QOHTpM']
list_authorizationtoken = ['eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk4NjM0MzgsImV4cCI6MTc2OTg2NDAzOCwiczMiOiJZbHA1V0ZkdWEwMUdMMmc1V1VSek0zQmhNbXBETjFWRFlrWjJRaXRpVjNkQ1JrcDVVM1pKUVVFclZWcFNRVVpyYm5KRksyWmhXakZsYlZJMWRIUmlWM28xTWtOTFkwRnVTVnBxTVUwMU9GUTFaV2d2WVZvclNrNHlhR2xEZVZrM2IwRm1kM2RaVW14cFlrZE1LMUJzUkZaYWVDdFpPVFZPZUVaalZUQjBZM2xLT0dOaWJWQlFaVlF5Um5GNlUzSk1hazR3TmtWd01UVjNkbkpZYVhwWGJEaEhVRGM1VW5aUlpsZHhXVnBhVlVaeFlpOUdhVmRaV1hnemNETXdTakJoVWsxVWFVVldZMUZTZUZKM2VHZEhWWGt6UmtOa1IyRXdPVXR4VjBoV1YzSkxSVE5DZVM5Tk1TdEdWbEJMVVVkSVZqUmlOWFZSWldOUVJuaE1VVm95UkZWcmMwTmFTelZTU1hoMlJWYzFTRlZ4TW1WVVJVbG1NVlJPWjJSU2MwUjJTRGsxVlRNNFdESXplRVZZUzFJNWFVVnNRbXhwVXpodWEybHpMMmwyTlcxRGJFTTRORU52Y0RKRkt6WXZia1pHYWxKdVNXbDFLM0E0WkdwWVFYUkNObnBFY0hSR2JtVm9OSG93UFFvPSIsImRhdGEiOiIyU2ttWXlBUzFkNkh0WU1XVEg5eExFUXlJTFFZRFl1ZG1yeHNHeTFySXlPK1BxTDg2dHBwV3NMdzZRR1hObUxhMnNTTzlNWmJVM1BETzZnU1NBK0ltSjFFN0gyay91aGpqZmZvdEZQQ0RZNDRQOHhrQ1hNTldWV2RVRUdaRXh6djh0S0FkNmVJMk1tdGtGQTJDckRrd1BhbXV6OFQxYmV4MlM3SVZRa1ExT0dJU1FHMU5tRnJ4eW9aYWxsaVBEd0JjWnlyT2h5ckk1ZStBOWpDZm45ZTUwNU5lNlk3ankzYm9ZdTdKb3E4enA4NnErVFJlQitlMjkxeHhoa3FHbnp6Y2lYa0ZJRDk0LzJLSTBzTmJBVXljQ09hSkZoM2pHNjVJQ3dLczFMTFFOMFQ0cUN3T1JMcmI0NCtoRTdWWUJMVjRKVlA2U1JzRGs4S2xqcXhMK2FKbVJ6NkkvblN4ZDhvcWZnRmJFQlFrZ1k9IiwidiI6IjIiLCJzMSI6IjhGSG45TkRIZHFVeDhiL1RvbUFOR2srS09oekY0Z0IwIiwiczIiOiJFdmFtamJqbFgrVm8xZTMrdW9RNkRWeGMrZExnUEd2NCJ9._Kl4_uSvMuaI-nTqlMMnBj6ZIvbkqAj8SXdjDv1zD6M', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk4NjM3MzcsImV4cCI6MTc2OTg2NDMzNywiczMiOiJZbHA1V0ZkdWEwMUdMMmc1V1VSek0zQmhNbXBETjFWRFlrWjJRaXRpVjNkQ1JrcDVVM1pKUVVFclZWcFNRVVpyYm5KRksyWmhXakZsYlZJMWRIUmlWM28xTWtOTFkwRnVTVnBxTVUwMU9GUTFaV2d2WVZvclNrNHlhR2xEZVZrM2IwRm1kM2RaVW14cFlrZE1LMUJzUkZaYWVDdFpPVFZPZUVaalZUQjBZM2xLT0dOaWJWQlFaVlF5Um5GNlUzSk1hazR3TmtWd01UVjNkbkpZYVhwWGJEaEhVRGM1VW5aUlpsZHhXVnBhVlVaeFlpOUdhVmRaV1hnemNETXdTakJoVWsxVWFVVldZMUZTZUZKM2VHZEhWWGt6UmtOa1IyRXdPVXR4VjBoV1YzSkxSVE5DZVM5Tk1TdEdWbEJMVVVkSVZqUmlOWFZSWldOUVJuaE1VVm95UkZWcmMwTmFTelZTU1hoMlJWYzFTRlZ4TW1WVVJVbG1NVlJPWjJSU2MwUjJTRGsxVlRNNFdESXplRVZZUzFJNWFVVnNRbXhwVXpodWEybHpMMmwyTlcxRGJFTTRORU52Y0RKRkt6WXZia1pHYWxKdVNXbDFLM0E0WkdwWVFYUkNObnBFY0hSR2JtVm9OSG93UFFvPSIsImRhdGEiOiI3MHJRc25vSEF1Y3NSOXJvMHVvNUxHQ3V1WlhaWUwraVNGcE1VYVh1RXpCRFlZenIxWGFXV0Y5V0FVRm1waEJ5ZCsyTjZNUzdReGZFS1RQS2plelhQeDNSYUYxZHB5T0FIR0pPbVdHYTkzckZvRG9DQ0MvYXFyeXp0dkd2YS92TktEWFBlWUFTVWR4RGFuWU41b0dnRG1JRjY0cXMzZE5vbHpZZ01OenRzM1ZySDFqRlltRXd2ekxWUStpcU5vOHBMTzY2MUxrNXBoc0JzVlV3TGk3Q2x2VnBobnVjLzFaMmhueDhNdzRmUVltbUhRclI2VUNuWC9waXNhVFdoTjR6ZGlDdXlCNkx6YXh3L2VRMHM0bE1FVUtZQVU4Mk82bDdJVUdYT3dhbjRZOWtmZ29QS2QzR2kxOTlZTUVFeXdyUm05SC9QZGxZR3dhVVFpNFZLakhIREhNVFF1dEJJZ3NBbi8zZUVjdEhpN289IiwidiI6IjIiLCJzMSI6IjhGSG45TkRIZHFVeDhiL1RvbUFOR2srS09oekY0Z0IwIiwiczIiOiJFdmFtamJqbFgrVm8xZTMrdW9RNkRWeGMrZExnUEd2NCJ9.pg8GAT81aag1PeaN1mCSNy5jSB16txUhkJp-ijQxGtM', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk4NjM4MDcsImV4cCI6MTc2OTg2NDQwNywiczMiOiJZbHA1V0ZkdWEwMUdMMmc1V1VSek0zQmhNbXBETjFWRFlrWjJRaXRpVjNkQ1JrcDVVM1pKUVVFclZWcFNRVVpyYm5KRksyWmhXakZsYlZJMWRIUmlWM28xTWtOTFkwRnVTVnBxTVUwMU9GUTFaV2d2WVZvclNrNHlhR2xEZVZrM2IwRm1kM2RaVW14cFlrZE1LMUJzUkZaYWVDdFpPVFZPZUVaalZUQjBZM2xLT0dOaWJWQlFaVlF5Um5GNlUzSk1hazR3TmtWd01UVjNkbkpZYVhwWGJEaEhVRGM1VW5aUlpsZHhXVnBhVlVaeFlpOUdhVmRaV1hnemNETXdTakJoVWsxVWFVVldZMUZTZUZKM2VHZEhWWGt6UmtOa1IyRXdPVXR4VjBoV1YzSkxSVE5DZVM5Tk1TdEdWbEJMVVVkSVZqUmlOWFZSWldOUVJuaE1VVm95UkZWcmMwTmFTelZTU1hoMlJWYzFTRlZ4TW1WVVJVbG1NVlJPWjJSU2MwUjJTRGsxVlRNNFdESXplRVZZUzFJNWFVVnNRbXhwVXpodWEybHpMMmwyTlcxRGJFTTRORU52Y0RKRkt6WXZia1pHYWxKdVNXbDFLM0E0WkdwWVFYUkNObnBFY0hSR2JtVm9OSG93UFFvPSIsImRhdGEiOiJ1Q2pxSkRlck9FWjhDT0hFOEJYZFBEM2F0VEx2MGQ5eWQ0eHFoWjN2OVdXdEM1OGxjRzhGWFNsWnMxc3AyOUNlMHJHcFc3RW56VXQ0OVNBSVRjNFJYN25YWVo0dWxwUW8vV2FiUnhINEZrd2tDMXhXaTNXVVZ4azBTdzlRZk9aNGhTTEZkVlcyQmpEMzlpY2lRL3NuMGtRY1ROM2IvYThVQnZCZ2N4VWsvcXMzZEZ0bmdzQ1QwY2phVWMrOEpFTCtTRFdEdlVmQ2s2VndMaG9rWitpeE0rZ3N2S2k5dUZzR2NpdjgxVGhPWGMxSXFRSzk5Y1JtQVl1UG5jWldhNU1CSEJxL1FjN3ozWXhGb1lHNU9zYUJMSHRMaUEyN2lQazIya0tKNHFmOGpPZjhOcExhUFcwMkZyUnFnY1VzZHk5aEJ6akZaaFF6cWZ5Rk9SaFo4MWJZMnFyd20wakx3djlhb244bjVVU0JnLzg9IiwidiI6IjIiLCJzMSI6IjhGSG45TkRIZHFVeDhiL1RvbUFOR2srS09oekY0Z0IwIiwiczIiOiJFdmFtamJqbFgrVm8xZTMrdW9RNkRWeGMrZExnUEd2NCJ9.3fBOHzToHxplco6qX8hwCJjoyQNK2eXNN9Zo5sPa0YI', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk4NjM4ODEsImV4cCI6MTc2OTg2NDQ4MSwiczMiOiJZbHA1V0ZkdWEwMUdMMmc1V1VSek0zQmhNbXBETjFWRFlrWjJRaXRpVjNkQ1JrcDVVM1pKUVVFclZWcFNRVVpyYm5KRksyWmhXakZsYlZJMWRIUmlWM28xTWtOTFkwRnVTVnBxTVUwMU9GUTFaV2d2WVZvclNrNHlhR2xEZVZrM2IwRm1kM2RaVW14cFlrZE1LMUJzUkZaYWVDdFpPVFZPZUVaalZUQjBZM2xLT0dOaWJWQlFaVlF5Um5GNlUzSk1hazR3TmtWd01UVjNkbkpZYVhwWGJEaEhVRGM1VW5aUlpsZHhXVnBhVlVaeFlpOUdhVmRaV1hnemNETXdTakJoVWsxVWFVVldZMUZTZUZKM2VHZEhWWGt6UmtOa1IyRXdPVXR4VjBoV1YzSkxSVE5DZVM5Tk1TdEdWbEJMVVVkSVZqUmlOWFZSWldOUVJuaE1VVm95UkZWcmMwTmFTelZTU1hoMlJWYzFTRlZ4TW1WVVJVbG1NVlJPWjJSU2MwUjJTRGsxVlRNNFdESXplRVZZUzFJNWFVVnNRbXhwVXpodWEybHpMMmwyTlcxRGJFTTRORU52Y0RKRkt6WXZia1pHYWxKdVNXbDFLM0E0WkdwWVFYUkNObnBFY0hSR2JtVm9OSG93UFFvPSIsImRhdGEiOiJsVmhLU3hObDMvMkV6cFV1S2FsNnRyb3dGeFlrRWYwS0ZLanR3WGhBRU9RbTJocVZUTnNIZHNJTFVqUmVPbm42UlVicFFxdE9qZTVORithMit5NEtZZk5UOTBBY0lBKzlnVG4vbjlzVHQ0emxLTi9sKzVTaXJYaHI0cTVBSStmUS9SVm1KMGlBNktNWVQ5WFR4UXhDQ3psczhsRUh5b1BMRUh3WUhjUVlxb0o4TkplSTdodGRnbDRnR01VeVdFU3hXN3g0WXpnc3JCUks0K0IwdFAwZDVjRzZEdXBoTFlHQW12c1FvbVFsRmQyUzFRZ1FTSmRkc0pua0hPcmlRdWErcC9yR2tPWWxxak1zUXVEYjljdllrUjRGSXpOdUFhQ0lWSTJKNUFwWjJoUnZSVTBwc2UxQkowMjh5VVd4R2hUZi9sZVNoZFdsNUpQeVdkTXNBdnIxRlhUSGJDQlhINzBZd1hBUFB2MGwyQ2s9IiwidiI6IjIiLCJzMSI6IjhGSG45TkRIZHFVeDhiL1RvbUFOR2srS09oekY0Z0IwIiwiczIiOiJFdmFtamJqbFgrVm8xZTMrdW9RNkRWeGMrZExnUEd2NCJ9.0p4lSNPqmEp7GAkCX378jp8Vyn_RVxii42p2hfOdsXc', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk4NjM5MzQsImV4cCI6MTc2OTg2NDUzNCwiczMiOiJZbHA1V0ZkdWEwMUdMMmc1V1VSek0zQmhNbXBETjFWRFlrWjJRaXRpVjNkQ1JrcDVVM1pKUVVFclZWcFNRVVpyYm5KRksyWmhXakZsYlZJMWRIUmlWM28xTWtOTFkwRnVTVnBxTVUwMU9GUTFaV2d2WVZvclNrNHlhR2xEZVZrM2IwRm1kM2RaVW14cFlrZE1LMUJzUkZaYWVDdFpPVFZPZUVaalZUQjBZM2xLT0dOaWJWQlFaVlF5Um5GNlUzSk1hazR3TmtWd01UVjNkbkpZYVhwWGJEaEhVRGM1VW5aUlpsZHhXVnBhVlVaeFlpOUdhVmRaV1hnemNETXdTakJoVWsxVWFVVldZMUZTZUZKM2VHZEhWWGt6UmtOa1IyRXdPVXR4VjBoV1YzSkxSVE5DZVM5Tk1TdEdWbEJMVVVkSVZqUmlOWFZSWldOUVJuaE1VVm95UkZWcmMwTmFTelZTU1hoMlJWYzFTRlZ4TW1WVVJVbG1NVlJPWjJSU2MwUjJTRGsxVlRNNFdESXplRVZZUzFJNWFVVnNRbXhwVXpodWEybHpMMmwyTlcxRGJFTTRORU52Y0RKRkt6WXZia1pHYWxKdVNXbDFLM0E0WkdwWVFYUkNObnBFY0hSR2JtVm9OSG93UFFvPSIsImRhdGEiOiJnV3ZtdHFzTDl4blBYRGpQMTlmZitDYkUrUFBTb1dtZDFUOEVUT3JZTmpIV0h5ZUh2dENYNlpiWTlEdXRzR05FTExTelNScmQ4b1JoR3hzWUNTNzI1NDB1VVNxL0dzdlNzaEhCOUhMNzRlb0pxZFBqUG85NWNHRm5nek41aDRwY2xjTkxPWE4vY3Rac2dEV0duOTNzU1Z2cEZyN05XWUxJd2tKSzBjcHdPWEdkVndYMGU4RHFMcGNCbzhEL1FsRitwa1ljUTYyWEZYMURSVnp3Y2NtWEE4NVVIMHBCVEE2T2VKRVlNaFB1Sm1TZHhxSDAxa2d5V3BiOWU5SXBYZWFpcFRhWS9LZ0w0ZTRaRndlZHBzbmVJV0ZmdUoxY1ltN2xQNVIrOFJsYVhUNmw1eTcwTDdQbkczUUFkeVNWaXdaSkhoVDhhbjZBaU9OZ2tSdlZ6Y2JHRzl1dkNWbHFjc3V0K1ZnOHdFWllQbHc9IiwidiI6IjIiLCJzMSI6IjhGSG45TkRIZHFVeDhiL1RvbUFOR2srS09oekY0Z0IwIiwiczIiOiJFdmFtamJqbFgrVm8xZTMrdW9RNkRWeGMrZExnUEd2NCJ9.puJbcgQ0QFzBLqbcq56XwyylyNzpMCgB34try0aHakA', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk4NjM5NjcsImV4cCI6MTc2OTg2NDU2NywiczMiOiJZbHA1V0ZkdWEwMUdMMmc1V1VSek0zQmhNbXBETjFWRFlrWjJRaXRpVjNkQ1JrcDVVM1pKUVVFclZWcFNRVVpyYm5KRksyWmhXakZsYlZJMWRIUmlWM28xTWtOTFkwRnVTVnBxTVUwMU9GUTFaV2d2WVZvclNrNHlhR2xEZVZrM2IwRm1kM2RaVW14cFlrZE1LMUJzUkZaYWVDdFpPVFZPZUVaalZUQjBZM2xLT0dOaWJWQlFaVlF5Um5GNlUzSk1hazR3TmtWd01UVjNkbkpZYVhwWGJEaEhVRGM1VW5aUlpsZHhXVnBhVlVaeFlpOUdhVmRaV1hnemNETXdTakJoVWsxVWFVVldZMUZTZUZKM2VHZEhWWGt6UmtOa1IyRXdPVXR4VjBoV1YzSkxSVE5DZVM5Tk1TdEdWbEJMVVVkSVZqUmlOWFZSWldOUVJuaE1VVm95UkZWcmMwTmFTelZTU1hoMlJWYzFTRlZ4TW1WVVJVbG1NVlJPWjJSU2MwUjJTRGsxVlRNNFdESXplRVZZUzFJNWFVVnNRbXhwVXpodWEybHpMMmwyTlcxRGJFTTRORU52Y0RKRkt6WXZia1pHYWxKdVNXbDFLM0E0WkdwWVFYUkNObnBFY0hSR2JtVm9OSG93UFFvPSIsImRhdGEiOiJ2K1Vxb0U4Y21IZ2RrNXFOSnlpNmsza1RjZVV6aWdLL0gyTnJlaEV2S0I2RW1ucC9Pa0Fhdnd1aG45aW53SXpsbzRVZWU5UDE5N05CTkFNcjlCWHlQV3FndEg5dlRSQ3d6L0lUQnRYYy9tZ2hhWjBVaTF6MEI1aThhUVZCaGVFRzlwa3lhNW9LMVZtTHFEMldzK1hQSnVrd0tBZ21xaFRkSjNTS29XcXBRdHVtenZ3Q3FJSGFrakdqcExtckpVdjNVNzBwZDNVa0M5MHNyK3o3YjR4M0tmVG1qdUJHOHFDdko3dUlCWVplTmVoVjhBNkp2VlV0dnVYTXBwL0tyMzk4K1pLOCswbGpab294OXdVYVkrUW8zZ2NqU0hhNHVGZVVMdithamZ2QXAzRDFhZkZIYWpRZytvYzgvT3FGanlFOVFQWVFMWUVnMk9aU0U4NXJjWUdjSXRhSWRYbEpiYk9pNmErQWZqcXM0c0E9IiwidiI6IjIiLCJzMSI6IjhGSG45TkRIZHFVeDhiL1RvbUFOR2srS09oekY0Z0IwIiwiczIiOiJFdmFtamJqbFgrVm8xZTMrdW9RNkRWeGMrZExnUEd2NCJ9.HGode5QU0pJAZw2zgb9wpu25Uw7xYc-VIO-8cciQoTc', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk4NjQwMDIsImV4cCI6MTc2OTg2NDYwMiwiczMiOiJZbHA1V0ZkdWEwMUdMMmc1V1VSek0zQmhNbXBETjFWRFlrWjJRaXRpVjNkQ1JrcDVVM1pKUVVFclZWcFNRVVpyYm5KRksyWmhXakZsYlZJMWRIUmlWM28xTWtOTFkwRnVTVnBxTVUwMU9GUTFaV2d2WVZvclNrNHlhR2xEZVZrM2IwRm1kM2RaVW14cFlrZE1LMUJzUkZaYWVDdFpPVFZPZUVaalZUQjBZM2xLT0dOaWJWQlFaVlF5Um5GNlUzSk1hazR3TmtWd01UVjNkbkpZYVhwWGJEaEhVRGM1VW5aUlpsZHhXVnBhVlVaeFlpOUdhVmRaV1hnemNETXdTakJoVWsxVWFVVldZMUZTZUZKM2VHZEhWWGt6UmtOa1IyRXdPVXR4VjBoV1YzSkxSVE5DZVM5Tk1TdEdWbEJMVVVkSVZqUmlOWFZSWldOUVJuaE1VVm95UkZWcmMwTmFTelZTU1hoMlJWYzFTRlZ4TW1WVVJVbG1NVlJPWjJSU2MwUjJTRGsxVlRNNFdESXplRVZZUzFJNWFVVnNRbXhwVXpodWEybHpMMmwyTlcxRGJFTTRORU52Y0RKRkt6WXZia1pHYWxKdVNXbDFLM0E0WkdwWVFYUkNObnBFY0hSR2JtVm9OSG93UFFvPSIsImRhdGEiOiJKRGVtNEM4eldMZm1pV2crWmRtbWdBREF3S2JvVnp2Z05pRkdlTnRDNWpETTVWNTlRQXV6dG1FelpBUjFQZFhmaCtZOVp4VDE5K0o4THVlQU16RmcyYlB0WEtEVG9lZ0wxeGYvYkQ3ZHBCblMwUXVCWHNaeWt0K0lEaUJ1MnhScDdUSE9VVWJ4c3BJNFhRWUt4c3FyUERtRXlhbVRSNTk0aklrMVJkcnAzbDduY3d5dFNLeDZRaWZMRjF0SFpodlFRbUNzVjBKZ1VTb2Rmdk9vYzV4TUdvTnZUMVRvWE1nRDFkUDd2MXo0V3h1dnpPSGJlU3VnREpEN1VVZWI5dEd0a2JVZkdBU3B6SFJvSVBzdnBGclRSaHZaY3VmbENUeTNOdWEvQkg1eTJTbHVGTWpCRzBPV0FqVVUreGZuUHZJeFFOdnZUWndFZmI2azYrU25MMzlJWXRJRGVxazQxTzJyZlZPSE5qRWwrLzg9IiwidiI6IjIiLCJzMSI6IjhGSG45TkRIZHFVeDhiL1RvbUFOR2srS09oekY0Z0IwIiwiczIiOiJFdmFtamJqbFgrVm8xZTMrdW9RNkRWeGMrZExnUEd2NCJ9.C3hI3Ne_9hqYJXpjiuq1Z6_3bbZNlMe3hcaKO8zz_EA']

#----------------------------------------------- LOGGING SETUP ------------------------------------------------#
# Common formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s",
                              datefmt="%Y-%m-%d %H:%M:%S")

# Clear any existing log handlers
logging.getLogger().handlers = []
logging.getLogger().setLevel(logging.INFO)  # Keep this if you still want other handlers to capture DEBUG

# =========================
# PART 1 — FILE + CONSOLE
# =========================
# Create a logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# File handler (INFO and above only)
# Get current date in DD_MM_YYYY format
current_date = datetime.now().strftime("%d_%m_%Y")

# Create log file name dynamically
log_filename = f"logs/logs_{current_date}.log"

# Setup file handler
file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Console handler (DEBUG and above)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Add handlers
logging.getLogger().addHandler(file_handler)
logging.getLogger().addHandler(console_handler)


# # =========================
# # PART 2 — CONSOLE ONLY
# # =========================

# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.DEBUG)  # Or INFO if you want less output
# console_handler.setFormatter(formatter)

# logging.getLogger().addHandler(console_handler)

## ---------------------------------------- HELPER FUNCTIONS ------------------------------------------------##
# Function to generate a random user agent
def get_random_user_agent():
    """
    Generates a random user agent string using the fake_useragent library.
    """
    ua = UserAgent()
    return ua.random

def get_random_apitoken(apitoken_list = list_apitoken):
    """
    Selects a random API token from the provided list.
    """
    return choice(apitoken_list)

def get_random_authorizationtoken(authorizationtoken_list = list_authorizationtoken):
    """
    Selects a random authorization token from the provided list.
    """
    return choice(authorizationtoken_list)

# Function to sleep for a random interval
def random_sleep(min_seconds: float, max_seconds: float):
    """
    Suspends execution for a random interval between min and max range.
    """
    sleep_time = uniform(min_seconds, max_seconds)
    print(f"Sleeping for {sleep_time:.2f} seconds...")
    time.sleep(sleep_time)



# Global counter & lock
request_counter = 0
counter_lock = Lock()

## ------------------------------------------- CSV READING FUNCTION ----------------------------------------------##
# Reads listing IDs from a CSV file
def read_listing_ids_from_csv(csv_path, column_name="listing_id"):
    """
    Reads listing_id column from a CSV file and returns it as a list.
    """
    listing_ids = []

    try:
        with open(csv_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            if column_name not in reader.fieldnames:
                raise ValueError(f"Column '{column_name}' not found in CSV")

            for row in reader:
                value = row.get(column_name)
                if value:
                    listing_ids.append(value.strip())

        logging.info(f"Successfully read {len(listing_ids)} listing IDs")

    except FileNotFoundError:
        logging.error(f"CSV file not found: {csv_path}")

    except ValueError as ve:
        logging.error(str(ve))

    except Exception as e:
        logging.exception(f"Unexpected error while reading CSV: {e}")

    return listing_ids

# Reads existing project IDs from output CSV to avoid duplicates
def read_outpurt_file_existing_data(csv_path, column_name="project_id"):
    """
    Reads project_id column from CSV, converts it to a unique list, and returns it.
    """
    project_ids = set()

    try:
        with open(csv_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            if column_name not in reader.fieldnames:
                raise ValueError(f"Column '{column_name}' not found in CSV")

            for row in reader:
                value = row.get(column_name)
                if value:
                    project_ids.add(value.strip())

        logging.info(f"Loaded {len(project_ids)} unique project IDs")

    except FileNotFoundError:
        logging.error(f"CSV file not found: {csv_path}")

    except ValueError as ve:
        logging.error(str(ve))

    except Exception as e:
        logging.exception(f"Unexpected error while reading CSV: {e}")

    return list(project_ids)


def project_details_API(project_id):

    url = f"https://www.99acres.com/api-aggregator/v2/project-details?projectIds=PROJECT_{project_id}_R&page=PROJECT_DETAIL_PAGE&platform=DESKTOP&stage=SCROLL_CLICK&crawlableComponents=SEARCH_RESALE_PROPERTIES,SEARCH_RENTAL_PROPERTIES,SEARCH_BUILDER_PROJECTS,COLLABORATIVE_PROJECTS,SIMILAR_PROJECTS,RATINGS_AND_REVIEWS"

    user_agent = get_random_user_agent()
    new_apitoken = get_random_apitoken()
    new_authorizationtoken = get_random_authorizationtoken()
    payload = {}
    headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,es;q=0.8',
    'apitoken': new_apitoken,
    'authorizationtoken': new_authorizationtoken,
    'dnt': '1',
    'pagename': 'XID',
    'platform': 'desktop',
    'priority': 'u=1, i',
    'referer': f'https://www.99acres.com/property-r{project_id}',
    'user-agent': user_agent
    }

    # Use a session for better performance and retry logic
    session = requests.Session()
    
    try:
        # Added verify=False if you are getting SSL/Proxy errors
        # Added timeout to prevent the script from hanging indefinitely
        response = session.get(url, headers=headers, timeout=15, verify=False)
        
        if response.status_code != 200:
            for i in range(5):
                logging.warning(f"Retry {i+1} for Project {project_id} (Status: {response.status_code})")
                random_sleep(1, 3)
                response = session.get(url, headers=headers, timeout=15, verify=False)
                if response.status_code == 200:
                    break
        
        return response.text if response.status_code == 200 else None

    except requests.exceptions.SSLError:
        logging.error("SSL Error: Try setting verify=False in the get() request.")
    except Exception as e:
        logging.error(f"Error fetching project details: {e}")
    return None

def extract_99acres_project_data_safe(response_text: str) -> dict:
    try:
        data = json.loads(response_text)
    except Exception:
        return {}

    projects = data.get("projects") or []
    if not projects:
        return {}

    project = projects[0] or {}

    basic = project.get("basicDetails") or {}
    location = basic.get("location") or {}
    components = project.get("components") or {}
    floor_plans = (
        components
        .get("floorPlans", {})
        .get("configurations", {})
        .get("tuples") or []
    )

    # ---------------- Project level ----------------
    result = {
        "project_id": basic.get("projectId"),
        "project_name": basic.get("name"),
        "project_type": "Residential",
        "launch_status": (
            project.get("commonElements", {})
                   .get("benefits", {})
                   .get("heading")
        ),
        "city": location.get("cityName"),
        "locality": location.get("localityName"),
        "state": location.get("stateName"),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "address": basic.get("streetAddress"),
        "postal_code": basic.get("postalCode"),
        "price_min": basic.get("price", {}).get("min"),
        "price_max": basic.get("price", {}).get("max"),
        "price_label": basic.get("price", {}).get("label"),
        "site_plan_url": components.get("floorPlans", {}).get("sitePlanURL"),
        "highlights": [
            h.get("text")
            for h in (basic.get("keyHighlights") or [])
            if h.get("text")
        ],
        "government_charges": [
            {
                "title": g.get("title"),
                "points": g.get("points") or []
            }
            for g in (project.get("govtCharges", {}).get("tuples") or [])
        ],
        "has_rera_disclaimer": bool(
            project.get("commonElements", {}).get("reraDefaultInfo")
        ),
        "available_bhk_types": sorted({
            cfg.get("bedroom")
            for cfg in floor_plans
            if cfg.get("bedroom") is not None
        }),
        "units": []
    }

    # ---------------- Unit level ----------------
    for cfg in floor_plans:
        if not isinstance(cfg, dict):
            continue

        bhk = cfg.get("bedroom")
        prop_type = cfg.get("propertyTypeLabel")

        for group in (cfg.get("groups") or []):
            for unit in (group.get("tuples") or []):

                area = unit.get("area") or {}
                price = unit.get("price") or {}
                construction = unit.get("constructionStatusCard") or {}

                images = unit.get("images") or {}
                images_2d = images.get("2D") or []
                images_3d = images.get("3D") or []

                sellers = [
                    {
                        "name": s.get("name"),
                        "company": s.get("companyName"),
                        "type": s.get("label")
                    }
                    for s in (unit.get("sellers", {}).get("tuples") or [])
                ]

                result["units"].append({
                    "bhk": bhk,
                    "property_type": prop_type,
                    "area_sqft": area.get("min"),
                    "area_type": area.get("type", {}).get("label"),
                    "price": price.get("min"),
                    "price_authentic": price.get("authentic"),
                    "possession": construction.get("subLabel"),
                    "possession_raw": construction.get("dateLabel"),
                    "floorplan_2d_url": (
                        images_2d[0].get("variants", {}).get("ORIGINAL")
                        if images_2d else None
                    ),
                    "floorplan_3d_url": (
                        images_3d[0].get("variants", {}).get("LARGE")
                        if images_3d else None
                    ),
                    "sellers": sellers
                })

    return result

def save_99acres_data_to_csv(project_data: dict, csv_path: str):
    if not project_data or "units" not in project_data:
        return

    file_exists = os.path.isfile(csv_path)

    fieldnames = [
        "project_id", "project_name", "project_type", "launch_status",
        "city", "locality", "state", "latitude", "longitude",
        "address", "postal_code",
        "price_min", "price_max", "price_label",
        "site_plan_url", "has_rera_disclaimer",
        "available_bhk_types", "highlights", "government_charges",
        "bhk", "property_type", "area_sqft", "area_type",
        "price", "price_authentic",
        "possession", "possession_raw",
        "floorplan_2d_url", "floorplan_3d_url",
        "sellers"
    ]

    with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for unit in project_data.get("units", []):
            row = {
                "project_id": project_data.get("project_id"),
                "project_name": project_data.get("project_name"),
                "project_type": project_data.get("project_type"),
                "launch_status": project_data.get("launch_status"),
                "city": project_data.get("city"),
                "locality": project_data.get("locality"),
                "state": project_data.get("state"),
                "latitude": project_data.get("latitude"),
                "longitude": project_data.get("longitude"),
                "address": project_data.get("address"),
                "postal_code": project_data.get("postal_code"),
                "price_min": project_data.get("price_min"),
                "price_max": project_data.get("price_max"),
                "price_label": project_data.get("price_label"),
                "site_plan_url": project_data.get("site_plan_url"),
                "has_rera_disclaimer": project_data.get("has_rera_disclaimer"),
                "available_bhk_types": ",".join(
                    map(str, project_data.get("available_bhk_types", []))
                ),
                "highlights": " | ".join(project_data.get("highlights", [])),
                "government_charges": " | ".join(
                    f"{g.get('title')}: {', '.join(g.get('points', []))}"
                    for g in project_data.get("government_charges", [])
                ),
                "bhk": unit.get("bhk"),
                "property_type": unit.get("property_type"),
                "area_sqft": unit.get("area_sqft"),
                "area_type": unit.get("area_type"),
                "price": unit.get("price"),
                "price_authentic": unit.get("price_authentic"),
                "possession": unit.get("possession"),
                "possession_raw": unit.get("possession_raw"),
                "floorplan_2d_url": unit.get("floorplan_2d_url"),
                "floorplan_3d_url": unit.get("floorplan_3d_url"),
                "sellers": " | ".join(
                    f"{s.get('name')} ({s.get('type')})"
                    for s in unit.get("sellers", [])
                )
            }

            writer.writerow(row)

def process_single_project(project_id):
    """Function for a single thread to execute"""
    try:
        logging.info(f"Fetching details for project ID: {project_id}")
        
        response = project_details_API(project_id)
        if not response:
            return

        project_data = extract_99acres_project_data_safe(response)
        
        if project_data:
            # Use the lock to ensure thread-safe writing
            with csv_lock:
                save_99acres_data_to_csv(project_data, "99acres_projects.csv")
        
        # Small sleep to avoid overwhelming the API
        random_sleep(2, 4)
        
    except Exception as e:
        logging.error(f"Error in thread for ID {project_id}: {e}")

# ---------------------------------------- MULTITHREADING SETUP ------------------------------------------------##
def wrapped_process(project_id):
    global request_counter

    process_single_project(project_id)

    with counter_lock:
        request_counter += 1

        # Pause after every 30 requests
        if request_counter % 30 == 0:
            sleep_time = random.randint(60, 120)  # 1–2 minutes
            logging.info(
                f"Processed {request_counter} projects. "
                f"Sleeping for {sleep_time}s to respect rate limits."
            )
            time.sleep(sleep_time)
            
def multithreading_process(new_listing_ids):
    max_workers = 3
    logging.info(
        f"Starting multithreaded extraction for {len(new_listing_ids)} projects "
        f"with {max_workers} workers (30/min rate limit)..."
    )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(wrapped_process, pid)
            for pid in new_listing_ids
        ]

        for future in as_completed(futures):
            future.result()  # surface exceptions

    logging.info("Multithreaded processing complete.")


def main():
    csv_path_listing = "all_listings.csv"
    csv_path_output = "99acres_projects.csv"

    listing_ids = read_listing_ids_from_csv(csv_path_listing)
    logging.info(f"Total Listing IDs: {len(listing_ids)}")

    existing_project_ids = read_outpurt_file_existing_data(csv_path_output)
    logging.info(f"Existing Project IDs: {len(existing_project_ids)}")

    # Keep only new listing IDs
    existing_set = set(existing_project_ids)
    new_listing_ids = [lid for lid in listing_ids if lid not in existing_set]

    logging.info(f"New Listing IDs to process: {len(new_listing_ids)}")

    if not new_listing_ids:
        logging.info("No new listing IDs to process.")
        return

    logging.info(f"Received {len(new_listing_ids)} new listing IDs")

    multithreading_process(new_listing_ids)

    logging.info("Main execution finished.")

if __name__ == "__main__":
    main()