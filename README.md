## checking cf manifest.yml
Reads manifest.yml and checking:
- if service instances exists in the current target space
- if routes are available by checking [check-reserved-routes-for-a-domain cf api](https://v3-apidocs.cloudfoundry.org/version/3.197.0/index.html#check-reserved-routes-for-a-domain)

it exits with 0 if all good. exit 1 otherwise.

## prerequisites
- python3
- pip3 install pyyaml

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

Checking Routes availability from the manifest (./manifest-good.yml)
  Fetching cf domains from the target foundation ...
  All routes from the manifest available

Checking Service instance from the manifest (./manifest-good.yml)
  Current service instances in this space '['my-cups', 'my-cups2', 'my-cups 3']'
  All service instance from the manifest exists in current space
  
$ echo $?
0
```

bad case.
```
$ python3 check-manifest.py ./manifest-bad.yml

API endpoint:   https://api.sys.dhaka.cf-app.com
API version:    3.194.0
user:           minseok.kim@broadcom.com
org:            minseok
space:          test

Checking Routes availability from the manifest (./manifest-bad.yml)
  Fetching cf domains from the target foundation ...
  Found Routes Not Available:
  -   Route is reserved ('cryodocs.apps.dhaka.cf-app.com' under application 'spring-music')
  -   No such domain 'internal' in cf domains ('apps.internal' under application 'spring-music')
  -   Invalid route. too short 'internal' ('internal' under application 'spring-music')

Checking Service instance from the manifest (./manifest-bad.yml)
  Current service instances in this space '['my-cups', 'my-cups2', 'my-cups 3']'
  Found Missing service instance:
  -   Missing 'service-not-exist1' under application 'spring-music'
  -   Missing 'service-not-exist2' under application 'spring-music'
  -   Missing '2service-not-exist1' under application 'spring-music2'
  -   Missing '2service-not-exist2' under application 'spring-music2'

$ echo $?
1
```