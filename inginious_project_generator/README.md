# LEPL1402-IntelliJProjectGenerator

Generator of [IntelliJ](https://www.jetbrains.com/idea/) project for [INGInious](https://inginious.info.ucl.ac.be/) courses.

The project is generated in a zip archive.

## generator.py usage:

``` bash
usage: python3 generator.py [-h] (-task TASK_DIR | -A) [-wd WEBDAV_PATH]
                            [-c COURSE_ID] [-l LIBRARIES_PATH]
                            [-r RESOURCES_PATH] [-test TESTS_PATH]
                            [-arch ARCHIVE_PATH] [-p PLUGIN_PATH]

optional arguments:
  -h, --help            show this help message and exit
  -task TASK_DIR, --task_dir TASK_DIR
                        The directory name inside the webdav
  -A, --all             Generate an IntelliJ project for all tasks inside the
                        webdav
  -wd WEBDAV_PATH, --webdav_path WEBDAV_PATH
                        The location of the webdav of the course
  -c COURSE_ID, --course_id COURSE_ID
                        The course acronym
  -l LIBRARIES_PATH, --libraries_path LIBRARIES_PATH
                        The path inside the webdav to the libraries to include
                        inside the project
  -r RESOURCES_PATH, --resources_path RESOURCES_PATH
                        The path inside the task_dir to the directory
                        containing the classes to be filled by students
  -test TESTS_PATH, --tests_path TESTS_PATH
                        The path inside the task_dir to the directory
                        containing the tests
  -arch ARCHIVE_PATH, --archive_path ARCHIVE_PATH
                        The path inside path_dir to the directory where the
                        archive of the project will be generated
  -p PLUGIN_PATH, --plugin_path PLUGIN_PATH
                        Path to the location of this script

```