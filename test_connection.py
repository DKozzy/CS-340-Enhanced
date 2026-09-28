import os

from CRUD_Python_Module import AnimalShelter


# ---------------------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------------------

username = os.getenv("AAC_MONGO_USER", "aacuser")
password = os.getenv("AAC_MONGO_PASSWORD")

if not password:
    raise RuntimeError(
        "AAC_MONGO_PASSWORD environment variable is not set."
    )

shelter = AnimalShelter(username, password)


# ---------------------------------------------------------------------------
# Connection and basic database operations
# ---------------------------------------------------------------------------

def test_database_connection():
    print("\n--- DATABASE CONNECTION TEST ---")

    connection_test = shelter.read_paginated(
        {"animal_type": "Dog"},
        page=1,
        page_size=1
    )

    dog_count = shelter.count({"animal_type": "Dog"})

    print("Connection successful!")
    print("Dogs found:", dog_count)

    if connection_test:
        print("First dog:")
        print(connection_test[0])
    else:
        print("No dog records found.")


# ---------------------------------------------------------------------------
# Pagination and sorting
# ---------------------------------------------------------------------------

def test_pagination():
    print("\n--- PAGINATION AND SORTING TESTS ---")

    print("\nTesting page 1...")
    page_one = shelter.read_paginated(
        {"animal_type": "Dog"},
        page=1,
        page_size=10,
        sort_field="animal_id",
        sort_direction=1
    )

    print("Page 1 records:", len(page_one))
    for animal in page_one:
        print(animal.get("animal_id"))

    print("\nTesting page 2...")
    page_two = shelter.read_paginated(
        {"animal_type": "Dog"},
        page=2,
        page_size=10,
        sort_field="animal_id",
        sort_direction=1
    )

    print("Page 2 records:", len(page_two))
    for animal in page_two:
        print(animal.get("animal_id"))

    print("\nTesting pagination validation...")
    invalid_page = shelter.read_paginated(
        {"animal_type": "Dog"},
        page=0,
        page_size=10
    )

    invalid_sort = shelter.read_paginated(
        {"animal_type": "Dog"},
        page=1,
        page_size=10,
        sort_field="animal_id",
        sort_direction=5
    )

    print("Invalid page result:", invalid_page)
    print("Invalid sort result:", invalid_sort)


# ---------------------------------------------------------------------------
# Aggregation and analytics
# ---------------------------------------------------------------------------

def test_aggregation():
    print("\n--- AGGREGATION TESTS ---")

    breed_summary = shelter.get_breed_summary(
        {"animal_type": "Dog"},
        limit=10
    )

    print("\nTop 10 dog breeds:")
    for breed in breed_summary:
        print(breed["_id"], "-", breed["count"])

    print("\nTesting aggregation limit validation...")
    invalid_limit = shelter.get_breed_summary(
        {"animal_type": "Dog"},
        limit="10"
    )

    print("Invalid aggregation limit:", invalid_limit)


# ---------------------------------------------------------------------------
# Shared rescue query used by index tests
# ---------------------------------------------------------------------------

def get_water_rescue_query():
    return {
        "animal_type": "Dog",
        "breed": {
            "$in": [
                "Labrador Retriever Mix",
                "Chesapeake Bay Retriever",
                "Newfoundland"
            ]
        },
        "sex_upon_outcome": "Intact Female",
        "age_upon_outcome_in_weeks": {
            "$gte": 26,
            "$lte": 156
        }
    }


# ---------------------------------------------------------------------------
# Index creation and query plans
# ---------------------------------------------------------------------------

def test_indexes():
    print("\n--- INDEX AND QUERY PLAN TESTS ---")

    print("\nTesting index creation...")
    index_names = shelter.create_indexes()
    print("Created indexes:", index_names)

    print("\nTesting index retrieval...")
    indexes = shelter.get_indexes()

    for index in indexes:
        print(index)

    print("\nTesting animal ID query execution plan...")
    explanation = shelter.explain_query(
        {"animal_id": "A716330"}
    )

    winning_plan = explanation["queryPlanner"]["winningPlan"]
    print("Winning query plan:")
    print(winning_plan)

    print("\nTesting rescue filter execution plan...")
    water_query = get_water_rescue_query()

    rescue_explanation = shelter.explain_query(water_query)
    rescue_plan = rescue_explanation["queryPlanner"]["winningPlan"]

    print("Water rescue winning query plan:")
    print(rescue_plan)


