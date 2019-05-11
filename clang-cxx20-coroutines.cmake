# Copyright (c) 2016-2018, Ruslan Baratov
# Copyright (c) 2017, David Hirvonen
# Copyright (c) 2019, Richard Hodges
# All rights reserved.

if(DEFINED POLLY_CLANG_CXX20_COROUTINES_CMAKE_)
  return()
else()
	set(POLLY_CLANG_CXX20_COROUTINES_CMAKE_ 1)
endif()

include("${CMAKE_CURRENT_LIST_DIR}/utilities/polly_init.cmake")

polly_init(
    "clang / c++20-coroutines support"
    "Unix Makefiles"
)

include("${CMAKE_CURRENT_LIST_DIR}/utilities/polly_common.cmake")

include("${CMAKE_CURRENT_LIST_DIR}/compiler/clang.cmake")
include("${CMAKE_CURRENT_LIST_DIR}/flags/cxx20.cmake")
include("${CMAKE_CURRENT_LIST_DIR}/flags/fcoroutines-ts.cmake")
include("${CMAKE_CURRENT_LIST_DIR}/library/std/libcxx.cmake")
