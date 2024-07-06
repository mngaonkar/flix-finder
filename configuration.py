import json
from enum import Enum
from logging import config


from sympy import im
import constants

class VectorStoreStatus(Enum):
    READY = 1
    NOT_INTIALIZED = 2
    ERROR = 3

class Configuration(object):
    """Class for storing application configuration."""
    def __init__(self, config_file=constants.DEFAULT_CONFIF_FILE):
        self.config_file = config_file
        self_config = None

    def load_config(self):
        try:
            self._config = json.load(open(self.config_file))
        except FileNotFoundError:
            self.create_new_config()
            self._config = json.load(open(self.config_file))

    def save_increamental_config(self, key, value):
        self._config[key] = value
        json.dump(self._config, open(self.config_file, "w"))

    def get_vector_store_config(self, database_name: str):
        return VectorStoreConfig(self, database_name)
    
    def get_config(self):
        return self._config
    
    def create_new_config(self):
        self._config = {}
        json.dump(self._config, open(self.config_file, "w"))

class VectorStoreConfig():
    """Class for storing vector store configuration."""
    KEY_VECTOR_STORES = "vector_stores"
    def __init__(self, config_obj: Configuration, database_name: str) -> None:
        self._config_obj = config_obj
        self.database_name = database_name

    def get_vector_store_status(self):
        try:
            if self.database_name not in self._config_obj._config["vector_stores"]:
                return VectorStoreStatus.NOT_INTIALIZED
        except KeyError:
            return VectorStoreStatus.NOT_INTIALIZED
        
        return self._config_obj._config[self.KEY_VECTOR_STORES][self.database_name]["status"]
    
    def set_vector_store_status(self, status: VectorStoreStatus):
        if self.KEY_VECTOR_STORES not in self._config_obj._config:
            self._config_obj._config[self.KEY_VECTOR_STORES] = {}

        if self.database_name not in self._config_obj._config[self.KEY_VECTOR_STORES]:
            self._config_obj._config[self.KEY_VECTOR_STORES][self.database_name] = {}
            
        self._config_obj._config[self.KEY_VECTOR_STORES][self.database_name]["status"] = status.value
        return self

    def get_config(self):
        return self._config_obj._config[self.KEY_VECTOR_STORES]
    
    def save_config(self):
        self._config_obj.save_increamental_config(self.KEY_VECTOR_STORES, self._config_obj._config[self.KEY_VECTOR_STORES])
    
