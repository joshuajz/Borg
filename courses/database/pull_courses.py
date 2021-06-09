from courses.database.queens import pull_values as p_queens
from courses.database.uoft import pull_values as p_uoft
from courses.database.waterloo import pull_values as p_uw


def pull_courses():

    print("Pulling Queens Courses.")
    p_queens()
    print("Finished Queens Courses.")

    print("Pulling UofT Courses")
    p_uoft()
    print("Finished UofT Courses.")

    print("Pulling Waterloo Courses.")
    p_uw()
    print("Finished Waterloo Courses.")
