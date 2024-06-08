cmake_minimum_required(VERSION 3.5...3.28.3)
project(test_package LANGUAGES CXX)

add_executable(${PROJECT_NAME})
target_sources(${PROJECT_NAME} PRIVATE test_package.cpp)
