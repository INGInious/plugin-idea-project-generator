# LEPL1402-IntelliJProjectGenerator

Generator of [IntelliJ](https://www.jetbrains.com/idea/) project for [INGInious](https://inginious.info.ucl.ac.be/) courses.

The project is generated in a zip archive.

## generator.py usage:

`python3 generator.py -p <webdav_path> -d <task_dir> -c <course_id> [-l <libs_dir> -r <resources_dir> 
-t <tests_dir> -a <archive_path>]`

### Arguments list:
#### Mandatory arguments:
  `-p <webdav_path>` : the path to the directory containing all tasks
  `-d <task_dir>` : the name of the directory of the task
  `c <course_id>` : the course acronym (like **LEPL1402**)
#### Optional arguments:
  - `-l <libs_dir>` : 
      - The path from `<webdav_path>` to the directory containing the libraries to include inside the project.
      - For example is the directory containing the libraries is located at `<webdav_path>/$common/libs`, you should paste `$common/libs`.
      - By default this value is `$common/libs`. 
      - The name of the libraries **must be** `<lib_name>-<version>.jar`
  - `-r <resources_dir>`:
      - The path from `<task-dir>` to the directory containing the java files that the students must fill
      - The default value is `public`
  - `-t <tests_dir>` :
      - The path from `<task-dir>` to the directory containing the unit-tests given to the students
      - The default value is `unit_test`
  - `-a <archive_path>` :
      - The path from `<task-dir>` to the directory containing where the generated archive of the project will be placed
      - The default value is `public`
