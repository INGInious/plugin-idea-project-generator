# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import os
import web
from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
import project_generator.generator

__version__ = "0.1.dev0"
PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))


class ProjectGeneratorPage(INGIniousAdminPage):

    def GET_AUTH(self, course_id):
        course, _ = self.get_course_and_check_rights(course_id, allow_all_staff=True)
        return self.display_page(course)

    def POST_AUTH(self, course_id):
        course, _ = self.get_course_and_check_rights(course_id, allow_all_staff=True)
        input_data = web.input()


    def display_page(self, course, task=None, libraries_path='\'$common\'/libs', resources_path='public', test_path='unit_test', archive_path='public'):
        tpl = self.template_helper.get_custom_renderer(os.path.join(PATH_TO_PLUGIN, 'static')).project_generator
        return tpl(course, task, libraries_path, resources_path, test_path, archive_path)


def task_menu(course, task, template_helper):
    return str(template_helper.get_custom_renderer(os.path.join(PATH_TO_PLUGIN, 'static'), False).task_menu(PATH_TO_PLUGIN, course, task))


def course_admin_menu(course):
    return 'project_generator', '<i class="fa fa-file-archive-o fa-fw"></i>&nbsp; Project Generator'


def init(plugin_manager, _, _2, _3):
    plugin_manager.add_page('/admin/([^/]+)/project_generator', ProjectGeneratorPage)
    plugin_manager.add_hook('task_menu', task_menu)
    plugin_manager.add_hook('course_admin_menu', course_admin_menu)

