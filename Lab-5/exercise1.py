
resources = [
    [101, "Laptop", "Electronics", 8],
    [102, "Projector", "Electronics", 0],
    [103, "Whiteboard", "Classroom", 5],
    [104, "Microphone", "Audio", 3],
    [105, "Camera", "Electronics", 2]
]


#Display all resources
def display_resources(resources):
    if not resources:
        print("No resources found.")
        return

    for resource in resources:
        resource_id, name, category, quantity = resource

        if quantity < 0:
            print(resource_id, name, category, "- Invalid quantity")
        else:
            print(resource_id, name, category, quantity)


#Search resources by category
def search_by_category(resources, category):
    found = False

    for resource in resources:
        if resource[2].lower() == category.lower():
            print(resource)
            found = True

    if not found:
        print("No resources found in this category.")


#Find unavailable resources
def find_unavailable(resources):
    found = False

    for resource in resources:
        if resource[3] == 0:
            print(resource)
            found = True

    if not found:
        print("No unavailable resources found.")


# Search by resource ID (for testing)
def search_by_id(resources, resource_id):
    for resource in resources:
        if resource[0] == resource_id:
            print(resource)
            return

    print("Resource ID not found.")



print("All Resources:")
display_resources(resources)

print("\nElectronics Resources:")
search_by_category(resources, "Electronics")

print("\nUnavailable Resources:")
find_unavailable(resources)


# Testing and Debugging
print("\nTest 1: Unknown Resource ID")
search_by_id(resources, 999)

print("\nTest 2: Negative Quantity")
test_resources = resources + [
    [106, "Scanner", "Electronics", -3]
]
display_resources(test_resources)

print("\nTest 3: Zero Quantity")
find_unavailable(resources)

print("\nTest 4: Empty Resource List")
display_resources([])
