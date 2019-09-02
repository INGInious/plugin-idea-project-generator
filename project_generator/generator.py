#!/usr/bin/python

import os, shutil, argparse
import xml.etree.ElementTree as ET


def has_classes(resource_path):
    """
    Check if the directory 'resource_path' has java files or not.
    """
    files = os.listdir(resource_path)
    for file in files:
        if '.java' in file:
            return True
    return False


def run_all(webdav_path, course_id, libs_path, resources_path, test_path, archive_path):
    """
    Create a IntelliJ project for all tasks inside the webdav
    :param webdav_path: A path to the webdav
    :param course_id: The id of the course (like LEPL1402)
    :param libs_path: The path inside the webdav to the directory containing the libraries
    :param resources_path: The path inside the task directory to the directory
                            containing the java classes to be filled by students
    :param test_path: The path inside the task directory to the directory containing the tests
    :param archive_path: The path inside the task directory to the directory where the archive will be generated
    """
    dirs = os.listdir(webdav_path)
    for dir in dirs:
        full_path = os.path.join(webdav_path, dir)
        if os.path.isdir(full_path):
            requirement = check_requirements(webdav_path, dir, resources_path, test_path, libs_path, archive_path)
            if process_requirements(requirement):
                if has_classes(os.path.join(full_path, resources_path)):
                    # Create an archive only if classes are given to students
                    run(webdav_path, dir, course_id, libs_path, resources_path, test_path, archive_path, requirement)


def create_structure(webdav_path, project_name):
    """
    Create the directory that will contain the project
    """
    new_dir = os.path.join(webdav_path, project_name)
    if os.path.isdir(new_dir):
        shutil.rmtree(new_dir)
    os.mkdir(new_dir)
    return new_dir


def gen_src(new_dir):
    """
    Create a directory named src
    """
    src = os.path.join(new_dir, 'src')
    os.mkdir(src)
    return src


def gen_classes(webdav_path, src_folder, resource_path):
    """
    Copy all java files from 'resource_path' to the 'src/main' directory of the project
    """
    main_dir = os.path.join(src_folder, 'main')
    os.mkdir(main_dir)
    java_dir = os.path.join(main_dir, 'java')
    os.mkdir(java_dir)
    public = os.path.join(webdav_path, resource_path)
    files = os.listdir(public)
    for file in files:
        full_path = os.path.join(public, file)
        if os.path.isfile(full_path) and '.java' in file:
            shutil.copy(full_path, java_dir)


def gen_tests(webdav_path, src_folder, test_path, has_tests):
    """
    Copy all test files from 'test_path' to the 'src/test' directory of the project
    """
    main_dir = os.path.join(src_folder, 'test')
    os.mkdir(main_dir)
    java_dir = os.path.join(main_dir, 'java')
    os.mkdir(java_dir)
    if has_tests:
        unit_test = os.path.join(webdav_path, test_path)
        files = os.listdir(unit_test)
        for file in files:
            full_path = os.path.join(unit_test, file)
            if os.path.isfile(full_path) and '.java' in full_path:
                shutil.copy(full_path, java_dir)


def gen_libs(webdav_path, new_dir, libs_path, has_libs):
    """
    Copy all libraries from 'libs_path' to the 'libs' directory of the project
    """
    directory = os.path.join(webdav_path, libs_path)
    libs = os.path.join(new_dir, 'libs')
    os.mkdir(libs)
    if has_libs:
        files = os.listdir(directory)
        for file in files:
            full_path = os.path.join(directory, file)
            if os.path.isfile(full_path):
                shutil.copy(full_path, libs)
        return files
    else:
        return []


def gen_target(src_foler):
    """
    Create the 'target' directory and subdirectories
    """
    target = os.path.join(src_foler, 'target')
    os.mkdir(target)
    dirs = ['classes', 'generated-sources', 'generated-test-sources', 'test-classes']
    for direct in dirs:
        os.mkdir(os.path.join(target, direct))