# ---------------------------------------------------------------------------
# Index performance comparison
# ---------------------------------------------------------------------------

def test_query_performance():
    print("\n--- QUERY PERFORMANCE TEST ---")

    water_query = get_water_rescue_query()

    # Run normally so MongoDB can use the compound index
    indexed_stats = shelter.explain_query_stats(water_query)

    # Force a collection scan to represent performance without the index
    collection_scan_stats = shelter.explain_query_stats(
        water_query,
        hint={"$natural": 1}
    )

    indexed_execution = indexed_stats["executionStats"]
    scan_execution = collection_scan_stats["executionStats"]

    print("\nWith rescue_filter_idx:")
    print("Documents returned:", indexed_execution["nReturned"])
    print("Documents examined:", indexed_execution["totalDocsExamined"])
    print("Index keys examined:", indexed_execution["totalKeysExamined"])
    print(
        "Execution time (ms):",
        indexed_execution["executionTimeMillis"]
    )

    print("\nWithout index (collection scan):")
    print("Documents returned:", scan_execution["nReturned"])
    print("Documents examined:", scan_execution["totalDocsExamined"])
    print("Index keys examined:", scan_execution["totalKeysExamined"])
    print(
        "Execution time (ms):",
        scan_execution["executionTimeMillis"]
    )


# ---------------------------------------------------------------------------
# Document normalization and validation
# ---------------------------------------------------------------------------

def test_document_normalization():
    print("\n--- DOCUMENT NORMALIZATION TEST ---")

    test_document = {
        "animal_id": " TEST001 ",
        "name": " Bruno ",
        "animal_type": " Dog ",
        "breed": " Labrador Retriever Mix ",
        "sex_upon_outcome": " Neutered Male "
    }

    normalized_document = shelter.normalize_document(test_document)

    print("Original:")
    print(test_document)

    print("\nNormalized:")
    print(normalized_document)


def test_document_validation():
    print("\n--- DOCUMENT VALIDATION TESTS ---")

    valid_document = {
        "animal_id": "TEST001",
        "animal_type": "Dog",
        "breed": "Labrador Retriever Mix",
        "sex_upon_outcome": "Neutered Male",
        "age_upon_outcome_in_weeks": 52
    }

    missing_field_document = {
        "animal_id": "TEST002",
        "animal_type": "Dog",
        "sex_upon_outcome": "Neutered Male"
    }

    blank_field_document = {
        "animal_id": "   ",
        "animal_type": "Dog",
        "breed": "Labrador Retriever Mix",
        "sex_upon_outcome": "Neutered Male"
    }

    negative_age_document = {
        "animal_id": "TEST003",
        "animal_type": "Dog",
        "breed": "Labrador Retriever Mix",
        "sex_upon_outcome": "Neutered Male",
        "age_upon_outcome_in_weeks": -5
    }

    print("Valid document:",
          shelter.validate_document(valid_document))
    print("Missing required field:",
          shelter.validate_document(missing_field_document))
    print("Blank required field:",
          shelter.validate_document(blank_field_document))
    print("Negative age:",
          shelter.validate_document(negative_age_document))


def test_update_validation():
    print("\n--- UPDATE VALIDATION TESTS ---")

    valid_update = {"name": "Updated Name"}
    normalized_update = {"breed": " Labrador Retriever Mix "}
    invalid_update = {"age_upon_outcome_in_weeks": -25}
    blank_update = {"breed": "   "}

    print("Valid partial update:",
          shelter.validate_update(valid_update))
    print("Valid breed update:",
          shelter.validate_update(normalized_update))
    print("Negative age update:",
          shelter.validate_update(invalid_update))
    print("Blank breed update:",
          shelter.validate_update(blank_update))


# ---------------------------------------------------------------------------
# Create operation and invalid-write protection
# ---------------------------------------------------------------------------

