# class

This is a tool for interacting with Banner, the registration system used by
[Memorial University](http://www.mun.ca).
It suffers so that you don't have to.


## Installation

The simplest way to use `class` is to run it directly from a source checkout.
After installing a few Python dependencies:

```sh
$ pip install humanize inflect mechanicalsoup passlib peewee
```

clone this repository and test that you can run the `class` command:

```sh
$ ./class --help
```


## Usage

The command-line `class` tool uses a subcommand style of interaction:

```
usage: class [-h] [--db DB] {init,banner,parse,list,group,mail,plot} ...

positional arguments:
  {init,banner,parse,list,group,mail,plot}
    init                initialize class database
    banner              interact directly with Banner
    parse               parse Banner HTML
    list                list students in the course
    group               group students together (e.g., for labs)
    mail                send email to class
    plot                plot statistics

optional arguments:
  -h, --help            show this help message and exit
  --db DB               database URL
```

You will want to start with `class init` in order to create an empty class
database file, followed by some Banner comands.


### `banner` subcommands

The `banner` subcommand directly interacts with the online Banner system.
It can be used to look up course IDs (`banner crn`) or to fetch
class lists and save the resulting student data into the local database
(`banner fetch`).

```
$ class banner crn ENGI 3891
Found one course section:
201601 41327: ENGI 3891-001           95/100 registered (  5 remaining)
$ class banner --term 201601 classlist 41327
Foundations of Programming - ENGI 3891 001
Sep 07, 2016 - Dec 16, 2016
95 students

95 existing students, 0 new:
$ class banner transcript --all
201600001 Alice B Cool                     11 courses
[...]
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


### `parse` subcommands

The `parse` subcommands can be used to parse an already-downloaded
class list or transcript HTML file:

```
$ class parse transcript ~/Downloads/transcript.html
Parsed transcript for Alice B Cool:

ENGL 1080  Critical Reading&Writing; I      99
MATH 1000  Calculus I                       99
MATH 1001  Calculus II                      79
MATH 2050  Linear Algebra I                 99
ENGI 1010  Engineering Statics              99
CHEM 1050  General Chemistry I              99
PHYS 1050  Gen Phys I:Mechanics             99
ENGI 1030  Engineering Graphics & Design    99
ENGI 1020  Introduction to Programming      99
ENGI 1040  Mechanisms & Electric Circuits   99
PHYS 1051  Gen Phys II:Osc,Waves,Electrom   99

  A    10  **********
  B     1  *

 Subj   N   Min   Avg   Max
  ----  --   ---  -----  ---
     *  11   99%  99.0%  99%
  ENGI   4   99%  99.0%  99%
  MATH   3   79%  92.3%  99%
  PHYS   2   99%  99.0%  99%
  CHEM   1   99%  99.0%  99%
  ENGL   1   99%  99.0%  99%
```

These operations are idempotent, i.e., it is safe to import a class list or
transcript multiple times.


### `list` subcommand

The `class list` command can be used to display selected pieces of information
about each student, possibly sorted according to a number of sort fields:

```
$ class list
      abc123 201600001 Alice B Cool                    abc123@mun.ca Group 1 
      [...]

$ class list username name level group --sort-by group --reverse
Alice B Cool             201600001       abc123 Undergrad
      [...]
```


### `group` subcommand

The `class group` command can be used to put students into groups
(e.g., lab groups) in a manual or automatic way:

```
$ class group abc123 def456
   1          abc123 Alice B Cool                def456 Dwayne E Foghorn
$ class group --auto
   2          abc123 Alice B Cool                def456 Dwayne E Foghorn
   3          pc1234 Peter Capaldi               rs1234 River Song
```


### `svn` subcommand

This command can be used to generate configuration files for a Subversion
repository (e.g., `authz` for access control and `htpasswd` for hashed
passwords).
It also generates a `groups.json` file that describes lab groups for the
`scripts/svn-affected-users` script.

```
class svn --prefix 2016 --instructors me1234 --tas ta1234,ta5678
Writing 50 groups and 100 students to authz
Writing 50 groups to groups.json
```


### `mail` subcommand

The `class mail` command can be used to email groups of students, using BCC as
appropriate to hide students' email addresses from each other.
When the `--test` flag is present, the command simply prints the message
that *would* be sent:

```
$ class mail --test --to abc123,def456 --sender me@mun.ca --subject 'ENGI 1234: labs'
This is a message typed directly into the console.
^D
From nobody Thu Sep  8 14:38:08 2016
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: base64
Subject: ENGI 3891: test
From: me@mun.ca
To: me@mun.ca
Bcc: abc123@mun.ca, def456@mun.ca

aGkK
```

```
$ class mail --test --all --sender me@mun.ca --subject foo message.txt
From nobody Thu Sep  8 14:38:08 2016
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: base64
Subject: foo
From: me@mun.ca
To: me@mun.ca
Bcc: abc123@mun.ca, def456@mun.ca, pc1234@mun.ca, rs1234@mun.ca

dGVzdCBtZXNzYWdlCg==
```

```
$ echo "test message" | class mail --test --all --sender me@mun.ca --subject foo
From nobody Thu Sep  8 14:38:08 2016
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: base64
Subject: foo
From: me@mun.ca
To: me@mun.ca
Bcc: abc123@mun.ca, def456@mun.ca, pc1234@mun.ca, rs1234@mun.ca

dGVzdCBtZXNzYWdlCg==
```

(note the use of base64 encoding for messages encoded in UTF-8)

When the `--test` flag is removed, the message is actually sent.


### `plot` subcommand

`class plot` can be used to plot various useful graphs, such as the average of
all students' performance in a prerequisite course.
This command will only plot results that have already been parsed from
transcripts, so it may be useful to run `class banner transcript --all` first.

```
$ class plot course MATH 1000
$ class plot subject ENGI
$ class plot eng-one
```
