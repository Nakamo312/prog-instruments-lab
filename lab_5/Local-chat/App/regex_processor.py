import re
from App.logger import ChatLogger

class RegexProcessor:
    def __init__(self):
        self.masked = True
        self.patterns = [
          (r"(?<=[^\w@])(?:https?:\/\/)?(?:www\.)?(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:[a-zA-Z]{2,6}|xn--[a-zA-Z0-9]+)(?:\/[^\s]*)?", "URL"),
          (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "MAIL"),
          (r"\+?[1-8]\d{10}|\+?[1-8][-.\s]\(?\d{3}\)?[-.\s]\d{3}?[-.\s](?:\d{2}[-.\s]\d{2}|\d{4})", "Phone",
           )
        ]
        self.logger = ChatLogger().getLogger(self.__class__.__name__)
    
    def regex_processing(self, message:str) -> str:
        for pattern, name in self.patterns:
            try:
                matches = re.findall(pattern, message, re.MULTILINE | re.DOTALL)
                for m in matches:
                    self.logger.info("CATCH: %s"\
                                     " | %s" %(name, m))  
            except Exception as e:
                self.logger.error("%s" %e)         
            message = re.sub(pattern, "******", message)
        return message