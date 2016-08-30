# class

This is a tool for interacting with Banner, the registration system used by
[Memorial University](http://www.mun.ca).
It suffers so that you don't have to.


## Installation

The simplest way to use `class` is to run it directly from a source checkout.
After installing a few Python dependencies:

```sh
$ pip install humanize inflect mechanicalsoup
```

clone this repository and test that you can run the `class` command:

```sh
$ ./class --help
```


## Usage

The command-line `class` tool uses a subcommand style of interaction:

```
usage: class [-h] [--db DB] {init,banner,parse,list} ...

positional arguments:
  {init,banner,parse,list}
    init                initialize class database
    banner              interact directly with Banner
    parse               parse Banner HTML
    list                list students in the course

optional arguments:
  -h, --help            show this help message and exit
  --db DB               database URL
```

You will want to start with `class init` in order to create an empty class
database file, followed by some Banner comands.


### Banner subcommands

The `banner` subcommand directly interacts with the online Banner system.
It can be used to look up course IDs (`banner crn`) or to fetch
class lists and save the resulting student data into the local database
(`banner fetch`).

```
$ ./class banner -h
usage: class banner [-h] [--banner-root BANNER_ROOT] [--ca-bundle CA_BUNDLE]
                    [--credential-file CREDENTIAL_FILE] [--term TERM]
                    {crn,classlist,transcript} ...

positional arguments:
  {crn,classlist,transcript}
    crn                 find course CRN from Banner
    classlist           fetch class list
    transcript          fetch transcript

optional arguments:
  -h, --help            show this help message and exit
  --banner-root BANNER_ROOT
                        Root URL for all Banner requests
  --ca-bundle CA_BUNDLE
                        path to CA certificate bundle
  --credential-file CREDENTIAL_FILE
                        username/password file (YAML format)
  --term TERM           e.g., Fall 2016: 201601 [default: 201502]
```

It is helpful to create a file called `credentials.yaml` with your
username and password:

```sh
$ touch credentials.yaml
$ chmod 600 credentials.yaml
$ echo << EOF > credentials
username: your_user_name
password: your_password
EOF
$ chmod 400 credentials.yaml
```
