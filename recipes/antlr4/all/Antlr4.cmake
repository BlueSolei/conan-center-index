cmake_minimum_required(VERSION 3.19)

include(CMakePrintHelpers)

find_package(
  Java
  COMPONENTS Runtime
  REQUIRED)

# generate parser for taget
function(antlr4_generate_parser target)
  cmake_parse_arguments(PARSE_ARGV 1 ARG "" "NAME"
                        "GRAMMER_FILES;ANTLR_JAR_ARGS")

  if(NOT ARG_ANTLR_JAR_ARGS)
    set(ARG_ANTLR_JAR_ARGS -listener -visitor)
  endif()
  set(GENERATED_SOURCES_DIR ${CMAKE_CURRENT_BINARY_DIR})
  set(GRAMMER_TARGET "${target}-${NAME}")

  # ~~~
  # Make the generated files depend on the grammer files
  # PROBLEM: CMake is difficult in depending on generated files which are
  #   unknown in configure time. the antlr4 generated files (names and count) depend on the
  #   parameters & the files it is invoked with.
  # SOLUTION: generate once, so we know exactly which files are generated.
  #   then, we depend on these files with add_custom_target()
  # ~~~
  message(
    STATUS "Antlr4: generating parser for grammer '${ARG_NAME}' - first time")
  set(GENERATE_PARSER_CMD
      "${Java_JAVA_EXECUTABLE}"
      -jar
      ${CONAN_USER_ANTLR4_antlr_executable}
      -Xexact-output-dir
      -Werror
      -Dlanguage=Cpp
      ${ARG_ANTLR_JAR_ARGS}
      -o
      ${GENERATED_SOURCES_DIR}
      ${ARG_GRAMMER_FILES})

  # generate once to collect generated file names
  execute_process(
    COMMAND ${GENERATE_PARSER_CMD} WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                                                     COMMAND_ERROR_IS_FATAL ANY)
  file(GLOB GENERATED_SOURCES ${GENERATED_SOURCES_DIR}/*.cpp)
  message(
    STATUS
      "Antlr4: generating parser for grammer '${ARG_NAME}' - first time - done")

  # generate the parser (on build step) when grammer files changes
  add_custom_command(
    OUTPUT ${GENERATED_SOURCES}
    COMMAND ${GENERATE_PARSER_CMD}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    DEPENDS ${ARG_GRAMMER_FILES}
    COMMENT "Antlr4: generating parser for grammer '${ARG_NAME}'")
  add_custom_target(${GRAMMER_TARGET} DEPENDS ${ARG_GRAMMER_FILES})
  add_dependencies(${target} ${GRAMMER_TARGET})

  target_sources(${target} PRIVATE ${GENERATED_SOURCES})
  target_include_directories(${target} PRIVATE ${GENERATED_SOURCES_DIR})
  # Antlr4 requires C++11 or newer stansrad
  target_compile_features(${target} PUBLIC cxx_std_11)
  target_compile_definitions(${target} PUBLIC ANTLR4CPP_STATIC)
endfunction()
