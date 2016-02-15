# pmcparser
A parser for organizing payment receipts from www.pagomiscuentas.com.ar

I've grown tired of having all my digital payment receipts lying around, so I made this to parse each pdf, get some metadata and place them, sorted, in a specific directory.

When run for the first time, pmcparser will create ~/.config/pmcparser.ini, with something like:

~~~
[DEFAULT]
# where to scan for the original pdf files.
path = /home/<user>/Downloads

# the path where to save processed pdf files.
save_path = /home/<user>/payments

# the template to use when creating the directory in save_path.
# valid keywords are provider, year, month and day
default_tmpl = year/provider
~~~

You can change it to your liking, or create a similar one in the same place.

## TODO

- Add an option to just create the config file and exit.
- Consider moving to a plugin architecture to be able to handle different payment receipts. Basically anything that is a PDF and is able to be parsed by PyPDF2 should work.
