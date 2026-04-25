import json
import os

from bots.core import logger


class Database(object):
    """
    A simple JSON-file-based database handler for storing and retrieving
    Property data.
    """

    def __init__(self, path: str = 'db.json'):
        """
        Initializes the database handler.

        Args:
            path: The file path to the JSON database (e.g., 'data/db.json').
        """

        self.path = path
        self.data = []

        self.connect()

    def connect(self) -> bool:
        """
        Simulates a connection by loading the JSON file into memory.
        If the file does not exist, it initializes an empty structure.
        """

        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        if not os.path.exists(self.path):
            logger.info(
                f'[{self.__class__.__name__}] {self.path} not found. Creating new database.'
            )

            self.data = []
            if not self.commit():
                return False

            return True

        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

            logger.info(
                f'[{self.__class__.__name__}] Connected to {self.path}')

            return True
        except (json.JSONDecodeError, IOError) as e:
            logger.error(
                f'[{self.__class__.__name__}] Failed to load database: {e}')

        self.data = []
        return False

    def add(self, data: object | list[object]) -> None:
        """
        Adds one or multiple objects to the database.
        Automatically handles serialization and updates existing entries.

        Args:
            data: A list of instances to save.
        """

        items = data if isinstance(data, list) else [data]

        if not items:
            logger.warning(
                f'[{self.__class__.__name__}] No data provided for bulk sync.'
            )
            return False

        existing_entries = {str(item.get('id')): i for i,
                            item in enumerate(self.data)}

        for obj in items:
            if isinstance(obj, dict):
                obj_dict = obj.copy()
                obj_id = str(obj.get('id', ''))
            elif hasattr(obj, 'to_dict'):
                obj_dict = obj.to_dict()
                obj_id = str(obj_dict.get('id', ''))
            else:
                obj_dict = obj.__dict__.copy()
                obj_id = str(getattr(obj, 'id', ''))

            if obj_id in existing_entries:
                index = existing_entries[obj_id]
                self.data[index] = obj_dict
            else:
                self.data.append(obj_dict)

    def read(self, target: object = object, filters: dict = None) -> list:
        """
        Syncs with the JSON file and returns deserialized object instances.

        Args:
            target: The class to instantiate.
            filters: Optional dictionary for filtering results.
        """

        def match(item, filters):
            """
            Checks if an item matches the provided filters, supporting both simple equality and operator-based filters.
            """

            for key, value in filters.items():
                item_value = item.get(key)

                if isinstance(value, dict):
                    for op, op_val in value.items():
                        if op == '$gte' and not (item_value >= op_val):
                            return False
                        if op == '$lte' and not (item_value <= op_val):
                            return False
                        if op == '$gt' and not (item_value > op_val):
                            return False
                        if op == '$lt' and not (item_value < op_val):
                            return False
                        if op == '$ne' and not (item_value != op_val):
                            return False
                        if op == '$in' and item_value not in op_val:
                            return False
                else:
                    if item_value != value:
                        return False

            return True

        self.connect()

        raw_data = self.data

        if filters:
            raw_data = [item for item in raw_data if match(item, filters)]

        return [self.__deserialize__(target, item) for item in raw_data]

    def commit(self) -> bool:
        """
        Saves the current in-memory data back to the JSON file.
        """

        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)

            logger.debug(
                f'[{self.__class__.__name__}] Changes committed to {self.path}'
            )

            return True
        except IOError as e:
            logger.error(
                f'[{self.__class__.__name__}] Failed to save data: {e}')

        return False

    def close(self) -> bool:
        """
        Closes the database connection. For JSON, this ensures
        all data is saved before the object is destroyed.
        """

        if not self.commit():
            logger.error(
                f'[{self.__class__.__name__}] Failed to commit changes before closing.'
            )
            return False

        logger.info(
            f'[{self.__class__.__name__}] Connection to {self.path} closed.')
        return True

    def __deserialize__(self, cls, data: dict):
        """
        Maps a dictionary back to a class instance using the class's
        own deserialization logic if available.
        """

        if hasattr(cls, 'from_dict'):
            return cls.from_dict(data)

        return cls(**data)
