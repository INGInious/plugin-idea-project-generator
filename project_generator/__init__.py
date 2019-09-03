# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import os
import web
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.common import custom_yaml
from project_generator.generator import run, run_all

__version__ = "0.1.dev0"
PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))
CONFIG_FILE_NAME = "project_generator_config.yaml"
DEFAULT_CONFIG = {
    "resources_path": "public",
    "tests_path": "unit_test",
    "libraries_path": "\'$common\'/libs",
    "archive_path": "public"
}


class ProjectGeneratorPage(INGIniousAdminPage):

    def GET_AUTH(self, course_id):
        course, _ = self.get_course_and_check_rights(course_id, allow_all_staff=True)
        data = get_configuration_file(course.get_fs().prefix)
        if data is not None:
            return self.display_page(course, libraries_path=data['libraries_path'], resources_path=data['resources_path'],
                                 tests_path=data['tests_path'], archive_path=data['archive_path'])
        else:
            return self.display_page(course)

    def POST_AUTH(self, course_id):
        course, _ = self.get_course_and_check_rights(course_id, allow_all_staff=True)
        input_data = web.input()
        task_id = None
        if input_data.get("action", "") == "generateAllProjects":
            new_data = {
                "resources_path": input_data["resources_path"],
                "tests_path": input_data["tests_path"],
                "libraries_path": input_data["libraries_path"],
                "archive_path": input_data["archive_path"]
            }
            if "task_to_generate" not in input_data:
                run_all(course.get_fs().prefix, course.get_id(), new_data["libraries_path"], new_data["resources_path"],
                        new_data["tests_path"], new_data["archive_path"], PATH_TO_PLUGIN)
            else:
                task_id = input_data["task_to_generate"]
                requirements = generator.check_requirements(course.get_fs().prefix, task_id,
                                                            new_data["resources_path"], new_data["tests_path"], new_data["libraries_path"], new_data["archive_path"])
                run(course.get_fs().prefix, task_id, course.get_id(), new_data["libraries_path"],
                    new_data["resources_path"], new_data["tests_path"], new_data["archive_path"], requirements, PATH_TO_PLUGIN)
            edit_configuration_file(course.get_fs().prefix, new_data)
            return self.display_page(course, task_id, new_data["libraries_path"], new_data["resources_path"],
                                     new_data["tests_path"], new_data["archive_path"], True)

        elif input_data.get("action", "") == "generateProjectTask":
            data = get_configuration_file(course.get_fs().prefix)
            if data is not None:
                return self.display_page(course, input_data.get("task", ""), libraries_path=data['libraries_path'],
                                         resources_path=data['resources_path'],
                                         tests_path=data['tests_path'], archive_path=data['archive_path'])
            else:
                return self.display_page(course, input_data.get("task", ""))

    def display_page(self, course, task=None, libraries_path=DEFAULT_CONFIG['libraries_path'], resources_path=DEFAULT_CONFIG['resources_path'],
                     tests_path=DEFAULT_CONFIG['tests_path'], archive_path=DEFAULT_CONFIG['archive_path'], generated=False):
        tpl = self.template_helper.get_custom_renderer(os.path.join(PATH_TO_PLUGIN, 'static')).project_generator
        return tpl(course, task, libraries_path, resources_path, tests_path, archive_path, generated)


def edit_configuration_file(path, data):
    config_file_path = os.path.join(path, CONFIG_FILE_NAME)
    if os.path.isfile(config_file_path):
        stream = open(config_file_path, 'w')
        custom_yaml.dump(data, stream)
        stream.close()
    else:
        get_configuration_file(path)


def get_configuration_file(path):
    config_file_path = os.path.join(path, CONFIG_FILE_NAME)
    if os.path.exists(config_file_path):
        stream = open(config_file_path, 'r')
        data = custom_yaml.load(stream)
        stream.close()
        return data
    else:
        stream = open(config_file_path, 'w')
        custom_yaml.dump(DEFAULT_CONFIG, stream)
        stream.close()
        return DEFAULT_CONFIG


def task_menu(course, task, template_helper):
    data = get_configuration_file(course.get_fs().prefix)
    can_display = generator.process_requirements(generator.check_requirements(course.get_fs().prefix, task.get_id(), data['resources_path'],
                                                                              data['tests_path'], data['libraries_path'], data['archive_path']))
    tpl = template_helper.get_custom_renderer(os.path.join(PATH_TO_PLUGIN, 'static'), False).task_menu
    return str(tpl(PATH_TO_PLUGIN, course, task, data['libraries_path'], data['resources_path'], data['tests_path'], data['archive_path'], False, can_display))


def course_admin_menu(course):
    return 'project_generator', '<i class="fa fa-file-archive-o fa-fw"></i>&nbsp; Project Generator'


def init(plugin_manager, _, _2, _3):
    plugin_manager.add_page('/admin/([^/]+)/project_generator', ProjectGeneratorPage)
    plugin_manager.add_hook('task_menu', task_menu)
    plugin_manager.add_hook('course_admin_menu', course_admin_menu)