def gen_pom(new_dir, project_name, libs, has_libs):
    """
    Copy the pom.xml file into the project directory
    and fill it correctly with the name of the project and the dependencies of the libraries
    """
    cwd = os.getcwd()
    shutil.copy(os.path.join(cwd, 'pom.xml'), new_dir)
    pom = os.path.join(new_dir, 'pom.xml')
    tree = ET.parse(pom)
    root = tree.getroot()
    # Add the name of the project to the pom.xml
    artifact_id = root.find('artifactId')
    group_id = root.find('groupId')
    group_id.text = project_name
    artifact_id.text = project_name
    if has_libs:
        put_dependencies(libs, root)
    # Add these lines to the top of the pom
    root.set('xmlns', 'http://maven.apache.org/POM/4.0.0')
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.set('xsi:schemaLocation', 'http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd')
    indent(root)
    tree.write(pom, encoding="UTF-8", xml_declaration=True)


def indent(elem, level=0):
    """
    Indent correctly the 'pom.xml' file
    Solution find at http://effbot.org/zone/element-lib.htm#prettyprint
    """
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def put_dependencies(libs, root):
    """
    Put the correct dependencies corresponding to all libraries of the project inside the 'pom.xml'
    """
    dependencies = root.find('dependencies')
    if dependencies is None:
        print("The pom.xml file is broken")
        return
    for lib in libs:
        fname = os.path.splitext(os.path.basename(lib))[0]
        v = '0.0.0'
        name = fname
        if '-' in fname:
            v = str.split(fname, '-')[-1]
            name = fname.replace('-' + v, '')
        dependency = ET.SubElement(dependencies, 'dependency')
        group_id = ET.SubElement(dependency, 'groupId')
        group_id.text = name
        artifact_id = ET.SubElement(dependency, 'artifactId')
        artifact_id.text = name
        version = ET.SubElement(dependency, 'version')
        version.text = v
        scope = ET.SubElement(dependency, 'scope')
        scope.text = 'system'
        system_path = ET.SubElement(dependency, 'systemPath')
        system_path.text = '${project.basedir}/libs/' + fname + '.jar'


def gen_archive(new_dir, webdav_task_dir, archive_path,  project_name):
    """
    Create the archive from the generated project
    """
    shutil.make_archive(os.path.join(webdav_task_dir, archive_path, project_name), 'zip', new_dir)
    shutil.rmtree(new_dir)


def delete_archive(webdav_task_dir, archive_path, project_name):
    """
    Delete the archive if one exist with the same name (remove an old one)
    """
    archive = os.path.join(webdav_task_dir, archive_path, project_name) + '.zip'
    if os.path.isfile(archive):
        os.remove(archive)


def check_requirements(webdav_path, task_dir, resource_path, test_path, libs_path, archive_path):
    """
    Check if the different arguments passed to the program are valid.
    More precisely check if the directories of the different path are valid.
    """
    req = {
        'webdav': True,
        'task_path': True,
        'resource_path': True,
        'test_path': True,
        'libs_path': True,
        'archive_path': True
    }
    if not os.path.isdir(webdav_path):
        print('[' + task_dir + '] The webdav directory is not correct')
        req['webdav'] = False
    if not os.path.isdir(os.path.join(webdav_path, task_dir)):
        print('[' + task_dir + '] The task directory is not correct')
        req['task_path'] = False
    if not os.path.isdir(os.path.join(webdav_path, task_dir, resource_path)):
        print('[' + task_dir + '] The resource directory is not correct')
        req['resource_path'] = False
    if not os.path.isdir(os.path.join(webdav_path, task_dir, test_path)):
        print('[' + task_dir + '] The test directory is not correct')
        req['test_path'] = False
    if not os.path.isdir(os.path.join(webdav_path, libs_path)):
        print('[' + task_dir + '] The library directory is not correct')
        req['libs_path'] = False
    if not os.path.isdir(os.path.join(webdav_path, task_dir, archive_path)):
        print('[' + task_dir + '] The archive directory is not correct')
        req['archive_path'] = False
    return req


