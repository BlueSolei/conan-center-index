# -*- mode:cmake -*-
cmake_minimum_required(VERSION 3.1)
project(antlr4-demo)

include(Antlr4.cmake)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(antlr4-demo)
install(TARGETS antlr4-demo)
target_sources(antlr4-demo PRIVATE ./main.cpp)
target_link_libraries(antlr4-demo ${CONAN_LIBS})

antlr4_generate_parser(
  antlr4-demo
  NAME
  "T-GRAMMER"
  GRAMMER_FILES
  ./TLexer.g4
  ./TParser.g4
  ANTLR_JAR_ARGS
  -listener
  -visitor
  -package
  antlrcpptest)
