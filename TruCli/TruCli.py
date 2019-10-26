from typing import Callable, Any, Dict, List
import logging

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
            params = self.__commands[name][1] # get all parameters in the specified command
            for param_key in params: # check if a parameter with no default hasn't been specified
                if 'default' not in params[param_key].keys() and params[param_key]['arg_name'] not in tokens[1]:
                    param = input(params[param_key]['prompt'] + ': ')
                    try:
                        tokens[1][params[param_key]['arg_name']] = params[param_key]['type'](param)
                    except ValueError:
                        print(param + ' is not a ' + params[param_key]['type'].__name__)
                        return
                elif params[param_key]['arg_name'] not in tokens[1]: # we have a default, so apply it
                    tokens[1][params[param_key]['arg_name']] = params[param_key]['default']
            del tokens[1]['help']
            ret = tokens[0](**tokens[1])
        if ret is not None:
            print(ret)

    def add_command(self, name: str, func: Callable[[Any], Any], params: Dict[str, Dict[str, str]] = None):
        """Add a command.
            Arguments:
            name -- The name of the command. Represent how it will be called from the command line
            func -- The function that will be executed when the command is called
            params -- A dictionary encapsulating the flags and the names of the arguments to pass to the function,
            defaults to None
                structure: {flag1: {'arg_name': name1, 'type': type, 'default': def, 'help': 'help text', 'prompt': 'prompt_text'}}
                e.g. {'-v': {'arg_name': 'verbose', 'type': bool, 'default': False, 'help': 'More detailed outputs'}}"""

        mandatory_keys = ['arg_name', 'type'] # and either default or prompt
        if params is not None:
            if all(key in mandatory_keys for key in params.keys()): # check if some mandatory keys are not there
                raise Exception('Mandatory keys not found')
            for key in params: # check if we are missing both default and prompt
                if 'default' not in params[key].keys() and 'prompt' not in params[key].keys():
                    raise Exception('Params should include either a default or a prompt. ' + key + ' does not.')
            params.update({'-help': {'arg_name': 'help', 'type': bool, 'default': False, 'help': 'Display this text'}})
        else:
            params = {'-help': {'arg_name': 'help', 'type': bool, 'default': False, 'help': 'Display this text'}}
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


    def __parse(self, line: str) -> dict:
        tokens = line.split(' ')
        if not tokens[0] in self.__commands.keys():
            return None
        to_ret = [self.__commands[tokens[0]][0], {}] # [func, {arg_name1: arg1, arg_name2: arg2}]
        odd_spot = True # flags start at 1, but booleans only take one space. if you have a boolean you have to change to and from odd numbers
        for i in range(1, len(tokens)):
            if (odd_spot and i%2==1) or (not odd_spot and i%2==0): # if i should be odd and it is odd or viceversa
                arg_name = self.__commands[tokens[0]][1][tokens[i]]['arg_name']
                last_token = i >= len(tokens) - 1
                if not last_token and tokens[i].startswith('-') and not tokens[i+1].startswith('-'): # the token is a flag and the next one is arg
                    correct_type = self.__commands[tokens[0]][1][tokens[i]]['type']
                    try:
                        to_ret[1].update({arg_name: correct_type(tokens[i + 1])}) # cast the value to the appropriate type
                    except ValueError:
                        raise Exception(str(tokens[i + 1]) + ' is not a valid ' + correct_type.__name__)
                elif tokens[i].startswith('-'): # the token is a boolean
                    to_ret[1].update({arg_name: True})
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
        for key in params.keys():
            par_type = params[key]['type']
            par_type = par_type.__name__ if par_type != bool else ''
            if 'help' in params[key]:
                help_string += key + ' ' +  par_type + ' -- ' + params[key]['help'] + '\n'
            else:
                help_string += key + ' ' +  par_type + ' -- ' + self.__generate_missing_help_string(params[key]) + '\n'

        return help_string

    def __generate_missing_help_string(self, param: Dict[str, Any]):
        return 'Set ' + param['arg_name']

# Example Code =====================================================


def hi(name):
    """Greets a person."""
    print('Hello ' + str(name))

if __name__ == '__main__':
    print('Initializing example code. Try the \'hello\' command!')
    cli = Cli()
    cli.add_command('hello', hi, {'-n': {'arg_name': 'name', 'type': str, 'default': 'World', 'help': 'Specify the name to be greeted'}})
    cli.run()