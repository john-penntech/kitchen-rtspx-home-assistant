# Security policy

## Supported version

Version 1.1.x is supported. Version 1.0.0 is retained only as the captured YAML
baseline. Security fixes are made on the default branch and released with a new
version and documented upgrade path.

## Reporting

Report suspected vulnerabilities privately to the repository owner through
GitHub's private vulnerability reporting feature. Do not include camera URLs,
credentials, Home Assistant backups, recordings, or full logs in a public
issue.

## Trust boundary

This component returns the configured stream string to Home Assistant's native
camera/go2rtc provider. It does not implement network transport, authentication,
or authorization. Protect stream URLs are credentials. Version 1.1.x stores
them in Home Assistant config-entry data, masks them in the setup UI, and redacts
them from diagnostics. The Home Assistant instance and camera network must not
be exposed merely because this source repository is public.
