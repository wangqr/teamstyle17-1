#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import ai_proxy

def sendInstruction(string):
    '''
    临时替代逻辑组的sendInstruction
    '''
    pass

'''
以下的类声明仅供参考，最终的json化可能在python中实现，也可能直接在c中完成。
'''

class Action:
    def __init__(self, action_json, action_name = None):
        self.ai_id = ai_id
        if (action_name):
            self.action_name = action_name
        else:
            if (act["action"] in ["init", "move", "use_skill", "upgrade_skill"]):
                self.action_name = 'instruction'
            elif (act["action"] in ["query_map", "query_status"]):
                self.action_name = 'query'
        self.action_json = action_json
    def run(self, logic):
        if (self.action_name == 'instruction'):
            logic.setInstruction(self.action_json)
        elif (self.action_name == 'query'):
            ret = logic.getInstruction(self.action_json)
            # TODO send back data
            #ai_proxy.update_info(ret, self.ai_id)
    def set_timestamp(time: int):
        q = json.loads(self.action_json)
        q['time'] = time
        self.action_json = json.dumps(q)

class QueryMap(Action):
    def __init__(self, ai_id):
        Action.__init__(self, ai_id, action_name="query")
    def run(self):
        r = sendInstruction(json.dumps(self.__dict__))
        sendBackToAI(self.ai_id, b'{"mapinfo":' + r + b'}')

class Move(Action):
    def __init__(self, ai_id, x, y, z):
        Action.__init__(self, ai_id, action_name="move")
        self.x=x
        self.y=y
        self.z=z

class UseSkill(Action):
    def __init__(self, ai_id, skill_type, dir_x, dir_y, dir_z, target_obj_id):
        Action.__init__(self, ai_id, action_name="skill")
        self.type=skill_type
        self.x=dir_x
        self.y=dir_y
        self.z=dir_z
        self.target=target_obj_id

class UpdateSkill(Action):
    def __init__(self, ai_id, skill_type):
        Action.__init__(self, ai_id, action_name="skill")
        self.type=skill_type
        self.x=dir_x
        self.y=dir_y
        self.z=dir_z
        self.target=target_obj_id

class PauseAction(Action):
    def __init__(self, ai_id):
        Action.__init__(self, ai_id, action_name="_pause")
    def run(self):
        pass # should be handled by platform

class GameEndAction(Action): # generated when time up
    def __init__(self, forced = False):
        Action.__init__(self, ai_id = -1, action_name="_end")
        self.forced=forced
    def run(self):
        pass # should be handled by platform
