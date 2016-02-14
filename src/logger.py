#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import queue
import time
import json

MaxRuntimeQueueSize = 100

class Logic:

	last_action_id = 0
	
	def __init__ (self, init_time):
		self.current_time = init_time

	# How to run?

class Run_Logger:

	def __init__ (self, init_action):
		run_time = time.localtime()
		self.filename = 'replay_'+str(run_time.tm_mon)+str(run_time.tm_mday)+\
						str(run_time.hour)+str(run_time.min)+str(run_time.sec)+'.replay'
		self.fp = open('filename', 'w', encoding='utf-8')
		self.fp.write('[')
		self.fp.write(init_action)
		self.logger_queue = queue.Queue(MaxRuntimeQueueSize)

	def __del__ (self):
		self.fp.write(']')
		self.fp.close()

	def log_action (self, cur_action):
		self.logger_queue.put(cur_action)
		if (self.logger_queue.full()):
			self.save_to_file()

	def save_to_file (self):
		while !(self.logger_queue.empty()):
			temp = self.logger_queue.get()
			self.fp.write(','+temp)


class Replay_Logger:

	logic_list = [Logic()]
	logic_count = 1
	current_logic = 0

	def __init__ (self, filename):
		self.fp = open('filename', 'r', decoding='utf-8')
		self.action_list = json.load(self.fp)
		self.action_count = len(self.action_list)

	def __del__ (self):
		self.fp.close()

	# Run current logic with instructions from UI_GROUP
	def run_logic (self):
		# TODO
		# check with UI_GROUP about the specification
		# 'last_action_id' should be constantly updated whenever an action is operated

	def new_logic (self, init_time):
		self.logic_list[self.logic_count] = Logic(init_time)		# The number of arguments of 'Logic.__init__()' requires further notice
		self.current_logic = logic_count
		self.logic_count += 1

		# action_list[0] is the initialization action
		# ??? Object of class 'Interface'?
		# ??? 'setInstruction' should include logic_id
		setInstruction(self.action_list[0])
		action_id = 1 			
		while (action_id < self.action_count) and (self.action_list[action_id]['time'] < init_time):
			# Object of class 'Interface'?
			setInstruction(self.action_list[action_id])
			action_id += 1
		self.logic_list[self.logic_count].last_action_id = action_id - 1
		run_logic()
		
	def time_travel (self, time_dest):
		logic_id = 0
		nearest_logic = -1
		found_available = False
		while (logic_id < self.logic_count):
			if (self.logic_list[logic_id].current_time < time_dest):
				if (found_available = False):
					found_available = True
					nearest_logic = logic_id
				if (self.logic_list[logic_id].current_time > self.logic_list[nearest_logic].current_time):
					nearest_logic = logic_id
			logic_id += 1
		if (found_available):
			self.current_logic = nearest_logic
			action_id = self.logic_list[self.current_logic].last_action_id + 1
			# Assume there exists an ending action
			while (self.action_list[action_id]['time'] < time_dest):
				self.logic_list[self.current_logic].last_action_id = action_id
				setInstruction(self.logic_list[action_id])
				action_id += 1
			run_logic()
		else:
			new_logic(time_dest)
			run_logic()
