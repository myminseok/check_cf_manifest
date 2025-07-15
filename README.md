## checking cf manifest.yml
Reads manifest.yml and checking:
- if service instances exists in the current target space
- if routes are available by checking http response code 200

it exits with 0 if all good. non 0 otherwise.

## prerequisites
- python3
- pip3 install pyyaml
- pip3 install requests
## How to run

log in to the target foundation.
```
cf login
```

verify manifest.yml
```
$ python3 check-manifest.py ./manifest-good.yml

API endpoint:   https://api.sys.dhaka.cf-app.com
API version:    3.194.0
user:           minseok.kim@broadcom.com
org:            minseok
space:          test
Checking Service instance from the manifest: ./manifest-good.yml
  Current service instances in this space:['my-cups', 'my-cups2', 'my-cups 3']
  All service instance from the manifest exists in current space
Checking Routes from the manifest: ./manifest-good.yml
  All routes from the manifest MAYBE available
```

bad case.
```
$ python3 check-manifest.py ./manifest-bad.yml

API endpoint:   https://api.sys.dhaka.cf-app.com
API version:    3.194.0
user:           minseok.kim@broadcom.com
org:            minseok
space:          test
Checking Service instance from the manifest: ./manifest-bad.yml
  Current service instances in this space:['my-cups', 'my-cups2', 'my-cups 3']
  Found Missing service instance:
  -   Missing 'service-not-exist1' under application 'spring-music-cds'
  -   Missing 'service-not-exist2' under application 'spring-music-cds'
  -   Missing '2service-not-exist1' under application 'spring-music-cds2'
  -   Missing '2service-not-exist2' under application 'spring-music-cds2'
Checking Routes from the manifest: ./manifest-bad.yml
  Found Routes that might be used already:
  -  Route 'apps.sys.dhaka.cf-app.com' under application 'spring-music-cds' responding with http-code 200
```