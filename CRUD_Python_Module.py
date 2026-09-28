#Roger Fisher 9/28/2026


from pymongo import MongoClient
from pymongo.errors import PyMongoError

class AnimalShelter(object): 
    """ CRUD operations for Animal collection in MongoDB """ 

    def __init__(self, username, password): 
        # Initializing the MongoClient. This helps to access the MongoDB 
        # databases and collections. This is hard-wired to use the aac 
        # database, the animals collection.
        
        # Connection Variables 
        USER = username
        PASS = password
        HOST = 'localhost' 
        PORT = 27017 
        DB = 'aac' 
        COL = 'animals' 
        
        # Initialize Connection 
        self.client = MongoClient('mongodb://%s:%s@%s:%d?authSource=admin' % (USER,PASS,HOST,PORT)) 
        self.database = self.client[DB] 
        self.collection = self.database[COL]

    # ---------------------------------------------------------------------------
    # Document validation and normalization
    # ---------------------------------------------------------------------------

    # Normalize animal record values before storing them in MongoDB
    def normalize_document(self, document):
        if not isinstance(document, dict):
            return None

        normalized = document.copy()

        # Remove accidental leading/trailing whitespace from text fields
        text_fields = [
            "animal_id",
            "name",
            "animal_type",
            "breed",
            "color",
            "sex_upon_outcome",
            "outcome_type",
            "outcome_subtype"
        ]

        for field in text_fields:
            if field in normalized and isinstance(normalized[field], str):
                normalized[field] = normalized[field].strip()

        return normalized

    # Validate required animal record fields before database operations
    def validate_document(self, document):
        if not isinstance(document, dict):
            return False

        required_fields = [
            "animal_id",
            "animal_type",
            "breed",
            "sex_upon_outcome"
        ]

        # Required fields must exist and contain a value
        for field in required_fields:
            if field not in document:
                return False

            value = document[field]

            if value is None:
                return False

            if isinstance(value, str) and not value.strip():
                return False

        # Age must be numeric and cannot be negative when supplied
        if "age_upon_outcome_in_weeks" in document:
            age = document["age_upon_outcome_in_weeks"]

            if not isinstance(age, (int, float)):
                return False

            if age < 0:
                return False

        return True

    # Validate fields supplied during partial document updates
    def validate_update(self, new_values):
        if not isinstance(new_values, dict) or not new_values:
            return False

        # Required fields cannot be changed to blank or null values
        protected_fields = [
            "animal_id",
            "animal_type",
            "breed",
            "sex_upon_outcome"
        ]

        for field in protected_fields:
            if field in new_values:
                value = new_values[field]

                if value is None:
                    return False

                if isinstance(value, str) and not value.strip():
                    return False

        # Age must remain numeric and nonnegative when updated
        if "age_upon_outcome_in_weeks" in new_values:
            age = new_values["age_upon_outcome_in_weeks"]

            if not isinstance(age, (int, float)):
                return False

            if age < 0:
                return False

        return True

    # Inserts a new document into the animals collection
    def create(self, document):
        normalized_document = self.normalize_document(document)

        if not self.validate_document(normalized_document):
            return False

        try:
            self.collection.insert_one(normalized_document)
            return True

        except PyMongoError as error:
            print(f"Database error during document creation: {error}")
            return False

    # ---------------------------------------------------------------------------
    # Read and query operations
    # ---------------------------------------------------------------------------

    # Retrieve documents from the animals collection that match the query
    def read(self, query):
        if query is not None:
            results = self.collection.find(query)
            return list(results)
        else:
            return []

    # Retrieve one page of matching documents with optional sorting
    def read_paginated(
            self,
            query=None,
            page=1,
            page_size=10,
            sort_field=None,
            sort_direction=1):

        if query is None:
            query = {}

        if not isinstance(page, int) or not isinstance(page_size, int):
            return []

        if page < 1 or page_size < 1:
            return []

        if sort_direction not in (1, -1):
            return []

        try:
            cursor = self.collection.find(query)

            if sort_field is not None:
                cursor = cursor.sort(
                    sort_field,
                    sort_direction
                )

            skip_count = (page - 1) * page_size

            cursor = cursor.skip(skip_count).limit(page_size)

            return list(cursor)

        except PyMongoError as error:
            print(f"Database error during paginated read: {error}")
            return []

    # Count documents that match the supplied query
    def count(self, query=None):
        if query is None:
            query = {}

        return self.collection.count_documents(query)

    # Summarize matching animals by breed using MongoDB aggregation
    def get_breed_summary(self, query=None, limit=10):
        if query is None:
            query = {}

        if not isinstance(limit, int) or limit < 1:
            return []

        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": "$breed",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]

        try:
            return list(self.collection.aggregate(pipeline))

        except PyMongoError as error:
            print(f"Database error during breed aggregation: {error}")
            return []

    # ---------------------------------------------------------------------------
    # Index management and query analysis
    # ---------------------------------------------------------------------------
    def create_indexes(self):
        animal_id_index = self.collection.create_index(
            [("animal_id", 1)]
        )

        rescue_filter_index = self.collection.create_index(
            [
                ("animal_type", 1),
                ("breed", 1),
                ("sex_upon_outcome", 1),
                ("age_upon_outcome_in_weeks", 1)
            ],
            name="rescue_filter_idx"
        )

        return animal_id_index, rescue_filter_index

    # Retrieve information about indexes on the collection
    def get_indexes(self):
        return list(self.collection.list_indexes())

    # Explain how MongoDB executes a query
    def explain_query(self, query):
        if query is None:
            query = {}

        return self.collection.find(query).explain()

    # Return execution statistics for a MongoDB query
    def explain_query_stats(self, query=None, hint=None):
        if query is None:
            query = {}

        find_command = {
            "find": self.collection.name,
            "filter": query
        }

        if hint is not None:
            find_command["hint"] = hint

        return self.database.command(
            "explain",
            find_command,
            verbosity="executionStats"
        )

    # ---------------------------------------------------------------------------
    # Update operations
    # ---------------------------------------------------------------------------
    
    # Update the existing documents that match the query
    def update(self, query, new_values):
        if query is None:
            return 0

        normalized_values = self.normalize_document(new_values)

        if not self.validate_update(normalized_values):
            return 0

        try:
            result = self.collection.update_many(
                query,
                {"$set": normalized_values}
            )

            return result.modified_count

        except PyMongoError as error:
            print(f"Database error during document update: {error}")
            return 0

    # ---------------------------------------------------------------------------
    # Delete operations
    # ---------------------------------------------------------------------------
    
    # Delete the documents from the animals collection that match the query
    def delete(self, query):
        if query is not None:
            result = self.collection.delete_many(query)
            return result.deleted_count
        else: 
            return 0 