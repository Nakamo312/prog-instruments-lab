import json
import os
import logging, logging.config

class ChatLogger:
    """
    A class for managing chat logging based on a JSON configuration file.

    Initializes a logger from a configuration file and provides
    methods for obtaining loggers 
    with different names in the logger hierarchy.
    """

    def __init__(self):
        with open(os.path.join(os.getcwd(),"server_logging.json"),
                  mode='r', encoding='utf-8') as config:
            data = json.load(config)
            logging.config.dictConfig(data)
            self.logger = logging.getLogger('App')

    def getLogger(self, name:str = None) -> logging.Logger:
        """
        Returns a logger with the specified name in the logger hierarchy.    
        Args:
          name (str, optional): The name of the logger. If None, the root logger 'App' is returned. Defaults to None.

        Returns:
          logging.Logger: An instance of the logger.
        """
        return logging.getLogger('App.' + name if name else '')
