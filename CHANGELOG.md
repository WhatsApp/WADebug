### 0.1.5 (January 15, 2020)
* Deprecate python 2 support 🎉
* `wadebug logs` now gets past 3 hours logs, instead of last 10K lines of logs
* Add `--since` option to `wadebug logs` that retrieves 3 hours of logs starting from the date time value specified
* [Bug Fix] Fail fast in json mode when incompatible params are used

### 0.1.4 (September 3, 2019)

* A new and cleaner UI for WADebug
* [Bug Fix] Fix wrong port printed when there's an error connecting in check_network action
* [Bug Fix] Add missing MySQL privilege requirements in check_mysql_permissions action

### 0.1.3 (April 26, 2019)

* Add new configuration file items required by new actions
* Add webhook health checks
* Add WADebug upgrade prompt when a new version is available on PyPi
* Add support endpoint response to uploaded logs for easier troubleshooting
* WADebug crash logs are now uploaded to to Facebook

### 0.1.2 (Dec 28, 2018)

* Limit the size of logs retrieved
* Capture coreapp coredumps in case of crashes
* Add new command to retrieve logs without upload
* Add enum34 as a required module for < Python 3.4

### 0.1.1 (Oct 23, 2018)

* Initial release
