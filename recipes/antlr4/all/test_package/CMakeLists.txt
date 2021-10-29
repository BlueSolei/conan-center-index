# -*- mode:cmake -*-
cmake_minimum_required(VERSION 3.1)
project(antlr4-demo)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_EXTENSIONS OFF)

# find_package(Java)

if(NOT UNIX)
  message(WARNING "Unsupported operating system")
endif()

set(antlr4-demo-GENERATED_SRC
    ${PROJECT_SOURCE_DIR}/generated/TLexer.cpp
    ${PROJECT_SOURCE_DIR}/generated/TParser.cpp
    ${PROJECT_SOURCE_DIR}/generated/TParserBaseListener.cpp
    ${PROJECT_SOURCE_DIR}/generated/TParserBaseVisitor.cpp
    ${PROJECT_SOURCE_DIR}/generated/TParserListener.cpp
    ${PROJECT_SOURCE_DIR}/generated/TParserVisitor.cpp)

foreach(src_file ${antlr4-demo-GENERATED_SRC})
  set_source_files_properties(${src_file} PROPERTIES GENERATED TRUE)
endforeach(src_file ${antlr4-demo-GENERATED_SRC})

add_custom_target(GenerateParser DEPENDS ${antlr4-demo-GENERATED_SRC})
add_custom_command(
  OUTPUT ${antlr4-demo-GENERATED_SRC}
  COMMAND ${CMAKE_COMMAND} -E make_directory
          ${PROJECT_SOURCE_DIR}/generated/
  COMMAND
    "${Java_JAVA_EXECUTABLE}" -jar ${ANTLR_JAR_LOCATION} -Werror -Dlanguage=Cpp
    -listener -visitor -o ${PROJECT_SOURCE_DIR}/generated/ -package
    antlrcpptest ${PROJECT_SOURCE_DIR}/TLexer.g4
    ${PROJECT_SOURCE_DIR}/TParser.g4
  WORKING_DIRECTORY "${CMAKE_BINARY_DIR}"
  DEPENDS ${PROJECT_SOURCE_DIR}/TLexer.g4
          ${PROJECT_SOURCE_DIR}/TParser.g4
  COMMENT "antlr4 code generation (lexer + parser)")

include_directories(${PROJECT_SOURCE_DIR}/generated)

# file(GLOB antlr4-demo_SRC "${PROJECT_SOURCE_DIR}/generated/*")
set(antlr4-demo_SRC ${PROJECT_SOURCE_DIR}/main.cpp
                    ${antlr4-demo-GENERATED_SRC})

if(NOT CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
  set(flags_1 "-Wno-overloaded-virtual")
else()
  set(flags_1 "-MP /wd4251")
endif()

foreach(src_file ${antlr4-demo_SRC})
  set_source_files_properties(
    ${src_file} PROPERTIES COMPILE_FLAGS "${COMPILE_FLAGS} ${flags_1}")
endforeach(src_file ${antlr4-demo_SRC})

add_executable(antlr4-demo ${antlr4-demo_SRC})
# add_precompiled_header(antlr4-demo
# ${PROJECT_SOURCE_DIR}/runtime/src/antlrcpp-Prefix.h)

if(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
  target_compile_options(antlr4-demo PRIVATE "/MT$<$<CONFIG:Debug>:d>")
endif()

add_dependencies(antlr4-demo GenerateParser)

target_link_libraries(antlr4-demo ${CONAN_LIBS})

install(
  TARGETS antlr4-demo
  DESTINATION "share"
  COMPONENT dev)
