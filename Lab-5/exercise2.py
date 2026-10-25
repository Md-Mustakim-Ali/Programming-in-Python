students = [
    [201, "Amina", [78, 85, 90]],
    [202, "Rahim", [65, 70, 68]],
    [203, "Nadia", [92, 88, 95]],
    [204, "Hasan", [55, 60, 65]],
    [205, "Tania", [80, 80, 80]]
]


#Calculate average marks
def calculate_average(marks):
    if len(marks) != 3:
        return None

    for mark in marks:
        if not isinstance(mark, (int, float)) or not 0 <= mark <= 100:
            return None

    return sum(marks) / len(marks)


#Classify performance
def classify_performance(average):
    if average >= 80:
        return "Excellent"
    elif average >= 70:
        return "Good"
    elif average >= 60:
        return "Satisfactory"
    else:
        return "Needs Improvement"


# Display student report
def display_report(students):
    if not students:
        print("No student records found.")
        return

    for student in students:
        student_id, name, marks = student
        average = calculate_average(marks)

        if average is None:
            print(student_id, name, "- Invalid or missing marks")
            continue

        performance = classify_performance(average)

        print("ID:", student_id)
        print("Name:", name)
        print("Average:", round(average, 2))
        print("Performance:", performance)
        print("--------------------")



print("Student Performance Report:")
display_report(students)


# Testing and Debugging

print("\nTest 1: Equal Marks")
display_report([[205, "Tania", [80, 80, 80]]])

print("\nTest 2: Tied Averages")
display_report([
    [205, "Tania", [80, 80, 80]],
    [206, "Arif", [70, 80, 90]]
])

print("\nTest 3: Invalid Marks")
display_report([
    [207, "Rima", [85, 110, 90]]
])

print("\nTest 4: Missing Marks")
display_report([
    [208, "Imran", []]
])
