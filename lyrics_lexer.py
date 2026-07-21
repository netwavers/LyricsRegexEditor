from lyrics_parser import TokenType

class Token:
    def __init__(self, token_type, content):
        self.token_type = token_type
        self.content = content

class LyricsLexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.tokens = []
        self._tokenize()
        self.token_pos = 0

    def _tokenize(self):
        text_len = len(self.text)
        OPEN_FULL = '\uff08'
        CLOSE_FULL = '\uff09'
        OPEN_BRACKET_FULL = '\uff3b'
        CLOSE_BRACKET_FULL = '\uff3d'
        
        # Characters that trigger a token change
        SPECIAL_CHARS = {
            '[': TokenType.OPEN_BRACKET,
            ']': TokenType.CLOSE_BRACKET,
            '(': TokenType.OPEN_PAREN,
            ')': TokenType.CLOSE_PAREN,
            OPEN_FULL: TokenType.OPEN_PAREN_FULL,
            CLOSE_FULL: TokenType.CLOSE_PAREN_FULL,
            OPEN_BRACKET_FULL: TokenType.OPEN_BRACKET_FULL,
            CLOSE_BRACKET_FULL: TokenType.CLOSE_BRACKET_FULL,
            '<': TokenType.ANGLE_LEFT,
            '>': TokenType.ANGLE_RIGHT,
            '-': TokenType.CHORD_MARK,
            '\n': TokenType.NL
        }
        
        while self.pos < text_len:
            c = self.text[self.pos]
            
            if c in SPECIAL_CHARS:
                self.tokens.append(Token(SPECIAL_CHARS[c], c))
                self.pos += 1
            else:
                # Consume as TEXT
                start = self.pos
                while self.pos < text_len and self.text[self.pos] not in SPECIAL_CHARS:
                    self.pos += 1
                content = self.text[start:self.pos]
                if content:
                    self.tokens.append(Token(TokenType.TEXT, content))
        
        self.tokens.append(Token(None, ""))
        
        # EOF Token
        self.tokens.append(Token(None, ""))

    def get_token(self):
        if self.token_pos < len(self.tokens):
            token = self.tokens[self.token_pos]
            self.token_pos += 1
            return token
        return self.tokens[-1]

    @property
    def index(self):
        return self.token_pos

    @index.setter
    def index(self, value):
        self.token_pos = value
