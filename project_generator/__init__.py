# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import os
import web

__version__ = "0.1.dev0"
PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))


def task_menu(course, task, template_helper):
    try:
        with open(os.path.join(PATH_TO_PLUGIN, "static", "task_menu.html"), 'r') as file:
            return str(file.read())
    except:
        return ""


def course_admin_menu(course):
    return 'project_generator', '<i class="fa fa-gavel fa-fw"></i>&nbsp; Project Generator'


def init(plugin_manager, _, _2, _3):
    plugin_manager.add_hook('task_menu', task_menu)
    plugin_manager.add_hook('course_admin_menu', course_admin_menu)

