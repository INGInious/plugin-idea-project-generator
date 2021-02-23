# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import os

from flask import request, redirect
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.pages.tasks import TaskPage
from inginious_project_generator.generator import run, run_all

__version__ = "0.1.dev0"
PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))
DEFAULT_CONFIG = {
    "resources_path": "public",
    "tests_path": "unit_test",
    "libraries_path": "$common/libs",
    "archive_path": "public"
}


class ProjectGeneratorPage(INGIniousAdminPage):
    """ Page of administration of the plugin"""

    def GET_AUTH(self, course_id):
        course, _ = self.get_course_and_check_rights(course_id, allow_all_staff=True)
        data = get_configuration_file(course)
        if data is not None:
            return self.display_page(course, config=data)
        else:
            return self.display_page(course)

    def POST_AUTH(self, course_id):
        course, _ = self.get_course_and_check_rights(course_id, allow_all_staff=True)
        input_data = request.form
        task_id = None
        tests_path_ok = True
        libs_path_ok = True
        generation_ok = True
        requirements = None
        # when the button generate archive is pushed
        if input_data.get("action", "") == "generateAllProjects":
            new_data = {
                "resources_path": input_data["resources_path"],
                "tests_path": input_data["tests_path"],
                "libraries_path": input_data["libraries_path"],
                "archive_path": input_data["archive_path"]
            }
            # if we went directly to the generator page we generate the archive for all tasks
            if "task_to_generate" not in input_data:
                gen_all_archive(course, new_data)
            # if we went from a test we generate only the archive for this test
            else:
                task_id = input_data["task_to_generate"]
                requirements = get_requirements(course, task_id, new_data)
                tests_path_ok = requirements["test_path"]
                libs_path_ok = requirements["libs_path"]
                if generator.process_requirements(requirements):
                    gen_task_archive(course, task_id, new_data, requirements)
                else:
                    generation_ok = False
            edit_configuration_file(self.course_factory, course, new_data)
            return self.display_page(course, task_id, new_data, True, tests_path_ok, libs_path_ok, generation_ok, requirements)

        # if an admin went from a test
        elif input_data.get("action", "") == "generateProjectTask":
            data = get_configuration_file(course)
            task_id = input_data.get("task", "")
            if data is not None:
                requirements = get_requirements(course, task_id, data)
                return self.display_page(course, task_id, config=data, requirements=requirements)
            else:
                return self.display_page(course, input_data.get("task", ""))

    def display_page(self, course, task=None, config=None, generated=False, tests_path_ok=True, libs_path_ok=True, generation_ok=True, requirements=None):
        if config is None:
            config = DEFAULT_CONFIG
        return self.template_helper.render("project_generator.html",
                                           template_folder=os.path.join(PATH_TO_PLUGIN, 'templates'),
                                           course=course, task_id=task, libraries_path=config["libraries_path"],
                                           resources_path=config["resources_path"], tests_path=config["tests_path"],
                                           archive_path=config["archive_path"], generated=generated,
                                           tests_path_ok=tests_path_ok, libs_path_ok=libs_path_ok,
                                           generation_ok=generation_ok, requirements=requirements)


class DownloadPage(TaskPage):
    """ Page to download the archive. Also available for students """
    def GET(self, courseid, taskid):
        return redirect(self.app.get_homepath() + "/course/" + courseid + "/" + taskid)

    def POST(self, courseid, taskid):
        course = self.course_factory.get_course(courseid)
        data = get_configuration_file(course)
        archive_location = DEFAULT_CONFIG["archive_path"]
        if data is not None and "archive_path" in data:
            archive_location = data["archive_path"]
        if not has_archive(course, taskid, archive_location):
            # We generate an archive if none exists
            requirements = get_requirements(course, taskid, data)
            gen_task_archive(course, taskid, data, requirements)
        return redirect(
            self.app.get_homepath() + "/course/" + courseid + "/" + taskid + "/" + courseid + "_" + taskid + '.zip')


def get_requirements(course, taskid, data):
    """ Get the requirements for the generation from generator """
    return generator.check_requirements(course.get_fs().prefix, taskid,
                                                        data["resources_path"], data["tests_path"],
                                                        data["libraries_path"], data["archive_path"])


def gen_task_archive(course, taskid, data, requirements):
    """ Generate the archive for the specific taskid """
    run(course.get_fs().prefix, taskid, course.get_id(), data["libraries_path"],
        data["resources_path"], data["tests_path"], data["archive_path"], requirements,
        PATH_TO_PLUGIN)


def gen_all_archive(course, data):
    """ Generate the archive for all task inside the course """
    run_all(course.get_fs().prefix, course.get_id(), data["libraries_path"], data["resources_path"], data["tests_path"], data['archive_path'], PATH_TO_PLUGIN)


def has_archive(course, task_id, archive_location):
    """ Check if an archive already exists or not """
    archive_path = os.path.join(course.get_fs().prefix, task_id, archive_location)
    return os.path.isfile(os.path.join(archive_path, course.get_id() + "_" + task_id + '.zip'))


def edit_configuration_file(course_factory, course, data):
    """ Edit the configuration file with the new configuration """
    course_content = course_factory.get_course_descriptor_content(course.get_id())
    course_content["intellij"] = data
    course_factory.update_course_descriptor_content(course.get_id(), course_content)


def get_configuration_file(course):
    """ Get the actual configuration from the configuration file"""
    return course.get_descriptor().get("intellij", DEFAULT_CONFIG)


def task_menu(course, task, template_helper):
    """ Display (or not) the buttons in the task menu """
    data = get_configuration_file(course)
    requirements = get_requirements(course, task.get_id(), data)
    requirements_ok = generator.process_requirements(requirements) and requirements['test_path'] and requirements['libs_path']
    can_display = False
    if requirements["resource_path"]:
        can_display = generator.has_classes(course.get_fs().prefix, task.get_id(), data['resources_path'])
    return template_helper.render("task_menu.html", template_folder=os.path.join(PATH_TO_PLUGIN, 'templates'),
                                  plugin_path=PATH_TO_PLUGIN, course=course, task=task,
                                  libraries_path=data['libraries_path'], resources_path=data['resources_path'],
                                  tests_path=data['tests_path'], archive_path=data['archive_path'],
                                  generated=False, can_display=can_display, requirements_ok=requirements_ok)


def course_admin_menu(course):
    return 'project_generator', '<i class="fa fa-file-archive-o fa-fw"></i>&nbsp; Project Generator'


def init(plugin_manager, _, _2, _3):
    plugin_manager.add_page('/plugins/<courseid>/<taskid>/project_generator', DownloadPage.as_view("pgdownloadpage"))
    plugin_manager.add_page('/admin/<course_id>/project_generator', ProjectGeneratorPage.as_view("pggeneratorpage"))
    plugin_manager.add_hook('task_menu', task_menu)
    plugin_manager.add_hook('course_admin_menu', course_admin_menu)

