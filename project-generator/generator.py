#!/usr/bin/python

import os, sys, shutil, argparse
import xml.etree.ElementTree as ET


def create_structure(webdav_path, project_name):
    new_dir = os.path.join(webdav_path, project_name)
    if os.path.isdir(new_dir):
        shutil.rmtree(new_dir)
    os.mkdir(new_dir)
    return new_dir


def gen_src(new_dir):
    src = os.path.join(new_dir, 'src')
    os.mkdir(src)
    return src


def gen_classes(webdav_path, src_folder, resource_path):
    main_dir = os.path.join(src_folder, 'main')
    os.mkdir(main_dir)
    java_dir = os.path.join(main_dir, 'java')
    os.mkdir(java_dir)
    public = os.path.join(webdav_path, resource_path)
    files = os.listdir(public)
    for file in files:
        full_path = os.path.join(public, file)
        if os.path.isfile(full_path):
            shutil.copy(full_path, java_dir)


def gen_tests(webdav_path, src_folder, test_path, has_tests):
    main_dir = os.path.join(src_folder, 'test')
    os.mkdir(main_dir)
    java_dir = os.path.join(main_dir, 'java')
    os.mkdir(java_dir)
    if has_tests:
        unit_test = os.path.join(webdav_path, test_path)
        files = os.listdir(unit_test)
        for file in files:
            full_path = os.path.join(unit_test, file)
            if os.path.isfile(full_path):
                shutil.copy(full_path, java_dir)


def gen_libs(webdav_path, new_dir, libs_path, has_libs):
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
    target = os.path.join(src_foler, 'target')
    os.mkdir(target)
    dirs = ['classes', 'generated-sources', 'generated-test-sources', 'test-classes']
    for direct in dirs:
        os.mkdir(os.path.join(target, direct))


def gen_pom(new_dir, project_name, libs, has_libs):
    cwd = os.getcwd()
    shutil.copy(os.path.join(cwd, 'pom.xml'), new_dir)
    pom = os.path.join(new_dir, 'pom.xml')
    tree = ET.parse(pom)
    root = tree.getroot()
    artifact_id = root.find('artifactId')
    group_id = root.find('groupId')
    group_id.text = project_name
    artifact_id.text = project_name
    if has_libs:
        put_dependencies(libs, root)
    root.set('xmlns', 'http://maven.apache.org/POM/4.0.0')
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.set('xsi:schemaLocation', 'http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd')
    indent(root)
    tree.write(pom, encoding="UTF-8", xml_declaration=True)


def indent(elem, level=0):
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
    shutil.make_archive(os.path.join(webdav_task_dir, archive_path, project_name), 'zip', new_dir)
    shutil.rmtree(new_dir)


def delete_archive(webdav_task_dir, archive_path, project_name):
    archive = os.path.join(webdav_task_dir, archive_path, project_name) + '.zip'
    if os.path.isfile(archive):
        os.remove(archive)


def check_requirements(webdav_path, task_dir, resource_path, test_path, libs_path, archive_path):
    status = True
    req = {
        'webdav': True,
        'task_path': True,
        'resource_path': True,
        'test_path': True,
        'libs_path': True,
        'archive_path': True
    }
    if not os.path.isdir(webdav_path):
        print('The webdav directory is not correct')
        req['webdav'] = False
        status = False
    if not os.path.isdir(os.path.join(webdav_path, task_dir)):
        print('The task directory is not correct')
        req['task_path'] = False
        status = False
    if not os.path.isdir(os.path.join(webdav_path, task_dir, resource_path)):
        print('The resource directory is not correct')
        req['resource_path'] = False
        status = False
    if not os.path.isdir(os.path.join(webdav_path, task_dir, test_path)):
        print('The test directory is not correct')
        req['test_path'] = False
        status = False
    if not os.path.isdir(os.path.join(webdav_path, libs_path)):
        print('The library directory is not correct')
        req['libs_path'] = False
        status = False
    if not os.path.isdir(os.path.join(webdav_path, task_dir, archive_path)):
        print('The archive directory is not correct')
        req['archive_path'] = False
        status = False
    return status, req


def run(webdav_path, task_dir, course_id, libs_path, resources_path, test_path, archive_path, requirement):
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
    if not requirement['webdav'] or not requirement['task_path'] or not requirement['resource_path'] \
            or not requirement['archive_path']:
        sys.exit(2)
    #test_path and lib_path are optional


def process_args():
    webdav_path = os.getcwd()
    course_id = 'LEPL'
    libs_path = '$common/libs'
    resources_path = 'public'
    test_path = 'unit_test'
    archive_path = 'public'
    parser = argparse.ArgumentParser()
    parser.add_argument('task_dir', help='The directory name inside the webdav')
    parser.add_argument('-p', '--webdav_path', help='The location of the webdav of the course', default=webdav_path)
    parser.add_argument('-c', '--course_id', help='The course acronym', default=course_id)
    parser.add_argument('-l', '--libraries_path', help='The path inside the webdav to the libraries to include '
                                                  'inside the project', default=libs_path)
    parser.add_argument('-r', '--resources_path', help='The path inside the task_dir to the directory containing'
                                                        ' the classes to be filled by students', default=resources_path)
    parser.add_argument('-t', '--tests_path', help='The path inside the task_dir to the directory containing '
                                                   'the tests', default=test_path)
    parser.add_argument('-a', '--archive_path', help='The path inside path_dir to the directory where the archive '
                                                     'of the project will be generated', default=archive_path)
    args = parser.parse_args()
    task_dir = args.task_dir
    webdav_path = args.webdav_path
    course_id = args.course_id
    libs_path = args.libraries_path
    resources_path = args.resources_path
    test_path = args.tests_path
    archive_path = args.archive_path
    (status, requirement) = check_requirements(webdav_path, task_dir, resources_path, test_path, libs_path, archive_path)
    if not status:
        process_requirements(requirement)
    run(webdav_path, task_dir, course_id, libs_path, resources_path, test_path, archive_path, requirement)


if __name__ == '__main__':
    process_args()
