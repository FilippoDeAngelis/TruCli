from typing import Callable, Any, List, Dict
import logging


class Param:

    def __init__(self, flag: str, arg_name: str, typ: type, prompt: str = None, default=None, help: str = None):
        """Initialize a param.

        Arguments:
            flag -- the flag for the param ('-v')
            arg_name -- the name of the corresponding parameter in the function
            typ -- the type of the corresponding parameter in the function
            prompt -- a question that will be asked to the user if the param hasn't been specified
            default -- the default value of the param (either this or prompt have to be set)
            help -- the help text for the param"""
        # mandatory params
        self.flag = flag
        self.arg_name = arg_name
        self.typ = typ
        # either one of the following must be set
        self.prompt = prompt
        self.default = default
        if prompt is None and default is None:
            raise Exception('Either prompt or default must be defined. Both were None.')
        # optional params
        self.help = help


class Cli:

    def __init__(self):
        self.__commands = {}
        self.add_command('help', self.__help)
        self.prompt = '>'

    def run(self):
        while True:
            self.main_loop()

    def main_loop(self):
        line = input(self.prompt)
        name = line.split(' ')[0]
        try:
            tokens = self.__parse(line)
        except Exception as e:
            print(e)
            return
        logging.debug('Tokens: ' + str(tokens))
        if tokens is None:
            print(line + ': Could not parse command.')
            return
        if 'help' in tokens[1].keys():
            ret = self.__generate_help(name)
        else:
            params = self.__commands[name][1]  # get all parameters in the specified command
            for param in params:  # check if a parameter with no default hasn't been specified
                if param.default is None and param.arg_name not in tokens[1]:
                    param_in = input(param.prompt + ': ')
                    try:
                        tokens[1][param.arg_name] = param.typ(param_in)
                    except ValueError:
                        print(param_in + ' is not a ' + param.typ.__name__)
                        return
                elif param.arg_name not in tokens[1]:  # we have a default, so apply it
                    tokens[1][param.arg_name] = param.default
            del tokens[1]['help']
            ret = tokens[0](**tokens[1])
        if ret is not None:
            print(ret)

    def add_command(self, name: str, func: Callable[[Any], Any], params: List[Param] = None):
        """Add a command.
            Arguments:
            name -- The name of the command. Represent how it will be called from the command line
            func -- The function that will be executed when the command is called
            params -- A list of objects Param representing the params for the command"""
        help_param = Param('-help', 'help', bool, default=False, help='Display this text')
        if params is not None:
            params.append(help_param)
        else:
            params = [help_param]
        self.__commands[name] = [func, params]

    def __help(self):
        """Display this text"""
        to_ret = 'Available commands:\n\n'
        for command in self.__commands:
            if self.__commands[command][0].__doc__ is not None:
                to_ret += command + ' -- ' + self.__commands[command][0].__doc__ + '\n'
            else:
                to_ret += command + '\n'
        return to_ret

    def __parse(self, line: str) -> Dict[callable, Dict[str, Any]]:
        tokens = line.split(' ')
        if not tokens[0] in self.__commands.keys():
            return None
        to_ret = [self.__commands[tokens[0]][0], {}] # [func, {arg_name1: arg1, arg_name2: arg2}]
        odd_spot = True # flags start at 1, but booleans only take one space. if you have a boolean you have to change to and from odd numbers
        for i in range(1, len(tokens)):
            if (odd_spot and i%2==1) or (not odd_spot and i%2==0): # if i should be odd and it is odd or viceversa
                param = self.__get_param_from_flag(tokens[0], tokens[i])
                arg_name = param.arg_name
                last_token = i >= len(tokens) - 1
                if not last_token and tokens[i].startswith('-') and not tokens[i+1].startswith('-'): # the token is a flag and the next one is arg
                    correct_type = self.__get_param_from_flag(tokens[0], tokens[i]).typ
                    try:
                        to_ret[1].update({arg_name: correct_type(tokens[i + 1])}) # cast the value to the appropriate type
                    except ValueError:
                        raise Exception(str(tokens[i + 1]) + ' is not a valid ' + correct_type.__name__)
                elif tokens[i].startswith('-'): # the token is a boolean
                    to_ret[1].update({arg_name: not param.default})
                    odd_spot = not odd_spot
                else:
                    return None
            # arg_name = self.__commands[tokens[0]][1][tokens[i]]
            # if arg_name is None:
            #     i += 1
            #     continue
            # to_ret[1].update({arg_name: tokens[i + 1]})
        return to_ret

    def __generate_help(self, name: str):
        """Generates a help page for 'name' functions"""
        func = self.__commands[name][0]
        if func.__doc__ is not None:
            help_string = func.__doc__ + '\n\nParameters:\n'
        else:
            help_string = 'Parameters:\n'
        params = self.__commands[name][1]
        for param in params:
            par_type = param.typ.__name__ if param.typ != bool else ''
            if param.help is not None:
                help_string += param.flag + ' ' + par_type + ' -- ' + param.help + '\n'
            else:
                help_string += param.flag + ' ' + par_type + ' -- ' + self.__generate_missing_help_string(param) + '\n'

        return help_string

    def __generate_missing_help_string(self, param: Param) -> str:
        return 'Set ' + param.arg_name

    def __get_param_from_flag(self, command_name: str, flag: str) -> Param:
        for param in self.__commands[command_name][1]:
            if param.flag == flag:
                return param
        return None


# Example Code =====================================================


def hi(name):
    """Greets a person."""
    print('Hello ' + str(name))


if __name__ == '__main__':
    print('Initializing example code. Try the \'hello\' command!')
    cli = Cli()
    cli.add_command('hello', hi, [Param('-n', 'name', str, prompt='Please enter a name', help='The name to be greeted')])
    cli.run()