def run(webdav_path, task_dir, course_id, libs_path, resources_path, test_path, archive_path, requirement):
    """
    Create an IntelliJ project for the specified task
    :param webdav_path: A path to the webdav
    :param task_dir: The name of the task
    :param course_id: The id of the course (like LEPL1402)
    :param libs_path: The path inside the webdav to the directory containing the libraries
    :param resources_path: The path inside the task directory to the directory
                            containing the java classes to be filled by students
    :param test_path: The path inside the task directory to the directory containing the tests
    :param archive_path: The path inside the task directory to the directory where the archive will be generated
    """
    project_name = course_id + '_' + task_dir  # define project name
    webdav_task_dir = os.path.join(webdav_path, task_dir)  # path to task
    delete_archive(webdav_task_dir, archive_path, project_name)  # delete the project archive if one exists
    new_dir = create_structure(webdav_task_dir, project_name)  # create the project directory and get the path to it
    src = gen_src(new_dir)  # create the src folder
    gen_classes(webdav_task_dir, src, resources_path)  # add the classes to be filled by students
    gen_tests(webdav_task_dir, src, test_path, requirement['test_path'])  # add tests if there are tests
    libs = gen_libs(webdav_path, new_dir, libs_path, requirement['libs_path'])  # add libraries if there are libs
    gen_target(new_dir)  # create target directory with sub directories
    gen_pom(new_dir, project_name, libs, requirement['libs_path'])  # generate pom.xml file
    gen_archive(new_dir, webdav_task_dir, archive_path, project_name)  # generate the archive


def process_requirements(requirement):
    """
    If the following requirements are not valid, abort the creation of the project
    """
    if not requirement['webdav'] or not requirement['task_path'] or not requirement['resource_path'] \
            or not requirement['archive_path']:
        return False
    return True
    # test_path and lib_path are optional


def process_args():
    """
    Get the arguments of the program and process them
    """
    webdav_path = os.getcwd()
    course_id = 'LEPL'
    libs_path = '$common/libs'
    resources_path = 'public'
    test_path = 'unit_test'
    archive_path = 'public'
    parser = argparse.ArgumentParser(prog="python3 generator.py")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-task', '--task_dir', help='The directory name inside the webdav')
    group.add_argument('-A', '--all', help='Generate an IntelliJ project for all tasks inside the webdav',
                        default=False, action='store_true')
    parser.add_argument('-wd', '--webdav_path', help='The location of the webdav of the course', default=webdav_path)
    parser.add_argument('-c', '--course_id', help='The course acronym', default=course_id)
    parser.add_argument('-l', '--libraries_path', help='The path inside the webdav to the libraries to include '
                                                  'inside the project', default=libs_path)
    parser.add_argument('-r', '--resources_path', help='The path inside the task_dir to the directory containing'
                                                        ' the classes to be filled by students', default=resources_path)
    parser.add_argument('-test', '--tests_path', help='The path inside the task_dir to the directory containing '
                                                   'the tests', default=test_path)
    parser.add_argument('-arch', '--archive_path', help='The path inside path_dir to the directory where the archive '
                                                     'of the project will be generated', default=archive_path)

    args = parser.parse_args()
    task_dir = args.task_dir
    webdav_path = args.webdav_path
    course_id = args.course_id
    libs_path = args.libraries_path
    resources_path = args.resources_path
    test_path = args.tests_path
    archive_path = args.archive_path
    if args.all:
        # if option all set
        run_all(webdav_path, course_id, libs_path, resources_path, test_path, archive_path)
    else:
        requirement = check_requirements(webdav_path, task_dir, resources_path, test_path, libs_path, archive_path)
        if process_requirements(requirement):
            run(webdav_path, task_dir, course_id, libs_path, resources_path, test_path, archive_path, requirement)


if __name__ == '__main__':
    process_args()
