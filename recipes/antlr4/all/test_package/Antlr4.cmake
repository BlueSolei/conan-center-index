cmake_minimum_required(VERSION 3.19)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(
  Java
  COMPONENTS Runtime
  REQUIRED)

if(NOT UNIX)
  message(WARNING "Unsupported operating system")
endif()

function(antlr4_generate_parser target)
  cmake_parse_arguments(PARSE_ARGV 1 ARG "" "NAME"
                        "GRAMMER_FILES;ANTLR_JAR_ARGS")
  set(GENERATED_SOURCES_DIR ${CMAKE_CURRENT_BINARY_DIR})
  set(GENERATED_SOURCES_VAR "${target}-${NAME}_GENERATED_SRC")
  set(GRAMMER_TARGET "${target}-${NAME}")

  # Make the generated files depend on the grammer files
  set(build_input_files) # Will be list of files copied into build tree
  foreach(input_file ${ARG_GRAMMER_FILES})
    # Extract name of the file for generate path of the file in the build tree
    get_filename_component(input_file_name ${input_file} NAME)
    # Path to the file created by copy
    set(build_input_file ${GENERATED_SOURCES_DIR}/${input_file_name})
    # Copy file
    configure_file(${input_file} ${build_input_file} COPY_ONLY)
    # Add name of created file into the list
    list(APPEND build_input_files ${build_input_file})
  endforeach()

  # generate parser
  if(NOT ARG_ANTLR_JAR_ARGS)
    set(ARG_ANTLR_JAR_ARGS -listener -visitor)
  endif()

  message(STATUS "Antlr4: generating parser for grammer '${ARG_NAME}'")
  set(INVOKE_ANTLR_CMD
      "${Java_JAVA_EXECUTABLE}"
      -jar
      ${CONAN_USER_ANTLR4_antlr_jar}
      -Xexact-output-dir
      -Werror
      -Dlanguage=Cpp
      ${ARG_ANTLR_JAR_ARGS}
      -o
      ${GENERATED_SOURCES_DIR}
      ${build_input_files})

  execute_process(
    COMMAND ${INVOKE_ANTLR_CMD} WORKING_DIRECTORY "${CMAKE_BINARY_DIR}"
                                                  COMMAND_ERROR_IS_FATAL ANY)

  file(GLOB ${GENERATED_SOURCES_VAR} "${GENERATED_SOURCES_DIR}/*.cpp")
  target_sources(${target} PRIVATE ${${GENERATED_SOURCES_VAR}})

  add_custom_target(${GRAMMER_TARGET} DEPENDS ${${ARG_GRAMMER_FILES}})
  add_dependencies(${target} ${GRAMMER_TARGET})
  target_include_directories(${target} PRIVATE ${GENERATED_SOURCES_DIR})
endfunction()

# set(${GENERATED_SOURCES_VAR} ${GENERATED_SOURCES_DIR}/TLexer.cpp
# ${GENERATED_SOURCES_DIR}/TParser.cpp
# ${GENERATED_SOURCES_DIR}/TParserBaseListener.cpp
# ${GENERATED_SOURCES_DIR}/TParserBaseVisitor.cpp
# ${GENERATED_SOURCES_DIR}/TParserListener.cpp
# ${GENERATED_SOURCES_DIR}/TParserVisitor.cpp)

# foreach(src_file ${${GENERATED_SOURCES_VAR}})
# set_source_files_properties(${src_file} PROPERTIES GENERATED TRUE)
# endforeach(src_file ${${GENERATED_SOURCES_VAR}})

# add_custom_command( OUTPUT ${${GENERATED_SOURCES_VAR}} COMMAND
# ${CMAKE_COMMAND} -E make_directory ${GENERATED_SOURCES_DIR}/ COMMAND
# "${Java_JAVA_EXECUTABLE}" -jar ${ANTLR_JAR_LOCATION} -Werror -Dlanguage=Cpp
# -listener -visitor -o ${GENERATED_SOURCES_DIR}/ -package antlrcpptest
# ${PROJECT_SOURCE_DIR}/TLexer.g4 ${PROJECT_SOURCE_DIR}/TParser.g4
# WORKING_DIRECTORY "${CMAKE_BINARY_DIR}" DEPENDS
# ${PROJECT_SOURCE_DIR}/TLexer.g4 ${PROJECT_SOURCE_DIR}/TParser.g4 COMMENT
# "antlr4 code generation (lexer + parser)")

# if(NOT CMAKE_CXX_COMPILER_ID MATCHES "MSVC") set(flags_1
# "-Wno-overloaded-virtual") else() set(flags_1 "-MP /wd4251") endif()

# foreach(src_file ${antlr4-demo_SRC}) set_source_files_properties( ${src_file}
# PROPERTIES COMPILE_FLAGS "${COMPILE_FLAGS} ${flags_1}") endforeach(src_file
# ${antlr4-demo_SRC})
