#!/usr/bin/python

import os, sys, getopt, shutil
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


def gen_tests(webdav_path, src_folder, test_path):
    main_dir = os.path.join(src_folder, 'test')
    os.mkdir(main_dir)
    java_dir = os.path.join(main_dir, 'java')
    os.mkdir(java_dir)
    unit_test = os.path.join(webdav_path, test_path)
    files = os.listdir(unit_test)
    for file in files:
        full_path = os.path.join(unit_test, file)
        if os.path.isfile(full_path):
            shutil.copy(full_path, java_dir)


def gen_libs(webdav_path, new_dir, libs_path):
    directory = os.path.join(webdav_path, libs_path)
    libs = os.path.join(new_dir, 'libs')
    os.mkdir(libs)
    files = os.listdir(directory)
    for file in files:
        full_path = os.path.join(directory, file)
        if os.path.isfile(full_path):
            shutil.copy(full_path, libs)
    return files


def gen_target(src_foler):
    target = os.path.join(src_foler, 'target')
    os.mkdir(target)
    dirs = ['classes', 'generated-sources', 'generated-test-sources', 'test-classes']
    for direct in dirs:
        os.mkdir(os.path.join(target, direct))


def gen_pom(new_dir, project_name, libs):
    cwd = os.getcwd()
    shutil.copy(os.path.join(cwd, 'pom.xml'), new_dir)
    pom = os.path.join(new_dir, 'pom.xml')
    tree = ET.parse(pom)
    root = tree.getroot()
    artifact_id = root.find('artifactId')
    group_id = root.find('groupId')
    group_id.text = project_name
    artifact_id.text = project_name
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


def check_requirements(path, dirname, resource_path, test_path, libs_path, archive_path):
    if not os.path.isdir(os.path.join(path, dirname, resource_path)) \
            or not os.path.isdir(os.path.join(path, dirname, test_path)) \
            or not os.path.isdir(os.path.join(path, libs_path))\
            or not os.path.isdir(os.path.join(path, dirname, archive_path)):
        print('The task files don\'t respect the desire structure')
        return False
    return True


def run(webdav_path, task_dir, course_id, libs_path, resources_path, test_path, archive_path):
    project_name = course_id + '_' + task_dir
    webdav_task_dir = os.path.join(webdav_path, task_dir)
    delete_archive(webdav_task_dir, archive_path, project_name)
    new_dir = create_structure(webdav_task_dir, project_name)
    src = gen_src(new_dir)
    gen_classes(webdav_task_dir, src, resources_path)
    gen_tests(webdav_task_dir, src, test_path)
    libs = gen_libs(webdav_path, new_dir, libs_path)
    gen_target(new_dir)
    gen_pom(new_dir, project_name, libs)
    gen_archive(new_dir, webdav_task_dir, archive_path, project_name)


def process_args(argv):
    webdav_path = ''
    task_dir = ''
    course_id = 'LINGI1402'
    libs_path = '$common/libs'
    resources_path = 'public'
    test_path = 'unit_test'
    archive_path = 'public'

    info_msg = "generator.py\n" \
                "\t -p <path_to_wevdav>\n" \
                "\t -d <task_directory>\n" \
                "\t -c <courseId>\n" \
                "\t -l <libraries_directory>\n" \
                "\t -r <resources_directory>\n" \
                "\t -t <test_directory>\n" \
                "\t -a <archive_directory>\n" \
                "\n \t<libraries_directory>\n" \
                "\t \t\tmust contains the path from the webdav directory to this directory\n" \
                "\t \t\tfor example if <libraries_directory_name> is located at /webdav/$common/libs, \n" \
                "\t \t\t\t<libraries_directory> should be \"$common/libs\"\n" \
                "\t <resources_directory>, <test_directory_name> and <archive_directory>\n" \
                "\t \t\tmust contain the path from <task_directory>\n" \
                "\t \t\tfor example if <resources_directory> is located at /webdav/<task_directory>/public/resources, \n" \
                "\t \t\t\t<resources_directory> should be \"public/resources\"\n"

    try:
        opts, args = getopt.getopt(argv, "hp:d:c:l:r:t:a:", ["path=", "dir=", "courseId=", "libs=", "resources=",
                                                           "tests=", "archive="])
    except getopt.GetoptError:
        print(info_msg)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(info_msg)
            sys.exit()
        elif opt in ("-p", "--path"):
            webdav_path = arg
        elif opt in ("-d", "--dir"):
            task_dir = arg
        elif opt in ("-c", "--courseId"):
            course_id = arg
        elif opt in ("-l", "--libs"):
            libs_path = arg
        elif opt in ('r', '--resources'):
            resources_path = args
        elif opt in ('t', '--tests'):
            test_path = arg
        elif opt in ('-a', '--archive'):
            archive_path = arg
    if not check_requirements(webdav_path, task_dir, test_path=test_path, resource_path=resources_path, libs_path=libs_path, archive_path=archive_path):
        sys.exit(2)
    run(webdav_path, task_dir, course_id, libs_path, resources_path, test_path, archive_path)


if __name__ == '__main__':
    process_args(sys.argv[1:])
