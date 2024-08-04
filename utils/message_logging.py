class MessageLogger():
    def __init__(self):
        self.messages = []
        
    def log(self, message):
        self.messages.append(message)
        
    def get_message(self):
        return '\n'.join(self.messages)
    
def log(logger, message):
    if not isinstance(logger, MessageLogger):
        return
    
    logger.log(message)