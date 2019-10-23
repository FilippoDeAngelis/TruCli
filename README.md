# TruCli
A small library to build CLIs fully contained in Python

# Installation
TruCli can easily be installed through pip
```
pip install TruCli
```

# Usage
TruCli is very simple to use. Here is a Hello World example:
```
from TruCli import Cli

def hello():
   print('Hello, World!')
  
cli = Cli()
cli.add_command('hello', hello)
cli.run()
```
This returns the following output:
```
>hello
Hello, World!
```

It is possible to add parameters, to give them as variables to our methods:
```
from TruCli import Cli

def hello(name):
    print('Hello, ' + name)
    
cli = Cli()
cli.add_command('hello', hi, {'-n': {'arg_name': 'name', 'type': str, 'default': 'World', 'help': 'Specify the name to be greeted'}})
cli.run()
```

The above code allows us to run the following commands:
```
>hello
Hello World
>hello -help
Greets a person.

Parameters:
-n str -- Specify the name to be greeted
-help  -- Display this text

>hello -n John
Hello John
```
