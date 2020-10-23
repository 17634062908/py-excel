# -*- coding: utf-8 -*-

from douyin.tasks.models import *

class dyusers:

    @classmethod
    def get_tag(cls, name, dept_id):
        if not name:
            return 0
        tag = DyTag.where('dept_id', '=', dept_id).where('name', '=', name).first()
        if tag is None:
            tag = DyTag.create(name=name, dept_id=dept_id)
            return tag.id
        return tag.id

    @classmethod
    def get_type(cls, id):
        map = {
            '关注的帐号': 1,
            '行业大V': 4,
            '本地大V': 5
        }

        if id in map.keys():
            return map.get(str(id))

        raise ValueError()