def test_create_operations():
    print("\n--- CREATE OPERATION TESTS ---")

    test_animal = {
        "animal_id": " CS499TEST001 ",
        "name": " Capstone Test ",
        "animal_type": " Dog ",
        "breed": " Labrador Retriever Mix ",
        "sex_upon_outcome": " Neutered Male ",
        "age_upon_outcome_in_weeks": 52
    }

    # Remove any leftover test record
    shelter.delete({"animal_id": "CS499TEST001"})

    try:
        print("\nTesting validated and normalized document creation...")

        creation_result = shelter.create(test_animal)
        print("Creation successful:", creation_result)

        stored_records = shelter.read({
            "animal_id": "CS499TEST001"
        })

        if stored_records:
            stored_animal = stored_records[0]

            print("Stored animal ID:", stored_animal["animal_id"])
            print("Stored name:", stored_animal["name"])
            print("Stored animal type:", stored_animal["animal_type"])
            print("Stored breed:", stored_animal["breed"])
            print(
                "Stored sex upon outcome:",
                stored_animal["sex_upon_outcome"]
            )
        else:
            print("Test animal was not found.")

    finally:
        deleted_count = shelter.delete({
            "animal_id": "CS499TEST001"
        })
        print("Test records deleted:", deleted_count)

    print("\nTesting rejection of invalid document...")

    invalid_animal = {
        "animal_id": "CS499INVALID001",
        "name": "Invalid Test",
        "animal_type": "Dog",
        # breed intentionally missing
        "sex_upon_outcome": "Neutered Male",
        "age_upon_outcome_in_weeks": -10
    }

    # Remove any leftover record before the rejection test
    shelter.delete({"animal_id": "CS499INVALID001"})

    invalid_creation_result = shelter.create(invalid_animal)
    print("Creation accepted:", invalid_creation_result)

    invalid_records = shelter.read({
        "animal_id": "CS499INVALID001"
    })

    print("Records found in database:", len(invalid_records))

    # Defensive cleanup
    shelter.delete({"animal_id": "CS499INVALID001"})


# ---------------------------------------------------------------------------
# Update operation and invalid-update protection
# ---------------------------------------------------------------------------

def test_update_operations():
    print("\n--- UPDATE OPERATION TESTS ---")

    update_test_animal = {
        "animal_id": "CS499UPDATE001",
        "name": "Original Name",
        "animal_type": "Dog",
        "breed": "Labrador Retriever Mix",
        "sex_upon_outcome": "Neutered Male",
        "age_upon_outcome_in_weeks": 52
    }

    # Remove any leftover test record
    shelter.delete({"animal_id": "CS499UPDATE001"})

    try:
        created = shelter.create(update_test_animal)
        print("Test record created:", created)

        # Update using values that require normalization
        modified_count = shelter.update(
            {"animal_id": "CS499UPDATE001"},
            {
                "name": " Updated Name ",
                "breed": " Labrador Retriever Mix "
            }
        )

        print("Records modified:", modified_count)

        # Verify normalized values were stored
        updated_records = shelter.read({
            "animal_id": "CS499UPDATE001"
        })

        if updated_records:
            updated_animal = updated_records[0]
            print("Stored name:", updated_animal["name"])
            print("Stored breed:", updated_animal["breed"])

        # Attempt an invalid update
        invalid_modified_count = shelter.update(
            {"animal_id": "CS499UPDATE001"},
            {
                "age_upon_outcome_in_weeks": -10
            }
        )

        print("Invalid update modified:", invalid_modified_count)

        # Verify the invalid value was not stored
        verification_records = shelter.read({
            "animal_id": "CS499UPDATE001"
        })

        if verification_records:
            print(
                "Age after invalid update:",
                verification_records[0]["age_upon_outcome_in_weeks"]
            )

    finally:
        deleted_count = shelter.delete({
            "animal_id": "CS499UPDATE001"
        })
        print("Test records deleted:", deleted_count)


# ---------------------------------------------------------------------------
# Run all database enhancement tests
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("GRAZIOSO SALVARE DATABASE ENHANCEMENT TESTS")
    print("=" * 70)

    test_database_connection()
    test_pagination()
    test_aggregation()
    test_indexes()
    test_query_performance()
    test_document_normalization()
    test_document_validation()
    test_update_validation()
    test_create_operations()
    test_update_operations()

    print("\n" + "=" * 70)
    print("DATABASE ENHANCEMENT TESTING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
