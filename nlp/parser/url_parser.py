# url scanning token parser

from token_parser import TokenParser

class UrlParser(TokenParser):
    def __init__(self, tokens):
        TokenParser.__init__(self, tokens)

    def _init_hooks(self):
        self.regex['url'] = 'https?://(\\w)+\.(\\w)(([\\w/.]*)*)'

        self.TokenDict['sites']     = [ ]
        self.TokenDict['titles']    = [ ]


