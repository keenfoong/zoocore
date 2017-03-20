import re
import os
from zoo.libs.utils import file


class NameManager(object):
    """The name manager deals with the maniplation of a string based on an expression allowing for a formalised
    naming convention, we use the terms 'rule' and 'tokens' throughout the class to describe the logic.
    rules are just a basic expression like so '{side}_{area}_{counter}_{type}', the '_' isnt not necessary for any logic.
    the characters within the curly brackets are tokens which will be replace when its resolved.
    tokens have a set of possible values that it can use if the value set this token to doesn't exist then it wont be
    resolved. you can add tokens and values in memory per instance or you can add it to the config JSON file.
    """
    BASE_CONFIG_VAR = "ZOO_NAMING_BASE_PATH"
    USER_CONFIG_VAR = "ZOO_NAMING_USER_PATHS"
    # super temp
    os.environ[BASE_CONFIG_VAR] = os.path.realpath(os.path.join(os.path.dirname(__file__), "config.json"))

    refilter = r"(?<={)[^}]*"
    counter = {"value": 0, "padding": 3, "default": 0}

    def __init__(self, activeRule=None):
        """
        :param activeRule: the active rule to set, see setActiveRule()
        :type activeRule: str
        """
        self._activeRule = None
        self.config = None
        self.load()
        if activeRule:
            self.setActiveRule(activeRule)
        self.config["tokens"]["counter"] = self.counter

    def setActiveRule(self, rule):
        """Sets the active rule, rules a basic expression that dictate how a name is resolved
        :param rule: the rule name, see method rules()
        :type rule: str
        """
        self._activeRule = rule

    def activeRule(self):
        """Returns the currently active rule name
        :rtype: str
        """
        return self._activeRule

    def rules(self):
        """returns all the currently active rules
        :return: a list of active rule names
        :rtype: list
        """
        return self.config["rules"].keys()

    def expression(self):
        return self.config["rules"][self.activeRule()]["expression"]

    def setExpression(self, value):
        self.config["rules"][self.activeRule()]["expression"] = value

    def description(self):
        return self.config["rules"][self.activeRule()]["description"]

    def setRuleDescription(self, value):
        self.config["rule"][self.activeRule()]["description"] = value

    def creator(self):
        return self.config[self.activeRule()]["creator"]

    def setCreator(self, creator):
        self.config[self.activeRule()]["creator"] = creator

    def addToken(self, name, value, default):
        data = {"default": default}
        data.update(value)
        self.config["tokens"][name] = data

    def hasToken(self, tokenName):
        return tokenName in self.config["tokens"]

    def hasTokenValue(self, tokenName, value):
        return self.hasToken(tokenName) and value in self.config["tokens"][tokenName]

    def updateTokenValue(self, name, value):
        if not self.hasToken(name):
            raise ValueError("Config has no token called {}".format(name))
        self.config["tokens"][name].update(value)

    def tokenValue(self, name):
        if not self.hasToken(name):
            raise ValueError("Config has no token called {}".format(name))
        if name == "counter":
            return self.config["tokens"][name]["value"]
        return self.config["tokens"][name]["default"]

    def addRule(self, name, expression, description, asActive=True):
        self.config["rule"].update({name: {"expression": expression,
                                           "description": description}})
        if asActive:
            self.setActiveRule(name)

    def rule(self, name):
        if self.config:
            return self.config["rule"].get(name)

    def setTokenDefault(self, name, value):
        tokens = self.config["tokens"]
        if name in tokens:
            tokens[name]["default"] = value

    def overrideToken(self, name, value, **kwargs):
        if not self.hasToken(name):
            self.addToken(name, {value, value}, default=value)

        if name == "counter":
            configData = self.config["tokens"][name]
            self.config["tokens"][name].update({"value": value,
                                                "padding": kwargs.get("padding", configData["padding"]),
                                                "default": kwargs.get("default", configData["default"])})
            return

        tokens = self.config["tokens"]
        if name in tokens:
            tokens[name]["default"] = value
            tokens[name].update(kwargs)

    def resolve(self):
        expression = self.expression()
        tokens = re.findall(NameManager.refilter, expression)
        newStr = expression
        for token in tokens:
            if token == "counter":
                val = str(self.counter["value"]).zfill(self.counter["padding"])
            else:
                val = self.config["tokens"][token]["default"]
            newStr = re.sub("{" + token + "}", val or "null", newStr)
        return newStr

    def save(self):
        configPath = os.environ[NameManager.BASE_CONFIG_VAR]
        file.saveJson(self.config, configPath)

    def load(self):
        configPath = os.environ[NameManager.BASE_CONFIG_VAR]
        data = file.loadJson(configPath)

        if os.environ.get(NameManager.USER_CONFIG_VAR):
            for p in os.environ[NameManager.USER_CONFIG_VAR].split(os.pathsep):
                if not p or not os.path.exists(p) or not p.endswith(".json"):
                    continue
                userData = file.loadJson(p)
                rules = userData.get("rules")
                tokens = userData.get("tokens")
                if rules:
                    data["rules"].update(rules)
                if tokens:
                    data["tokens"].update(tokens)
        self.config = data
