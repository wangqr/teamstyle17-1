cmake_minimum_required(VERSION 3.3.2)
set(CMAKE_CXX_STANDARD 11)
PROJECT(ts17_ai)
ADD_LIBRARY(ai SHARED ${PROJECT_SOURCE_DIR}/ai/ai.cpp ;${PROJECT_SOURCE_DIR}/ai/teamstyle17.h;${PROJECT_SOURCE_DIR}/ai/teamstyle17.cpp ;${PROJECT_SOURCE_DIR}/communicate/basic.h;${PROJECT_SOURCE_DIR}/communicate/communicate.cpp ;${PROJECT_SOURCE_DIR}/communicate/communicate.h ;${PROJECT_SOURCE_DIR}/communicate/dll_main.cpp)
